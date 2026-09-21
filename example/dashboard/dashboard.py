import html
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import pymysql
from pymysql.cursors import DictCursor


def required_env(name):
    value = os.environ.get(name)
    if value is None:
        raise RuntimeError(f"環境変数 {name} が設定されていません")
    return value


def database_config():
    return {
        "host": required_env("OCEANBASE_HOST"),
        "port": int(required_env("OCEANBASE_PORT")),
        "user": required_env("OCEANBASE_USER"),
        "password": required_env("OCEANBASE_PASSWORD"),
        "database": required_env("OCEANBASE_DATABASE"),
    }


def load_dashboard_data():
    connection = pymysql.connect(
        **database_config(),
        connect_timeout=5,
        cursorclass=DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            version = cursor.fetchone()["version"]

            cursor.execute("SELECT COUNT(*) AS count FROM users")
            user_count = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT id, name, created_at FROM users "
                "ORDER BY id"
            )
            users = cursor.fetchall()

        return {
            "version": version,
            "user_count": user_count,
            "users": users,
        }
    finally:
        connection.close()


def escape(value):
    return html.escape(str(value), quote=True)


def render_page(data=None, error=None):
    if error:
        status = "Connection error"
        status_class = "error"
        version = "Unavailable"
        user_count = "-"
        rows = "<tr><td colspan=\"3\" class=\"empty\">データを取得できませんでした</td></tr>"
        error_panel = f'<div class="alert error" role="alert">{escape(error)}</div>'
    else:
        status = "Connected"
        status_class = "connected"
        version = escape(data["version"])
        user_count = escape(data["user_count"])
        rows = "".join(
            "<tr>"
            f"<td>{escape(row['id'])}</td>"
            f"<td>{escape(row['name'])}</td>"
            f"<td>{escape(row['created_at'])}</td>"
            "</tr>"
            for row in data["users"]
        )
        if not rows:
            rows = '<tr><td colspan="3" class="empty">users は空です</td></tr>'
        error_panel = ""

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OceanBase Developer Lab</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17212b;
      --muted: #647382;
      --line: #dce4e8;
      --paper: #f7faf9;
      --panel: #ffffff;
      --teal: #087f73;
      --teal-dark: #075b54;
      --red: #a53b3b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: radial-gradient(circle at top right, #dcefeb, transparent 34%), var(--paper);
      font: 16px/1.5 ui-sans-serif, system-ui, sans-serif;
    }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 48px 24px 64px; }}
    .eyebrow {{ color: var(--teal); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: .78rem; }}
    h1 {{ margin: 8px 0 10px; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.05; letter-spacing: 0; }}
    .intro {{ color: var(--muted); max-width: 650px; margin: 0 0 32px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 16px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 22px; box-shadow: 0 10px 30px #163b3b0d; }}
    h2 {{ font-size: 1rem; margin: 0 0 16px; }}
    .status {{ display: flex; align-items: center; gap: 10px; font-size: 1.25rem; font-weight: 700; }}
    .dot {{ width: 11px; height: 11px; border-radius: 50%; background: var(--red); }}
    .dot.connected {{ background: var(--teal); }}
    .label {{ color: var(--muted); font-size: .82rem; margin-top: 16px; }}
    .value {{ font-weight: 650; overflow-wrap: anywhere; }}
    .count {{ font-size: 2.3rem; color: var(--teal-dark); font-weight: 750; }}
    .table-head {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    .table-head h2 {{ margin: 0; }}
    .button {{ color: #fff; background: var(--teal); border: 0; border-radius: 5px; padding: 10px 16px; font: inherit; font-weight: 700; text-decoration: none; cursor: pointer; }}
    .button:hover {{ background: var(--teal-dark); }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    th, td {{ padding: 13px 12px; border-bottom: 1px solid var(--line); white-space: nowrap; }}
    th {{ color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; }}
    .empty {{ color: var(--muted); text-align: center; padding: 28px; }}
    .alert {{ border: 1px solid #e3aaaa; color: var(--red); background: #fff5f3; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px; overflow-wrap: anywhere; }}
    @media (max-width: 680px) {{ main {{ padding: 32px 16px 48px; }} .grid {{ grid-template-columns: 1fr; }} .table-head {{ align-items: flex-start; flex-direction: column; }} }}
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">OceanBase Developer Lab</div>
    <h1>Data at a glance.</h1>
    <p class="intro">Codespaces 上の OceanBase CE に格納された移行データを確認します。</p>
    {error_panel}
    <section class="grid" aria-label="Database status">
      <article class="panel">
        <h2>Connection</h2>
        <div class="status"><span class="dot {status_class}"></span>{status}</div>
        <div class="label">Server version</div>
        <div class="value">{version}</div>
      </article>
      <article class="panel">
        <h2>Statistics</h2>
        <div class="label">Users</div>
        <div class="count">{user_count}</div>
        <div class="label">records in users</div>
      </article>
    </section>
    <section class="panel">
      <div class="table-head">
        <h2>Migrated Users</h2>
        <a class="button" href="/" aria-label="最新データを再取得">Refresh</a>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Created At</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            body = render_page(data=load_dashboard_data())
        except Exception as error:
            body = render_page(error=str(error))

        payload = body.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


def main():
    host = "0.0.0.0"
    port = int(os.environ.get("WEB_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"OceanBase dashboard listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()