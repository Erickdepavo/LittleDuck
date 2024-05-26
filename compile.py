import argparse

from little_duck import LittleDuckCompiler


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Little Duck code compiler")
    
    # Add arguments
    parser.add_argument("input_file", type=str, help="Input source file to compile")
    parser.add_argument("-o","--output_dir", type=str, default=".", help="Directory to place output files")
    parser.add_argument("-w", "--no_warnings", action="store_true", help="Hide warnings during compilation")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")

    # Parse the arguments
    args = parser.parse_args()

    # Use the arguments
    if args.debug or args.verbose:
        print("input_file:", args.input_file)
        print("output_dir:", args.output_dir)
        print("no_warnings:", args.no_warnings)
        print("debug:", args.debug)
        print("verbose:", args.verbose)

    # Run the compiler
    compiler = LittleDuckCompiler(debug=args.verbose)
    compiler.compile(args.input_file)

if __name__ == "__main__":
    main()
