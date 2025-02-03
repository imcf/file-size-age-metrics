"""Command-line functions / entry points."""

from time import sleep
import sys

import click
from loguru import logger as log
from prometheus_client import Info, start_http_server

from . import __version__
from .config import load_config_file
from .metrics import FileSizeAgeMetrics


def configure_logging(verbose: int):
    """Configure loguru logging / change log level.

    Parameters
    ----------
    verbose : int
        Desired log level, 1: SUCCESS, 2: INFO, 3: DEBUG, >=4: TRACE.
    """
    verbose = verbose if verbose <= 4 else 4
    mapping = {1: "SUCCESS", 2: "INFO", 3: "DEBUG", 4: "TRACE"}
    log.remove()
    log.add(sys.stderr, level=mapping[verbose])
    log.info(f"Setting log level to [{mapping[verbose]}].")


@click.command(help="Run the FSA metrics collector and exporter.")
@click.option(
    "--config",
    "conffile",
    required=True,
    help="""Path to a YAML configuration file. Use the pseudo filename
    'SHOWCONFIGDEFAULTS' to print the format and default values.""",
    envvar="FSA_CONFIG",
)
def run_fsa_exporter(conffile):
    """Main CLI entry point for the exporter. Blocking.

    Parameters
    ----------
    config : str
        The path to a YAML config file.
    """
    if conffile == "SHOWCONFIGDEFAULTS":
        config = load_config_file(None)
        with click.get_current_context() as ctx:
            click.echo(ctx.get_help())
            click.echo("\n\n== EXAMPLE CONFIGURATION FILE ==\n")
            click.echo(f"# ---\n{config.to_yaml()}# ---\n")
            sys.exit(0)

    config = load_config_file(conffile)
    configure_logging(config.verbosity)

    start_http_server(config.port)
    log.success(f"Providing metrics via HTTP on port {config.port}.")
    metrics = FileSizeAgeMetrics(config)

    info = Info(
        name="fsa_exporter",
        documentation="Information on the File-Size-Age metrics collector",
    )
    info.info(
        {
            "version": __version__,
            "collection_interval": f"{config.interval}s",
        }
    )

    log.success(
        f"{__package__} {__version__} started, "
        f"collection interval {config.interval}s."
    )

    while True:
        log.trace("Updating gauges status...")
        try:
            metrics.update_metrics()
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Updating metrics failed: {err}")
        sleep(config.interval)
