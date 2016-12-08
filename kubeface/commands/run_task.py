'''
Run a task. Used internally, not meant to be called by a user.
'''

import sys
import argparse
import logging
import tempfile

from .. import storage, serialization

parser = argparse.ArgumentParser(description=__doc__)

parser.add_argument("input_path")
parser.add_argument("result_path")

parser.add_argument(
    "--delete-input",
    action="store_true",
    default=False,
    help="Delete input file on success.")

parser.add_argument(
    "--quiet",
    action="store_true",
    default=False,
    help="")

parser.add_argument(
    "--verbose",
    action="store_true",
    default=False,
    help="")


def run(argv=sys.argv[1:]):
    args = parser.parse_args(argv)

    logging.info("Reading: %s" % args.input_path)
    input_handle = storage.get(args.input_path)
    task = serialization.load(input_handle)

    logging.info("Deserailized task: %s" % task)
    logging.info("Running task.")
    result = task.run()
    logging.info("Done running task.")

    with tempfile.TemporaryFile(
            prefix="kubeface-run-task-result-", suffix=".pkl") as fd:
        logging.info("Serializing.")
        serialization.dump(result, fd)
        logging.info("Serialized to %d bytes." % fd.tell())
        fd.seek(0)
        logging.info("Writing: %s" % args.result_path)
        storage.put(args.result_path, fd)

    if args.delete_input:
        logging.info("Deleting: %s" % args.input_path)
        storage.delete(args.input_path)

    logging.info("Done.")