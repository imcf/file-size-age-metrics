"""Metrics collection classes."""

from glob import glob
import os
import time

from loguru import logger as log

from prometheus_client import Summary


COLLECTOR_TIME = Summary(
    "fsa_collect_data_time", "time spent collecting file-size-age metrics"
)
"""Performance metric showing time spent for collecting data."""


# TODO: consider putting the details in a Box object!
def get_file_details(filename):
    """Collect details about the given file.

    Parameters
    ----------
    filename : str
        The file to scan.

    Returns
    -------
    tuple(str, str, str, int, float)
        A tuple with file details:
        - The directory name of the file.
        - The basename of the file.
        - The file type, one of `file`, `dir`, `link`, `other`.
        - The size of the file in bytes.
        - The "file age", as in: the time since the last file modification.
    """
    dirname = os.path.dirname(filename)
    parent_dir = os.path.basename(dirname)
    basename = os.path.basename(filename)
    file_type = "other"

    try:
        if os.path.isfile(filename):
            file_type = "file"
        elif os.path.isdir(filename):
            file_type = "dir"
        elif os.path.islink(filename):
            file_type = "link"
        size = os.path.getsize(filename)
        age = time.time() - os.path.getmtime(filename)
    except Exception as err:
        log.warning(f"Unable to get details for [{filename}]: {err}")
        return None

    return (dirname, basename, file_type, size, age, parent_dir)


@COLLECTOR_TIME.time()
def scan_files(path, pattern):
    """Wrapper for scanning files and collecting their metrics.

    Parameters
    ----------
    path : str
        The root path to scan for files.
    pattern : str
        A glob-style pattern to match filenames against.

    Returns
    -------
    list(tuple)
    """
    log.trace(f"Scanning files at [{path}]...")
    files = glob(f"{path}/{pattern}", recursive=True)
    log.trace(f"Found {len(files)} files, fetching details...")
    details = [get_file_details(filename) for filename in files]
    log.debug(f"Scanned {len(details)} files.")

    return details


class FSACollector:
    """Collector for file size and age data."""

    def __init__(self, fsa_dir, pattern):
        """FSACollector constructor.

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

        log.debug(f"Settings: pattern=[{self.pattern}] dir=[{self.fsa_dir}]")

    def collect(self):
        """Scan the directory tree and collect the file metrics.

        Returns
        -------
        list(tuple)
            A list with file details as generated by `scan_files`.

        Note
        ----
        Exceptions are silenced into log messages as they shouldn't be passed on
        when running in service mode.
        """
        try:
            details = scan_files(self.fsa_dir, self.pattern)
        except Exception as err:  # pylint: disable-msg=broad-except
            log.error(f"Failed scanning files: {err}")
            return None

        return details
