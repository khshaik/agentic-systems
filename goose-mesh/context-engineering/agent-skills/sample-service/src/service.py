"""Tiny dependency-free service used by the Agent Skill demo."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def health_payload() -> dict[str, str]:
    return {"status": "ok", "service": "sample-service"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        payload = json.dumps(health_payload()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("sample-service listening on http://127.0.0.1:8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
