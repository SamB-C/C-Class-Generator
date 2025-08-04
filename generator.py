import sys
from CPPClassCreator import CPPClassCreator


def manage_arguments() -> tuple[str, str, dict[str, bool]]:
    """Manage command line arguments for the C++ class generator. Gets the emmet description, location, and options.
    Options include: forced override. Returns: description, location, and a dictionary of options as a tuple."""
    # Default options
    options = {
        "override": False,
        "append": False
    }
    # Get emmet
    desc = sys.argv[1] if len(sys.argv) > 1 else None
    if desc is None:
        print("No emmet provided.")
        exit(1)
    # Get location if exists
    location = "."
    if len(sys.argv) < 3:
        return desc, location, options
    options_index_start = 2
    if sys.argv[2][0] != '-':
        location = sys.argv[2]
        options_index_start = 3
    # Get options
    for arg in sys.argv[options_index_start:]:
        if arg.startswith('-'):
            if arg == "-override" or arg == "-o":
                options["override"] = True
            if arg == "-append" or arg == "-a":
                options["append"] = True
        else:
            print(f"Unknown argument: {arg}")

    # Check for invalid option combinations
    if options["append"] and options["override"]:
        print("Cannot use -append and -override at the same time.")
        exit(1)

    return desc, location, options


def main():
    # Input emmet description of C++ class
    desc, location, options = manage_arguments()
    # Create ClassDescription object
    creator = CPPClassCreator(desc)
    creator.create_hpp_file(location, options)
    creator.create_cpp_file(location, options)


if __name__ == "__main__":
    main()
