import logging
import socket
import sys

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


DEFAULT_IMAP_TIMEOUT = 20


class Command(BaseCommand):
    help = "Starts a mail worker"

    def add_arguments(self, parser):
        parser.add_argument("--imap_timeout", type=int, default=30)
        parser.add_argument("worker_name")

    def handle(self, *args, **options):
        if not hasattr(settings, "TODO_MAIL_TRACKERS"):
            logger.error("missing TODO_MAIL_TRACKERS setting")
            sys.exit(1)

        worker_name = options["worker_name"]
        tracker = settings.TODO_MAIL_TRACKERS.get(worker_name, None)
        if tracker is None:
            logger.error("couldn't find configuration for %r in TODO_MAIL_TRACKERS", worker_name)
            sys.exit(1)

        # set the default socket timeout (imaplib doesn't enable configuring it)
        timeout = options["imap_timeout"]
        if timeout:
            socket.setdefaulttimeout(timeout)

        # run the mail polling loop
        producer = tracker["producer"]
        consumer = tracker["consumer"]

        consumer(producer())
