import email
import email.parser
import imaplib
import logging
import time

from email.policy import default
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def imap_check(command_tuple):
    status, ids = command_tuple
    assert status == "OK", ids


@contextmanager
def imap_connect(host, port, username, password):
    conn = imaplib.IMAP4_SSL(host=host, port=port)
    conn.login(username, password)
    imap_check(conn.list())
    try:
        yield conn
    finally:
        conn.close()


def parse_message(message):
    for response_part in message:
        if not isinstance(response_part, tuple):
            continue

        message_metadata, message_content = response_part
        email_parser = email.parser.BytesFeedParser(policy=default)
        email_parser.feed(message_content)
        return email_parser.close()


def search_message(conn, *filters):
    status, message_ids = conn.search(None, *filters)
    for message_id in message_ids[0].split():
        status, message = conn.fetch(message_id, "(RFC822)")
        yield message_id, parse_message(message)


def imap_producer(
    process_all=False,
    preserve=False,
    host=None,
    port=993,
    username=None,
    password=None,
    nap_duration=1,
    input_folder="INBOX",
):
    logger.debug("starting IMAP worker")
    imap_filter = "(ALL)" if process_all else "(UNSEEN)"

    def process_batch():
        logger.debug("starting to process batch")
        # reconnect each time to avoid repeated failures due to a lost connection
        with imap_connect(host, port, username, password) as conn:
            # select the requested folder
            imap_check(conn.select(input_folder, readonly=False))

            try:
                for message_uid, message in search_message(conn, imap_filter):
                    logger.info(f"received message {message_uid}")
                    try:
                        yield message
                    except Exception:
                        logger.exception(f"something went wrong while processing {message_uid}")
                        raise

                    if not preserve:
                        # tag the message for deletion
                        conn.store(message_uid, "+FLAGS", "\\Deleted")
                else:
                    logger.debug("did not receive any message")
            finally:
                if not preserve:
                    # flush deleted messages
                    conn.expunge()

    while True:
        try:
            yield from process_batch()
        except (GeneratorExit, KeyboardInterrupt):
            # the generator was closed, due to the consumer
            # breaking out of the loop, or an exception occuring
            raise
        except Exception:
            logger.exception("mail fetching went wrong, retrying")

        # sleep to avoid using too much resources
        # TODO: get notified when a new message arrives
        time.sleep(nap_duration)
