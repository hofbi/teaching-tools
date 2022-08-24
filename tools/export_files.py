"""Export files for students."""

import sys
from argparse import Namespace

from sel_tools.file_export.copy_item import copy_item
from sel_tools.file_export.export_item import visit_exported_item
from sel_tools.utils import args


def parse_arguments(arguments: list[str]) -> Namespace:
    """Parse CLI arguments."""
    factory = args.ArgumentParserFactory.default_parser(__doc__)
    factory.parser.add_argument(
        "source_path",
        type=args.dir_path,
        help="Path to the source files",
    )
    factory.add_output_path()
    factory.add_keep_solutions()

    return factory.parser.parse_args(arguments[1:])


def main() -> None:
    """main."""
    arguments = parse_arguments(sys.argv)

    copy_item(arguments.source_path, arguments.output_dir)
    visit_exported_item(arguments.output_dir, arguments.keep_solutions)


if __name__ == "__main__":
    main()
