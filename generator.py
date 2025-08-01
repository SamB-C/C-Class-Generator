import sys
from ClassDescriptors import ClassDescription


def main():
    # Input emmet description of C++ class
    desc = sys.argv[1]
    # Create ClassDescription object
    class_desc = ClassDescription(desc)
    class_desc.create_hpp_file()
    class_desc.create_cpp_file()


if __name__ == "__main__":
    main()
