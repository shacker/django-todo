from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse

from todo.operations.csv_importer import CSVImporter
from todo.utils import staff_check


@login_required
@user_passes_test(staff_check)
def import_csv(request) -> HttpResponse:
    """Import a specifically formatted CSV into stored tasks.
    """

    ctx = {"results": None}

    if request.method == "POST":
        filepath = request.FILES.get("csvfile")

        if not filepath:
            messages.error(request, "You must supply a CSV file to import.")
            return redirect(reverse("todo:import_csv"))

        importer = CSVImporter()
        results = importer.upsert(filepath)

        if results:
            ctx["results"] = results
        else:
            messages.error(request, "Could not parse provided CSV file.")
            return redirect(reverse("todo:import_csv"))

    return render(request, "todo/import_csv.html", context=ctx)
