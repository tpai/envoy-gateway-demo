from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

from flask import Flask, jsonify, request
from urllib.parse import quote
from flask_cors import CORS
import jwt
import os

app = Flask(__name__, static_folder=None)

# CORS configuration
# Comma-separated list of allowed origins, e.g. "http://localhost:3000,https://example.com"
_CORS_ALLOWED = os.getenv("CORS_ALLOWED_ORIGINS", "*").strip()
if _CORS_ALLOWED == "*" or _CORS_ALLOWED == "":
    CORS(app, resources={r"/api/*": {"origins": "*"}})
else:
    origins = [o.strip() for o in _CORS_ALLOWED.split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})

JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_ISS = os.getenv("JWT_ISS", "auth.example.com")
JWT_AUD = os.getenv("JWT_AUD", "private-api.example.com")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-prod")
ACCESS_TOKEN_EXPIRES_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "30"))
LOGIN_URL = os.getenv("LOGIN_URL", "http://localhost:8000/login")

def create_access_token(sub: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iss": JWT_ISS,
        "aud": JWT_AUD,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALG],
            audience=JWT_AUD,
            issuer=JWT_ISS,
        )
        return payload
    except Exception:
        return None


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            # Missing token -> 401 Unauthorized instead of redirect
            return jsonify({"error": "unauthorized", "reason": "missing_bearer"}), 401
        token = auth.split(" ", 1)[1].strip()
        payload = verify_token(token)
        if not payload:
            # Invalid/expired token -> 401 Unauthorized instead of redirect
            return jsonify({"error": "unauthorized", "reason": "invalid_token"}), 401
        request.jwt_payload = payload
        return fn(*args, **kwargs)

    return wrapper


@app.route("/api/public", methods=["GET"])
def public():
    return jsonify({"message": "This is a public endpoint."})


@app.route("/api/private", methods=["GET"])
@jwt_required
def private():
    sub = getattr(request, "jwt_payload", {}).get("sub", "unknown")
    return jsonify({"message": f"Hello {sub}, this is a private endpoint."})


@app.route("/api/auth", methods=["GET"], strict_slashes=False)  
@jwt_required
def auth_validate():
    payload = getattr(request, "jwt_payload", {})
    return jsonify({"valid": True, "payload": payload})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "admin":
        token = create_access_token(sub=username)
        return jsonify({"access_token": token, "token_type": "Bearer", "expires_in_minutes": ACCESS_TOKEN_EXPIRES_MIN})

    return jsonify({"error": "invalid credentials"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
