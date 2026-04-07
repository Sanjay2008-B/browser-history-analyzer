import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from parser import parse_history
from analyzer import build_stats, search_history

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB

# In-memory cache for current session
_cache = {}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        df, browser = parse_history(filepath)
        stats = build_stats(df)
        _cache["df"] = df
        _cache["browser"] = browser
        stats["browser"] = browser
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        try:
            os.remove(filepath)
        except Exception:
            pass


@app.route("/api/search", methods=["GET"])
def search():
    if "df" not in _cache:
        return jsonify({"error": "No history loaded"}), 400

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []})

    results = search_history(_cache["df"], query)
    return jsonify({"results": results})


@app.route("/api/status", methods=["GET"])
def status():
    loaded = "df" in _cache
    return jsonify({
        "loaded": loaded,
        "browser": _cache.get("browser", None),
        "rows": len(_cache["df"]) if loaded else 0,
    })


if __name__ == "__main__":
    print("🌐 Browser History Analyzer running at http://localhost:5000")
    app.run(debug=True, port=5000)
