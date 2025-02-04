# 📐 ⏱ 🧮 File-Size-Age Metrics Exporter

[![Poetry][badge_poetry]][poetry]

[Prometheus][1] exporter providing size and age metrics about files.

![FSA Metrics Grafana Demo Panel][fsa_panel]

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
there (alternatively, call `fsa-metrics --config SHOWCONFIGDEFAULTS` to have a
configuration example printed to stdout). Then run the exporter like this:

```bash
fsa-metrics --config config.yaml
```

The exporter running in foreground can be terminated as usual via `Ctrl+C`.

## 👟 Running as a service 👟

```bash
adduser --system fsaexporter
SITE_PKGS=$(/opt/fsa-metrics/bin/pip show file-size-age-metrics |
    grep '^Location: ' |
    cut -d ' ' -f 2
)
cp -v "$SITE_PKGS"/resources/systemd/fsa-metrics.service  /etc/systemd/system/
cp -v "$SITE_PKGS"/resources/config-example.yaml  /etc/fsa-metrics.yaml
vim /etc/fsa-metrics.yaml  # <- adapt settings to your requirements
systemctl daemon-reload
systemctl edit fsa-metrics.service
```

The last command will open an editor with the override configuration of the
service's unit file. Add a section like this **at the top** of the override
file, specifying where to find your configuration file for the service:

```text
[Service]
### configuration file for the FSA exporter service:
Environment=FSA_CONFIG=/etc/fsa-metrics.yaml
```

Note: on *Ubuntu 20.04* the `systemct edit` command will present you with an
empty file, so you will have to copy the respective lines from below or the
provided *central* unit file.

Finally enable the service and start it right away. The second line will show
the log messages on the console until `Ctrl+C` is pressed. This way you should
be able to tell if the service has started up properly and is providing metrics
on the configured port:

```bash
systemctl enable --now fsa-metrics.service
journalctl --follow --unit fsa-metrics
```

Open ports for the `fsa-metrics` exporter:

```bash
SOURCE="any"  # <-- put an IP address here to restrict access more
ufw allow from $SOURCE to any port fsa-metrics
```

## 🪂 Running via cron ⏰

In case you need the metrics exporter on a system where you are lacking
administrative privileges, running the exporter in kind of a
*poor-man's'service* approach through `cron` using a wrapper script is
absolutely feasible!

The wrapper script assumes the `fsa-metrics` venv will be placed in
`$HOME/.venvs/`, if that's not the case the path prefix in the script requires
to be adjusted.

```bash
mkdir -pv "$HOME/.venvs"
VENV_PATH="$HOME/.venvs/fsa-metrics"
python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/pip" install --upgrade pip
"$VENV_PATH/bin/pip" install file-size-age-metrics
SITE_PKGS=$("$VENV_PATH/bin/pip" show file-size-age-metrics |
    grep '^Location: ' |
    cut -d ' ' -f 2
)
cp -v "$SITE_PKGS/resources/config-example.yaml" "$VENV_PATH/fsa-metrics.yaml"
cp -v "$SITE_PKGS/resources/run-metrics-exporter.sh" "$VENV_PATH/bin/"
```

Obviously you also want to adapt the settings in the `.yaml` config file.

Now the wrapper can be put into a cron-job (`crontab -e`) that e.g. executes
once a minute and it will take care to only launch a new instance of the metrics
exporter if none is running. For example:

```cron
* * * * *  $HOME/.venvs/fsa-metrics/bin/run-metrics-exporter.sh
```

## Visualization in Grafana

To visualize data in a way as shown in the example panel above, queries like
the following ones may be used:

```text
sort(fsa_age_seconds{instance="pg_server.example.xy"})
sort(fsa_size_bytes{instance="pg_server.example.xy"})
```

## Known limitations

Currently only a single directory tree can be monitored. Adding support for
monitoring several trees with a single process is planned though.

## Scalability and resource usage considerations

The exporter is designed with code simplicity as a goal, it's *not* optimized
for efficiency or low resource usage. A few numbers on an average laptop running
the exporter on a rather large file tree (not recommended, just for
demonstration purposes):

- Number of files monitored: ~200'000
- Memory consumption: ~350 MB
- Metrics collection duration: < 10s

[1]: https://prometheus.io/
[3]: resources/config-example.yaml

[poetry]: https://python-poetry.org/
[badge_poetry]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json
[fsa_panel]: https://imcf.one/images/fsa-metrics-demo-panel.png
