import csv
import datetime
import logging
import sys
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from todo.models import Task, TaskList

log = logging.getLogger(__name__)


class CSVImporter:
    """Core upsert functionality for CSV import, for re-use by `import_csv` management command, web UI and tests.
    Supplies a detailed log of what was and was not imported at the end. See README for usage notes.
    """

    def __init__(self):
        self.error_msgs = []
        self.upsert_msgs = []
        self.summary_msgs = []
        self.line_count = 0
        self.upsert_count = 0

    def upsert(self, filepath):

        if not Path(filepath).exists():
            print(f"Sorry, couldn't find file: {filepath}")
            sys.exit(1)

        with open(filepath, mode="r", encoding="utf-8-sig") as csv_file:
            # Have arg and good file path -- read in rows as dicts.
            # Header row is:
            # Title, Group, Task List, Created Date, Due Date, Completed, Created By, Assigned To, Note, Priority

            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                self.line_count += 1

                newrow = self.validate_row(row)
                if newrow:
                    # newrow at this point is fully validated, and all FK relations exist,
                    # e.g. `newrow.get("Assigned To")`, is a Django User instance.
                    obj, created = Task.objects.update_or_create(
                        created_by=newrow.get("Created By"),
                        task_list=newrow.get("Task List"),
                        title=newrow.get("Title"),
                        defaults={
                            "assigned_to": newrow.get("Assigned To"),
                            "completed": newrow.get("Completed"),
                            "created_date": newrow.get("Created Date"),
                            "due_date": newrow.get("Due Date"),
                            "note": newrow.get("Note"),
                            "priority": newrow.get("Priority"),
                        },
                    )
                    self.upsert_count += 1
                    msg = (
                        f'Upserted task {obj.id}: "{obj.title}"'
                        f' in list "{obj.task_list}" (group "{obj.task_list.group}")'
                    )
                    self.upsert_msgs.append(msg)

        self.summary_msgs.append(f"\nProcessed {self.line_count} CSV rows")
        self.summary_msgs.append(f"Upserted {self.upsert_count} rows")

        _res = {
            "errors": self.error_msgs,
            "upserts": self.upsert_msgs,
            "summaries": self.summary_msgs,
        }
        return _res

    def validate_row(self, row):
        """Perform data integrity checks and set default values. Returns a valid object for insertion, or False.
        Errors are stored for later display."""

        row_errors = []

        # #######################
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

        # #######################
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

        # #######################
        # Group must exist
        try:
            target_group = Group.objects.get(name=row.get("Group"))
        except Group.DoesNotExist:
            msg = f"Could not find group {row.get('Group')}."
            row_errors.append(msg)

        # #######################
        # Task creator must be in the target group
        if creator and target_group not in creator.groups.all():
            msg = f"{creator} is not in group {target_group}"
            row_errors.append(msg)

        # #######################
        # Assignee must be in the target group
        if assignee and target_group not in assignee.groups.all():
            msg = f"{assignee} is not in group {target_group}"
            row_errors.append(msg)

        # #######################
        # Task list must exist in the target group
        try:
            tasklist = TaskList.objects.get(name=row.get("Task List"), group=target_group)
            row["Task List"] = tasklist
        except TaskList.DoesNotExist:
            msg = f"Task list {row.get('Task List')} in group {target_group} does not exist"
            row_errors.append(msg)

        # #######################
        # Validate Due Date
        dd = row.get("Due Date")
        if dd:
            try:
                row["Due Date"] = datetime.datetime.strptime(dd, "%Y-%m-%d")
            except ValueError:
                msg = f"Could not convert Due Date {dd} to python date"
                row_errors.append(msg)
        else:
            row["Created Date"] = None  # Override default empty string '' value

        # #######################
        # Validate Created Date
        cd = row.get("Created Date")
        if cd:
            try:
                row["Created Date"] = datetime.datetime.strptime(cd, "%Y-%m-%d")
            except ValueError:
                msg = f"Could not convert Created Date {cd} to python date"
                row_errors.append(msg)
        else:
            row["Created Date"] = None  # Override default empty string '' value

        # #######################
        # Group membership checks have passed
        row["Created By"] = creator
        row["Group"] = target_group
        if assignee:
            row["Assigned To"] = assignee

        # Set Completed
        row["Completed"] = True if row.get("Completed") == "Yes" else False

        # #######################
        if row_errors:
            self.error_msgs.append({self.line_count: row_errors})
            return False

        # No errors:
        return row
