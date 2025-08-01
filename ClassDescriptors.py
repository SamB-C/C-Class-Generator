from dataclasses import dataclass, field
from enum import Enum
import re
from itertools import count


class Inheritance(Enum):
    """Enum to represent inheritance types in C++ classes."""
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"


@dataclass(repr=True)
class Attribute:
    """Class to represent a private attribute in a C++ class."""
    type: str
    setter: bool
    getter: bool
    index: int = field(default_factory=lambda counter=count()
                       : next(counter), init=False)


@dataclass(repr=True)
class ParentClass:
    """Class to represent a parent class being inherited in a C++ class."""
    name: str
    virtual: bool
    inheritance: Inheritance
    position: int


class CPPClassCreator:
    """Class to parse and represent the inheritance and attributes of a C++ class from an emmet description."""

    def __init__(self, desc: str) -> None:
        # Initialize class attributes
        self.name = ""
        self.template = False
        self.specialisation = None
        self.parents = []
        self.attributes = []
        # Parse emmet description into components
        split_description = desc.split(":")
        declaration = split_description[0]
        attribute_sets = split_description[1:]
        # Get the name of the class
        self.set_class_name(declaration)
        self.get_template(declaration)
        self.set_parent_classes(declaration)
        self.set_attributes(attribute_sets)

    def set_class_name(self, declaration: str) -> None:
        """Extract the class name from the declaration string."""
        # Extract class name from declaration
        self.name = re.match(r"[a-zA-Z0-9_]+", declaration).group()

    def get_template(self, declaration: str) -> None:
        """Checks if the class is a template class and extracts the template specialisation if it exists."""
        # Check if the class is a template class
        if "<" in declaration and ">" in declaration:
            self.template = True
            # Extract the template specialisation
            start_index = declaration.index("<") + 1
            end_index = declaration.index(">")
            # Check whether is a template class or template specialisation
            if start_index == end_index:
                self.specialisation = None
            else:
                self.specialisation = declaration[start_index:end_index].strip(
                )
        else:
            self.template = False
            self.specialisation = None

    def set_parent_classes(self, declaration: str) -> None:
        """Extracts parent classes from the class declaration string, including their inheritance type and whether they are virtual."""
        # Get the index of every +, =, or - in the declaration
        parent_start_indicies = [m.start()
                                 for m in re.finditer(r"[+=-]", declaration)]
        # Create ParentClass objects for each parent class
        for i, parent_index in enumerate(parent_start_indicies):
            inheritance = None
            name = ""
            virtual = False

            # Determine the type of inheritance
            if declaration[parent_index] == "+":
                inheritance = Inheritance.PUBLIC
            elif declaration[parent_index] == "-":
                inheritance = Inheritance.PRIVATE
            elif declaration[parent_index] == "=":
                inheritance = Inheritance.PROTECTED
            else:
                raise ValueError("Invalid inheritance type")
            # Get name of parent class and if it is virtual
            name_section = ""
            if (i + 1) < len(parent_start_indicies):
                name_section = declaration[parent_index +
                                           1:parent_start_indicies[i + 1]]
            else:
                name_section = declaration[parent_index + 1:]

            name = name_section.replace("?", "")
            if "?" in name_section:
                virtual = True

            self.parents.append(ParentClass(name, virtual, inheritance, i))

    def set_attributes(self, attribute_sets: list[str]) -> None:
        """Extracts attributes from the attribute sets provided in the class description."""
        # Parse attribute sets to create Attribute objects
        for attribute_set in attribute_sets:
            # Determine whether attributes will have getters and/or setters
            getter = False
            setter = False
            if attribute_set[0].isnumeric():
                # Fix regex match for attribute sets starting with a number
                attribute_set = " " + attribute_set
            else:
                if attribute_set[1].isnumeric():
                    if attribute_set[0] == "g":
                        getter = True
                    elif attribute_set[0] == "s":
                        setter = True
                elif attribute_set[2].isnumeric():
                    getter = True
                    setter = True

            # Split into attributes by finding the start indicies
            attribute_start_indicies = [m.start() + 1
                                        for m in re.finditer(r"(?:^|[^0-9])(\d)", attribute_set)]
            # Create Attribute objects for each attribute type
            for i, start_index in enumerate(attribute_start_indicies):
                # Consider case when number is more than one digit
                type_start_index = start_index + 1
                number_length = 1
                while attribute_set[type_start_index].isdigit():
                    type_start_index += 1
                    number_length += 1

                # Get the type of the attribute
                attribute_type = ""
                if i + 1 < len(attribute_start_indicies):
                    attribute_type = attribute_set[type_start_index:
                                                   attribute_start_indicies[i + 1]]
                else:
                    attribute_type = attribute_set[type_start_index:]

                # Create that many Attribute objects for that type
                for j in range(int(attribute_set[start_index:start_index + number_length])):
                    self.attributes.append(
                        Attribute(attribute_type, setter, getter))

    def __repr__(self) -> str:
        return f"ClassDescription(name={self.name}, parents={self.parents}, attributes={self.attributes}, numParents={len(self.parents)}, numAttributes={len(self.attributes)}, template={self.template}, specialisation={self.specialisation})"

    def create_include_guards(self) -> list[str]:
        """Generates include guards for the class based on whether it is a template class or not. (`#ifndef`, `#define`, `#endif`)"""
        if self.template:
            return [f"#ifndef {self.name.upper()}_HPP", f"#define {self.name.upper()}_HPP", "#endif"]
        else:
            return []

    def create_inclusions(self) -> list[str]:
        """Generates namespace inclusions, and include statements if the types string or vector are used for attributes.
        Includes in format `#include <file>` and namespaces in format `using std::type;`.'"""
        namespaces_used = []
        includes = []
        type_include_association = {
            "string": "#include <string>",
            "std::string": "#include <string>",
            "vector": "#include <vector>",
            "std::vector": "#include <vector>",
        }
        for attribute in self.attributes:
            attribute: Attribute
            # Check if attribute needs to be included
            if attribute.type in type_include_association.keys():
                # Use std:: namespace for these types
                if f"using std::{attribute.type};" not in namespaces_used:
                    namespaces_used.append(f"using std::{attribute.type};")
                # Include these types if not already included
                if type_include_association[attribute.type] not in includes:
                    includes.append(type_include_association[attribute.type])
        return includes, namespaces_used

    def create_class_declaration(self) -> tuple[str, str]:
        """Generates Declaration for the class, including template specialisation if it exists. Template line in format
        `template <>` or `template <typename T>` ("" if class is not template) and declaration line in format `class ClassName : public ParentClass, protected ParentClass {`."""
        template_line = ""
        declaration_line = ""
        # Generate template line
        if self.template:
            if self.specialisation:
                template_line = f"template <>"
            else:
                template_line = f"template <typename T>"
        # Generate declaration line
        declaration_line += f"class {self.name}"
        # Add template specialisation if it exists
        if self.specialisation:
            declaration_line += f"<{self.specialisation}>"
        # Add inheritance if exists - in order
        if self.parents:
            # Add colon to indicate inheritance
            declaration_line += " : "
            # Iterate through parents to create inheritance declaration
            for i, parent in enumerate(self.parents):
                parent: ParentClass
                # Ensure parent classes are in order
                if parent.position != i:
                    raise IndexError(
                        f"Parent class {parent.name} is not in the correct position in the inheritance list.")
                # Add virtural keyword, inheritance type, and name or parent
                if i > 0:
                    declaration_line += ", "
                if parent.virtual:
                    declaration_line += "virtual "
                declaration_line += f"{parent.inheritance.value} {parent.name}"
        # Add opening brace to declaration line
        declaration_line += "\n{"
        return template_line, declaration_line

    def get_attribute_name(self, attribute: Attribute) -> str:
        """Returns the name of an attribute based on its dataclass: `get_set_attrX` where X is the index of the attribute, and get and set
        are included if the attribute has a getter or setter respectively."""
        name = ""
        if attribute.getter:
            name += "_g"
        if attribute.setter:
            name += "_s"
        name = "attr" + str(attribute.index) + name
        return name

    def create_attributes(self) -> list[str]:
        """Generates attribute declarations for the class, in the format `\\t{type} {attr_name};` where `type` is the type of the attribute
        and `attr_name` is the name of the attribute generated by `get_attribute_name`."""
        attributes: list[str] = []
        for attribute in self.attributes:
            attribute: Attribute
            # Create attribute
            attributes.append(
                f"\t{attribute.type} {self.get_attribute_name(attribute)};")
        return attributes

    def get_method_definitions(self) -> dict[str, list[str]]:
        """Generates method definitions for getter and setter methods, excluding the declaration, including both braces. Returns in the form of a list.
        Index 0: `{`. Index 1: `\\treturn {attr_name};` or `\\t{attr_name} = new{attr_name};`. Index 2: `}`."""
        methods = {}
        # Create definition for getters and setters
        for attribute in self.attributes:
            attribute: Attribute
            # Create getter method definition
            attr_name = self.get_attribute_name(attribute)
            if attribute.getter:
                methods[f"get_{attr_name}"] = [
                    "{", f"\treturn {attr_name};", "}"]
            if attribute.setter:
                methods[f"set_{attr_name}"] = [
                    "{", f"\t{attr_name} = new{attr_name};", "}"]
        return methods

    def create_method_declarations(self) -> list[str]:
        """Generates getter and setter declarations for the class. If class is template
        class, the methods will be defined and declared here. Declarations are preceded by a `\\t`."""
        method_declarations = []
        method_definitions = {}
        # If class is template class, get definitions as they must be defined along with declarations
        if self.template:
            method_definitions = self.get_method_definitions()
        for attribute in self.attributes:
            attribute: Attribute
            attr_name = self.get_attribute_name(attribute)
            # Create getter and setter declarations
            for method in ["get", "set"]:
                declaration = ""
                if method == "get" and attribute.getter:
                    declaration += f"\t{attribute.type} get_{attr_name}() const"
                elif method == "set" and attribute.setter:
                    declaration += f"\tvoid set_{attr_name}(const {attribute.type} &new{attr_name})"
                # If template, add method definition
                method_exists = (method == "get" and attribute.getter) or (
                    method == "set" and attribute.setter)
                if self.template and method_exists:
                    definition = method_definitions.get(
                        f"{method}_{attr_name}", None)
                    if definition == None:
                        raise ValueError(
                            f"Method definition for {method}_{attr_name} not found.")
                    else:
                        declaration += "\n\t" + "\n\t".join(definition)

                # Add declaration to list of method declarations
                if method_exists:
                    declaration += ";"
                    method_declarations.append(declaration)

        return method_declarations

    def create_cpp_header(self) -> str:
        return f"#include \"{self.name}.hpp\""

    def define_cpp_methods(self) -> list[str]:
        """Generates method definitions for associated declarations in the header file."""
        definitions = []
        method_definitions = self.get_method_definitions()
        for attribute in self.attributes:
            attribute: Attribute
            attr_name = self.get_attribute_name(attribute)
            # Create getter and setter declarations
            for method in ["get", "set"]:
                definition = ""
                if method == "get" and attribute.getter:
                    definition += f"{attribute.type} {self.name}::get_{attr_name}() const"
                elif method == "set" and attribute.setter:
                    definition += f"void {self.name}::set_{attr_name}(const {attribute.type} &new{attr_name})"
                # If template, add method definition
                method_exists = (method == "get" and attribute.getter) or (
                    method == "set" and attribute.setter)
                if method_exists:
                    method_definition = method_definitions.get(
                        f"{method}_{attr_name}", None)
                    if method_definition == None:
                        raise ValueError(
                            f"Method definition for {method}_{attr_name} not found.")
                    else:
                        definition += "\n" + "\n".join(method_definition)
                        definition += ";"
                        definitions.append(definition)

        return definitions

    def create_hpp_file(self) -> None:
        """Generates a header file (.hpp) and its contents for the given class description."""
        with open(f"{self.name}.hpp", "w") as file:
            include_guards = self.create_include_guards()
            inclusions, namespaces = self.create_inclusions()
            class_declaration = self.create_class_declaration()
            attributes = self.create_attributes()
            method_declarations = self.create_method_declarations()

            # Write first two parts of include guards
            if (self.template):
                file.write(include_guards[0] + "\n")
                file.write(include_guards[1] + "\n\n")

            # Write inclusions
            for inclusion in inclusions:
                file.write(inclusion + "\n")

            # Write namespaces used
            for namespace in namespaces:
                file.write(f"{namespace}\n")

            file.write("\n")

            # Write class
            if class_declaration[0] != "":
                file.write(class_declaration[0] + "\n")
            file.write(class_declaration[1] + "\n")

            # Write attributes
            file.write("private:\n")
            for attribute in attributes:
                file.write(attribute + "\n")

            # Write methods
            file.write("\npublic:\n")
            for method in method_declarations:
                file.write(method + "\n")

            # Close class declaration
            file.write("};\n\n")

            # Write last part of include guards
            if (self.template):
                file.write(include_guards[2])
        print(f"Header file generated successfully at ./{self.name}.hpp")

    def create_cpp_file(self) -> None:
        """Creates a cpp file (.cpp) for the given class description."""
        if self.template:
            # Exit as no cpp file needed
            return
        with open(f"{self.name}.cpp", "w") as file:
            header = self.create_cpp_header()
            inclusions, namespaces = self.create_inclusions()
            methods = self.define_cpp_methods()

            # Write header inclusion
            file.write(header + "\n\n")

            # Write namespaces used
            for namespace in namespaces:
                file.write(f"{namespace}\n")

            file.write("\n")

            # Write method definitions
            for method in methods:
                file.write(method + "\n\n")
        print(f"Source file generated successfully at ./{self.name}.cpp")
