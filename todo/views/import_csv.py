from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from todo.operations.csv_importer import CSVImporter

from todo.utils import staff_check

@login_required
@user_passes_test(staff_check)
def import_csv(request) -> HttpResponse:
    """Import a specifically formatted CSV into stored tasks.
    """

    ctx = {}

    if request.method == "POST":
        filepath = request.FILES.get('csvfile')
        importer = CSVImporter()
        results = importer.upsert(filepath)
        ctx["results"] = results

    return render(request, "todo/import_csv.html", context=ctx)
