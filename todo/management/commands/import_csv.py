import csv
import unicodecsv
import sys
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from todo.models import Task, TaskList


class Command(BaseCommand):
    help = """Import specifically formatted CSV file of incoming tasks.
    For specfic format of inbound CSV, see data/import example.csv.
    For documentation on field formats and required fields, see README.md.
    """

    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            "-f", "--file", dest="file", default=None, help="File to to inbound CSV file."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # ### Sanity checks ###

        # Need a file to proceed
        if not options.get("file"):
            print("Sorry, we need a file name to work from.")
            sys.exit(1)
        else:
            print(options.get("file"))
            if not Path(options.get("file")).exists():
                print(f"Sorry, couldn't find file name specified: {options.get('file')}")
                sys.exit(1)

        print("Have arg and good file path")
        with open(Path(options.get("file")), 'rb') as csvfile:
            # csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            # csvreader = csv.DictReader(csvfile)
            csvreader = unicodecsv.reader(csvfile, encoding='utf-8-sig')
            for row in csvreader:
                # print(', '.join(row))
                # print(row['Title'], row['Group'])
                print(row)