import argparse, os, sys

from pset_checker import check_problem_file
from pset_formatter import format_problem_file
from ra2html import format_relational_algebra


def main():
    parser = argparse.ArgumentParser(
        description="Converts a relational algebra markup file into an HTML " \
                    "file using the relational algebra notation.")

    parser.add_argument("input",
        help="Path and filename of input relational algebra file to " \
             "convert to HTML")

    parser.add_argument("-o", "--output",
        help="Specify the path and filename of where to store the output " \
             "HTML file.  If unspecified, the output file will be stored " \
             "in the same location as the input file, but with a .html " \
             "extension.")

    parser.add_argument("-n", "--dry_run", action="store_true",
        help="Causes the converter to perform a \"dry run\" of the file " \
             "conversion, without storing the output file.")

    args = parser.parse_args()

    if args.dry_run:
        print("Performing a dry-run through the input file.")

    infile = args.input
    if not os.path.isfile(infile):
        print("ERROR:  %s is not a file" % infile)
        sys.exit(1)

    print("Reading from input file:  %s" % infile)

    if args.output is not None:
        outfile = args.output
    else:
        parts = os.path.splitext(infile)
        outfile = parts[0] + '.html'

    if args.dry_run:
        print("Dry run:  Would write to output file %s" % outfile)

        check_problem_file(infile, sys.stdout)
    else:
        print("Writing to output file:  %s" % outfile)

        with open(outfile, 'w') as f:
            format_problem_file(infile, format_relational_algebra, f)


if __name__ == "__main__":
    main()

