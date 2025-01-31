"""Extremely basic metrics exporter reporting file sizes and ages."""

import os
import glob
import http.server
import socketserver
import time
from datetime import datetime, timedelta

PORT = int(os.getenv("FSA_PORT", "16061"))
DIR = os.getenv("FSA_DIR", "/var/backups/")
FILE_PATTERN = os.getenv("FSA_PATTERN", "**")


class MetricsRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler to build and expose metrics requests."""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        filenames = glob.glob(f"{DIR}/{FILE_PATTERN}", recursive=True)
        files_details = [
            (
                fname,
                os.path.getsize(os.path.join(DIR, fname)),
                os.path.getmtime(os.path.join(DIR, fname)),
                time.time() - os.path.getmtime(os.path.join(DIR, fname)),
            )
            for fname in filenames
        ]
        files_details.sort(key=lambda x: x[2], reverse=True)

        fsa_size = "# HELP fsa_size_bytes The size of the file in bytes "
        fsa_size += f"(path=[{DIR}], pattern=[{FILE_PATTERN}]\n"
        fsa_size += "# TYPE fsa_size_bytes gauge\n"

        for fname, size, mtime, age in files_details:
            mtime = datetime.fromtimestamp(mtime)

            # print(mtime.date())
            # print(datetime.today().date() - timedelta(days=1))
            age_range = "today"
            if mtime.date() < datetime.today().date() - timedelta(days=365):
                age_range = "more_than_a_year"
            elif mtime.date() < datetime.today().date() - timedelta(days=28):
                age_range = "more_than_a_month"
            elif mtime.date() < datetime.today().date() - timedelta(days=7):
                age_range = "more_than_a_week"
            elif mtime.date() < datetime.today().date() - timedelta(days=1):
                age_range = "less_than_a_week"
            elif mtime.date() == datetime.today().date() - timedelta(days=1):
                age_range = "yesterday"

            fsa_size += f'fsa_size_bytes{{name="{fname}"}} {size}\n'
            # fsa_size += f'file_size{{name="{fname}", date="{mtime}", age="{age}", '
            # fsa_size += f'age_range="{age_range}"}} {size}\n'

        html = fsa_size
        self.wfile.write(bytes(html, "utf8"))


with socketserver.TCPServer(("", PORT), MetricsRequestHandler) as my_server:
    my_server.serve_forever()
