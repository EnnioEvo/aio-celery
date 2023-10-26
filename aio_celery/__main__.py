import argparse
import asyncio
import sys

from . import __version__
from .worker import run


def main() -> None:
    """
    Main entrypoint of aio_celery.
    """
    parser = argparse.ArgumentParser(
        prog="aio_celery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "CLI for aio_celery\n\n"
            "Examples\n"
            "--------\n"
            "$ %(prog)s worker proj:app\n"
            "$ %(prog)s worker -Q high,low proj:app\n"
            "$ %(prog)s worker --concurrency=50000 proj:app\n"
        ),
    )
    parser.add_argument(
        "-V",
        "--version",
        dest="version",
        action="store_true",
        help="print current aio_celery version and exit",
    )
    subparsers = parser.add_subparsers(
        title="Available subcommands",
        metavar="",
        dest="subcommand",
    )
    worker = subparsers.add_parser(
        "worker",
        help="Run worker",
        description="Run worker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    worker.add_argument(
        "app",
        help=(
            "Where to search for application instance. "
            "This string must be specified in 'module.module:variable' format."
        ),
    )
    worker.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=10_000,
        help="Maximum simultaneous async tasks",
    )
    worker.add_argument(
        "-Q",
        "--queues",
        help="Comma separated list of queues",
    )

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    if args.subcommand is None:
        parser.print_help()
        return

    if not (0 < args.concurrency <= 65535):
        print(
            "concurrency must be between 1 and 65535 "
            "(latter is maximum AMQP 0-9-1 prefetch count)",
            file=sys.stderr,
        )
        sys.exit(2)

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
