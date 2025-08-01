from ClassDescriptors import ClassDescription
from ClassGenerators import create_include_guards, create_inclusions, create_class_declaration, create_attributes, create_method_declarations, create_cpp_header, define_cpp_methods


def create_hpp_file(classDesc: ClassDescription) -> None:
    """Generates a header file (.hpp) and its contents for the given class description."""
    with open(f"{classDesc.name}.hpp", "w") as file:
        include_guards = create_include_guards(classDesc)
        inclusions, namespaces = create_inclusions(classDesc)
        class_declaration = create_class_declaration(classDesc)
        attributes = create_attributes(classDesc)
        method_declarations = create_method_declarations(classDesc)

        # Write first two parts of include guards
        if (classDesc.template):
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
        if (classDesc.template):
            file.write(include_guards[2])
    print(f"Header file generated successfully at ./{classDesc.name}.hpp")


def create_cpp_file(classDesc: ClassDescription) -> None:
    """Creates a cpp file (.cpp) for the given class description."""
    if classDesc.template:
        # Exit as no cpp file needed
        return
    with open(f"{classDesc.name}.cpp", "w") as file:
        header = create_cpp_header(classDesc)
        inclusions, namespaces = create_inclusions(classDesc)
        methods = define_cpp_methods(classDesc)

        # Write header inclusion
        file.write(header + "\n\n")

        # Write namespaces used
        for namespace in namespaces:
            file.write(f"{namespace}\n")

        file.write("\n")

        # Write method definitions
        for method in methods:
            file.write(method + "\n\n")
    print(f"Source file generated successfully at ./{classDesc.name}.cpp")
