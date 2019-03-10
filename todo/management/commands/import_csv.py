import sys
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from todo.operations.csv_importer import CSVImporter


class Command(BaseCommand):
    help = """Import specifically formatted CSV file containing incoming tasks to be loaded.
    For specfic format of inbound CSV, see data/import_example.csv.
    For documentation on field formats and required fields, see README.md.
    """

    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            "-f", "--file", dest="file", default=None, help="File to to inbound CSV file."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Need a file to proceed
        if not options.get("file"):
            print("Sorry, we need a file name to work from.")
            sys.exit(1)
        else:
            # Don't check validity of filepath here; upserter will do that.
            filepath = str(options.get("file"))

        importer = CSVImporter()
        results = importer.upsert(filepath)

        # Report successes, failures and summaries
        print()
        for upsert_msg in results.get("upserts"):
            print(upsert_msg)

        # Stored errors has the form:
        # self.errors = [{3: ["Incorrect foo", "Non-existent bar"]}, {7: [...]}]
        for error_dict in results.get("errors"):
            for k, error_list in error_dict.items():
                print(f"\nSkipped CSV row {k}:")
                for msg in error_list:
                    print(f"- {msg}")

        print()
        for summary_msg in results.get("summaries"):
            print(summary_msg)
