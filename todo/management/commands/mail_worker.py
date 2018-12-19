import logging
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Starts a mail worker"

    def add_arguments(self, parser):
        parser.add_argument("worker_name")

    def handle(self, *args, **options):
        if not hasattr(settings, "TODO_MAIL_TRACKERS"):
            logger.error("missing TODO_MAIL_TRACKERS setting")
            sys.exit(1)

        worker_name = options["worker_name"]
        tracker = settings.TODO_MAIL_TRACKERS.get(worker_name, None)
        if tracker is None:
            logger.error(
                f"couldn't find configuration for {worker_name} in TODO_MAIL_TRACKERS"
            )
            sys.exit(1)

        producer = tracker["producer"]
        consumer = tracker["consumer"]

        consumer(producer())
