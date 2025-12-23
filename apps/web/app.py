from flask import Flask, request, send_from_directory, redirect, url_for, jsonify, make_response
import os

app = Flask(__name__, static_folder=None)

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
api_host = os.environ.get("HOST_API", "localhost:8000")
host_scheme = os.environ.get("HOST_SCHEME", "http")
API_BASE = f"{host_scheme}://{api_host}"

def _inject_api_base(html_filename: str):
    resp = send_from_directory(WEB_DIR, html_filename)
    if resp.mimetype == "text/html":
        resp.direct_passthrough = False
        body = resp.get_data(as_text=True).replace("{{API_BASE}}", API_BASE)
        new_resp = make_response(body)
        new_resp.headers["Content-Type"] = resp.headers.get("Content-Type", "text/html; charset=utf-8")
        return new_resp
    return resp

@app.get("/")
def serve_root():
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return _inject_api_base("index.html")
    return redirect(url_for("serve_login"))

@app.get("/login")
def serve_login():
    return _inject_api_base("login.html")


@app.get("/private")
def serve_private_page():
    token = request.cookies.get("access_token")
    if not token:
        next_param = request.path
        return redirect(url_for("serve_login", next=next_param))
    return _inject_api_base("private.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
