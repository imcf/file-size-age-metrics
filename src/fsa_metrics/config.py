"""Configuration loader function(s)."""

from box import Box


def load_config_file(filename):
    """Assemble a config object by loading values from a file."""
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
