import csv
import logging
import sys
from pathlib import Path
import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from icecream import ic

from todo.models import Task, TaskList

log = logging.getLogger(__name__)


class CSVImporter:
    """Core upsert functionality for CSV import, for re-use by `import_csv` management command, web UI and tests.
    For each row processed, first we try and get the correct related objects or set default values, then decide
    on our upsert logic - create or update? We must enforce internal rules during object creation and take a SAFE
    approache - for example
    we shouldn't add a task if it specifies that a user is not a specified group. For that reason, it also doesn't
    make sense to create new groups from here. In other words, the ingested CSV must accurately represent the current
    database. Non-conforming rows are skipped and logged. Unlike manual task creation, we won't assume that the person
    running this ingestion is the task creator - the creator must be specified, and a blank cell is an error. We also
    do not create new lists - they must already exist (because if we did create new lists we'd also have to add the user to it,
    etc.)

    Supplies a detailed log of what was and was not imported at the end."""

    def __init__(self):
        self.errors = []
        self.line_count = 0

    def upsert(self, filepath):

        if not Path(filepath).exists():
            print(f"Sorry, couldn't find file: {filepath}")
            sys.exit(1)

        with open(filepath, mode="r") as csv_file:
            # Have arg and good file path -- read rows
            # Inbound columns:
            # Title, Group, Task List, Created Date, Due Date, Completed, Created By, Assigned To, Note, Priority

            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.line_count += 1

                newrow = self.validate_row(row)  # Copy so we can modify  properties
                if newrow:
                    ic(newrow)
                    print("\n")

            # Report. Stored errors has the form:
            # self.errors = [{3: ["Incorrect foo", "Non-existent bar"]}, {7: [...]}]
            for error_dict in self.errors:
                for k, error_list in error_dict.items():
                    print(f"Skipped row {k}:")
                    for msg in error_list:
                        print(f"\t{msg}")

            print(f"\nProcessed {self.line_count} rows")
            print(f"Inserted xxx rows")

    def validate_row(self, row):
        """Perform data integrity checks and set default values. Returns a valid object for insertion, or False.
        Errors are stored for later display."""

        row_errors = []

        # Task creator must exist
        if not row.get("Created By"):
            msg = f"Missing required task creator."
            row_errors.append(msg)

        created_by = get_user_model().objects.filter(username=row.get("Created By"))
        if created_by.exists():
            creator = created_by.first()
        else:
            creator = None
            msg = f"Invalid task creator {row.get('Created By')}"
            row_errors.append(msg)

        # If specified, Assignee must exist
        if row.get("Assigned To"):
            assigned = get_user_model().objects.filter(username=row.get("Assigned To"))
            if assigned.exists():
                assignee = assigned.first()
            else:
                msg = f"Missing or invalid task assignee {row.get('Assigned To')}"
                row_errors.append(msg)
        else:
            assignee = None  # Perfectly valid

        # Group must exist
        try:
            target_group = Group.objects.get(name=row.get("Group"))
        except Group.DoesNotExist:
            msg = f"Could not find group {row.get('Group')}."
            row_errors.append(msg)

        # Task creator must be in the target group
        if creator and target_group not in creator.groups.all():
            msg = f"{creator} is not in group {target_group}"
            row_errors.append(msg)

        # Assignee must be in the target group
        if assignee and target_group not in assignee.groups.all():
            msg = f"{assignee} is not in group {target_group}"
            row_errors.append(msg)

        # Group membership checks have passed
        row["Created By"] = creator
        row["Group"] = target_group
        if assignee:
            row["Assigned To"] = assignee

        # Task list must exist in the target group
        try:
            tasklist = TaskList.objects.get(name=row.get("Task List"), group=target_group)
            row["Task List"] = tasklist
        except TaskList.DoesNotExist:
            msg = (
                f"Task list {row.get('Task List')} in group {target_group} does not exist"
            )
            row_errors.append(msg)

        # Validate Due Date
        dd = row.get("Due Date")
        if dd:
            try:
                row["Due Date"] = datetime.datetime.strptime(dd, '%Y-%m-%d')
            except ValueError:
                msg = f"Could not convert Due Date {dd} to python date"
                row_errors.append(msg)

        # Validate Created Date
        cd = row.get("Created Date")
        if cd:
            try:
                row["Created Date"] = datetime.datetime.strptime(cd, '%Y-%m-%d')
            except ValueError:
                msg = f"Could not convert Created Date {cd} to python date"
                row_errors.append(msg)

        # Set Completed default
        row["Completed"] = True if row.get("Completed") == "Yes" else False

        if row_errors:
            self.errors.append({self.line_count: row_errors})
            return False

        # No errors:
        return row
