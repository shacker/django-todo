import csv
import sys
from pathlib import Path

from django.contrib.auth import get_user_model
from icecream import ic

from todo.models import Task, TaskList


class CSVImporter:
    """Core upsert functionality for CSV import, for re-use by `import_csv` management command, web UI and tests."""

    def __init__(self):
        pass

    def upsert(filepath):

        if not Path(filepath).exists():
            print(f"Sorry, couldn't find file: {filepath}")
            sys.exit(1)

        # Have arg and good file path, read rows
        with open(filepath, mode="r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                # Title, Group, Task List, Created Date, Due Date, Completed, Created By, Assigned To, Note, Priority
                newrow = row  # Copy so we can modify  properties
                newrow["Completed"] = True if row.get("Completed") == "Yes" else False
                ic(newrow)

                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                print(
                    f"Row {line_count}: Title: {newrow['Title']}, Group: {newrow['Group']}, Completed: {newrow['Completed']}"
                )
                line_count += 1
