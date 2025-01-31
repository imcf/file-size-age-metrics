# 📐 ⏱ 🧮 File-Size-Age Metrics Exporter

[Prometheus][1] exporter providing size and age metrics about files.

## ⚙🔧 Installation ⚙🔧

Example installation on Debian / Ubuntu:

```bash
# required for creating Python virtualenvs:
apt update
apt install -y python3-venv

# create a virtualenv in /opt:
python3 -m venv /opt/fsa-metrics

# update 'pip' and install the 'file-size-age-metrics' package:
/opt/fsa-metrics/bin/pip install --upgrade pip
/opt/fsa-metrics/bin/pip install file-size-age-metrics
```

## 🏃 Running in foreground mode 🏃

This is mostly relevant for testing configuration settings and checking if the
exporter works as expected - to do this either activate the previously created
Python environment or call the `fsa-metrics` script using the full path to that
environment.

A configuration file is required for running the metrics exporter. Simply copy
the [config-example.yaml][3] file to e.g. `config.yaml` and adjust the settings
there. Then run the exporter like this:

```bash
fsa-metrics --config config.yaml
```

The exporter running in foreground can be terminated as usual via `Ctrl+C`.

## 👟 Running as a service 👟

FIXME!

## Known limitations

Currently only a single directory tree can be monitored. Adding support for
monitoring several trees with a single process is planned though.

[1]: https://prometheus.io/
[3]: resources/config-example.yaml
