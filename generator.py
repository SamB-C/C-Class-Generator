import sys
from ClassDescriptors import ClassDescription
from FileGenerators import create_hpp_file, create_cpp_file


def main():
    # Input emmet description of C++ class
    desc = sys.argv[1]
    # Create ClassDescription object
    class_desc = ClassDescription(desc)
    create_hpp_file(class_desc)
    create_cpp_file(class_desc)


if __name__ == "__main__":
    main()
