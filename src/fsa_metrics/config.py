"""Configuration loader function(s)."""

from box import Box


def load_config_file(filename):
    """Assemble a config object from a YAML file.

    Values that are not provided in the file will be filled with built-in defaults.

    Parameters
    ----------
    filename : str
        The path to a YAML file containing the configuration to parse. If `filename` is
        empty, a config object with the default settings will be created.

    Returns
    -------
    box.Box
        The config object with default settings unless overridden from the given file.
        Properties of the box are (defaults shown in square brackets):
        - `port` (str): the TCP port where the metrics will be provided [16061]
        - `interval` (int) : the interval at which metrics are updated [60]
        - `verbosity` (int) : logging verbosity [0]
        - `fsa_dir` (str) : the path to scan for files [`/var/backups`]
        - `pattern` (str) : a glob pattern for matching filenames [`**`]
    """
    if not filename:
        config = Box({})
    else:
        config = Box.from_yaml(filename=filename)

    if "port" not in config.keys():
        config.port = "16061"
    if "fsa_dir" not in config.keys():
        config.fsa_dir = "/var/backups"
    if "pattern" not in config.keys():
        config.pattern = "**"
    if "interval" not in config.keys():
        config.interval = 60
    if "verbosity" not in config.keys():
        config.verbosity = 0

    return config
