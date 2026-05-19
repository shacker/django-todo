from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_fk_to_m2m(apps, schema_editor):
    """Copy existing single-user FK assignments into the new M2M table."""
    Task = apps.get_model("todo", "Task")
    for task in Task.objects.filter(assigned_to_fk__isnull=False):
        task.assigned_to.add(task.assigned_to_fk_id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("todo", "0012_add_related_name_to_comments"),
    ]

    operations = [
        # Rename old FK to a temp name so the new M2M can take the original name
        migrations.RenameField(
            model_name="task",
            old_name="assigned_to",
            new_name="assigned_to_fk",
        ),
        # Change the FK's related_name to avoid clashing with the new M2M's related_name
        migrations.AlterField(
            model_name="task",
            name="assigned_to_fk",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="todo_assigned_to_fk",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Add the new M2M field
        migrations.AddField(
            model_name="task",
            name="assigned_to",
            field=models.ManyToManyField(
                blank=True,
                related_name="todo_assigned_to",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Preserve existing assignments
        migrations.RunPython(copy_fk_to_m2m, migrations.RunPython.noop),
        # Drop the old FK column
        migrations.RemoveField(
            model_name="task",
            name="assigned_to_fk",
        ),
    ]
