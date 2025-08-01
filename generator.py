import sys
from CPPClassCreator import CPPClassCreator


def main():
    # Input emmet description of C++ class
    desc = sys.argv[1]
    # Create ClassDescription object
    creator = CPPClassCreator(desc)
    creator.create_hpp_file()
    creator.create_cpp_file()


if __name__ == "__main__":
    main()
