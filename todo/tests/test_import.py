import datetime
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from todo.models import Task, TaskList
from todo.operations.csv_importer import CSVImporter


"""
Exercise the "Import CSV" feature, which shares a functional module that serves
both the `import_csv` management command and the "Import CSV" web interface.
"""


@pytest.mark.django_db
@pytest.fixture
def import_setup(todo_setup):
    app_path = Path(__file__).resolve().parent.parent
    filepath = Path(app_path, "tests/data/csv_import_data.csv")
    with filepath.open(mode="r", encoding="utf-8-sig") as fileobj:
        importer = CSVImporter()
        results = importer.upsert(fileobj, as_string_obj=True)
        assert results
    return {"results": results}


@pytest.mark.django_db
def test_setup(todo_setup):
    """Confirm what we should have from conftest, prior to importing CSV."""
    assert TaskList.objects.all().count() == 2
    assert Task.objects.all().count() == 6


@pytest.mark.django_db
def test_import(import_setup):
    """Confirm that importing the CSV gave us two more rows (one should have been skipped)"""
    assert Task.objects.all().count() == 8  # 2 out of 3 rows should have imported; one was an error


@pytest.mark.django_db
def test_report(import_setup):
    """Confirm that importing the CSV returned expected report messaging."""

    results = import_setup["results"]

    assert "Processed 3 CSV rows" in results["summaries"]
    assert "Upserted 2 rows" in results["summaries"]
    assert "Skipped 1 rows" in results["summaries"]

    assert isinstance(results["errors"], list)
    assert len(results["errors"]) == 1
    assert (
        results["errors"][0].get(3)[0]
        == "Could not convert Created Date 2015-06-248 to valid date instance"
    )

    assert (
        'Upserted task 7: "Make dinner" in list "Zip" (group "Workgroup One")' in results["upserts"]
    )
    assert (
        'Upserted task 8: "Bake bread" in list "Zip" (group "Workgroup One")' in results["upserts"]
    )


@pytest.mark.django_db
def test_inserted_row(import_setup):
    """Confirm that one inserted row is exactly right."""
    task = Task.objects.get(title="Make dinner", task_list__name="Zip")
    assert task.created_by == get_user_model().objects.get(username="u1")
    assert task.assigned_to == get_user_model().objects.get(username="u1")
    assert not task.completed
    assert task.note == "This is note one"
    assert task.priority == 3
    assert task.created_date == datetime.datetime.today().date()
