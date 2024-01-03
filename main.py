import sys

from src.legacy_parser.legacy_format_parser import LegacyParser
from src.flush import save_dataframe
from src.chair_matcher.chair_matcher import ChairMatcher
from argparse import ArgumentParser


def main(args):
    try:
        with open(args.input) as file:
            data = file.readlines()
            parser = LegacyParser(data)
            rooms = list(parser.parse_rooms())
            chairs = list(parser.parse_chairs())
    except FileNotFoundError:
        sys.exit(f'File {args.input} not found')

    matcher = ChairMatcher(rooms, chairs)
    matcher.print_report()

    if args.output is not None:
        save_dataframe(rooms, chairs, args.output)


def parse_args():
    arg_parser = ArgumentParser(description="CL tool to parse plans and outputs furniture quantity")
    arg_parser.add_argument("-i", "--input", type=str, help="Input file, 'input.txt' is default", default='input.txt', required=False)
    arg_parser.add_argument("-o", "--output", type=str, help="Output file, no output to file is default scenario", required=False)
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main(parse_args())

