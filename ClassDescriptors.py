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
    index: int = field(default_factory=lambda counter=count(): next(counter), init=False)


@dataclass(repr=True)
class ParentClass:
    """Class to represent a parent class being inherited in a C++ class."""
    name: str
    virtual: bool
    inheritance: Inheritance
    position: int


class ClassDescription:
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
        i = 1
        while declaration[:i].isalnum():
            i += 1
        self.name = declaration[:i-1]

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
