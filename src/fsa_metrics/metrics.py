"""Metrics for the FSA collector."""

from loguru import logger as log
from prometheus_client import Gauge

from .collector import FSACollector


class FileSizeAgeMetrics:
    """Product metrics class."""

    def __init__(self, fsa_dir, pattern):
        """FileSizeAgeMetrics constructor.

        Parameters
        ----------
        fsa_dir : str
            The top-level directory to scan files in.
        pattern : str
            The glob pattern to match names against.
        """
        log.trace(f"Instantiating {self.__class__}...")
        self.fsa_dir: str = f"{fsa_dir}"
        """Root of directory tree to scan."""
        self.pattern: str = f"{pattern}"
        """Pattern for matching filenames."""
        self.collector = FSACollector(fsa_dir, pattern)
        """An `fsa_metrics.collector.FSACollector` used to collect metrics data."""

        self.detail_gauges = {
            "size": Gauge(
                name="fsa_size_bytes",
                documentation="size of the file in bytes",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "age": Gauge(
                name="fsa_age_seconds",
                documentation="age of the file in seconds",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
        }
        """A dict of gauges for the individual files metrics."""

        self.summary_gauges = {
            "oldest_age": Gauge(
                name="fsa_oldest_age_seconds",
                documentation="age of the OLDEST file in the tree in seconds",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "oldest_size": Gauge(
                name="fsa_oldest_size_bytes",
                documentation="size of the OLDEST file in the tree in bytes",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "newest_age": Gauge(
                name="fsa_newest_age_seconds",
                documentation="age of the NEWEST file in the tree in seconds",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "newest_size": Gauge(
                name="fsa_newest_size_bytes",
                documentation="size of the NEWEST file in the tree in bytes",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "biggest_age": Gauge(
                name="fsa_biggest_age_seconds",
                documentation="age of the BIGGEST file in the tree in seconds",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "biggest_size": Gauge(
                name="fsa_biggest_size_bytes",
                documentation="size of the BIGGEST file in the tree in bytes",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "smallest_age": Gauge(
                name="fsa_smallest_age_seconds",
                documentation="age of the SMALLEST file in the tree in seconds",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
            "smallest_size": Gauge(
                name="fsa_smallest_size_bytes",
                documentation="size of the SMALLEST file in the tree in bytes",
                labelnames=["type", "pattern", "path", "name", "parent"],
            ),
        }
        """Summary gauges for oldest / newest / smallest / biggest details."""

        log.trace(f"Finished instantiating {self.__class__}.")

    def update_metrics(self):
        """Call the metrics collector and process the result."""
        log.debug("Updating metrics...")
        try:
            files_details = self.collector.collect()
        except Exception as err:  # pylint: disable-msg=broad-except
            raise RuntimeError(f"Fetching new data failed: {err}") from err

        # this clearing is required as otherwise values from previous iterations
        # that do not exist in the current run any more would still be around
        # with their old value:
        for name, gauge in self.detail_gauges.items():
            log.trace(f"Clearing labelsets for gauge {name}...")
            gauge.clear()

        g_size = self.detail_gauges["size"]
        g_age = self.detail_gauges["age"]
        pattern = self.pattern

        # not very elegant, potentially dangerous even - see the TODO in the collector
        # module about having details in a Box instead of a tuple...
        newest = oldest = biggest = smallest = files_details[0]

        for details in files_details:
            if not details:
                continue

            dirname, basename, ftype, size, age, parent = details
            g_size.labels(ftype, pattern, dirname, basename, parent).set(size)
            g_age.labels(ftype, pattern, dirname, basename, parent).set(age)
            if newest is None or age < newest[4]:
                newest = details
            if oldest is None or age > oldest[4]:
                oldest = details
            if biggest is None or size > biggest[3]:
                biggest = details
            if smallest is None or size < smallest[3]:
                smallest = details

        self.update_summary_metric("oldest", oldest)
        self.update_summary_metric("newest", newest)
        self.update_summary_metric("biggest", biggest)
        self.update_summary_metric("smallest", smallest)

    def update_summary_metric(self, name, details):
        """Helper method to update the various summary metrics gauges.

        Parameters
        ----------
        name : str
            The gauge name as stored in the `self.summary_gauges` dict.
        details : tuple
            The file details to use for updating the gauge.
        """
        pattern = self.pattern

        # log.trace(f"Updating '{name}' summary gauge: {details}")
        dirname, basename, ftype, size, age, parent = details

        gauge_size = self.summary_gauges[f"{name}_size"]
        gauge_size.clear()
        gauge_size.labels(ftype, pattern, dirname, basename, parent).set(size)

        gauge_age = self.summary_gauges[f"{name}_age"]
        gauge_age.clear()
        gauge_age.labels(ftype, pattern, dirname, basename, parent).set(age)
