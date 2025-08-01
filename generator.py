import sys
from ClassDescriptors import ClassDescription
from FileGenerators import create_hpp_file


def main():
    # Input emmet description of C++ class
    desc = sys.argv[1]
    # Create ClassDescription object
    class_desc = ClassDescription(desc)
    # Generate hpp file
    create_hpp_file(class_desc)


if __name__ == "__main__":
    main()
