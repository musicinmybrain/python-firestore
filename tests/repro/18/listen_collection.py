import argparse
import logging
import sys
import threading

from google.cloud import firestore_v1
from google.cloud.firestore_v1 import watch


logger = logging.getLogger("listen_collection")


def main(parsed):
    callback_done = threading.Event()
    callback_done.clear()
    db = firestore_v1.Client()
    coll_ref = db.collection(parsed.collection)

    modified = 0

    def callback(doc_snapshot, changes, read_time):
        nonlocal modified

        logger.info(f"Notified: {read_time.isoformat()}")

        if len(changes) > 0:
            for change in changes:
                if change.type == watch.ChangeType.MODIFIED:
                    modified += 1
                    logger.info(f"Change: {change.type:20} [{modified:6}]")
                elif change.type == watch.ChangeType.REMOVED:
                    logger.info("Deleted")
                    callback_done.set()
                else:
                    logger.info(f"Change: {change.type:20}")

    logger.info(f"Watching: {coll_ref._path}")
    coll_ref.on_snapshot(callback)

    logger.info("Waiting...")
    callback_done.wait()


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    parser = argparse.ArgumentParser(description="Listen to changes to a collection")
    parser.add_argument("--collection", default="repro_gcf_18", help="ID of collection")
    parsed = parser.parse_args()
    main(parsed)
