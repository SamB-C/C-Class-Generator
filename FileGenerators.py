from ClassDescriptors import ClassDescription
from ClassGenerators import create_include_guards, create_inclusions, create_class_declaration, create_attributes, create_method_declarations


def create_hpp_file(classDesc: ClassDescription) -> None:
    """Generates a header file (.hpp) and its contents for the given class description."""
    with open(f"{classDesc.name}.hpp", "w") as file:
        include_guards = create_include_guards(classDesc)
        inclusions, namespaces = create_inclusions(classDesc)
        class_declaration = create_class_declaration(classDesc)
        attributes = create_attributes(classDesc)
        method_declarations = create_method_declarations(classDesc)

        # Write first two parts of include guards
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
        file.write(include_guards[2])
