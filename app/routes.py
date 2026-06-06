from flask import Blueprint, jsonify, render_template, request
import requests as http_requests
import groq
from app.services.raiderio import get_character
from app.services.analyzer import analyze_party

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/health")
def health():
    return {"status": "ok"}, 200


@bp.route("/analyze", methods=["POST"])
def analyze():
    body = request.get_json(silent=True)
    if not body or "characters" not in body:
        return jsonify({"error": "Request body must include a 'characters' list"}), 400

    characters = body["characters"]
    if not isinstance(characters, list) or len(characters) == 0:
        return jsonify({"error": "'characters' must be a non-empty list"}), 400
    if len(characters) > 5:
        return jsonify({"error": "A maximum of 5 characters is allowed"}), 400

    results = []
    for char in characters:
        region = char.get("region", "")
        realm = char.get("realm", "")
        name = char.get("name", "")
        if not all([region, realm, name]):
            return jsonify({"error": f"Each character must have region, realm, and name: {char}"}), 400
        try:
            data = get_character(region, realm, name)
        except http_requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                return jsonify({
                    "error": f"Character not found: {name} on {realm}-{region.upper()}"
                }), 404
            return jsonify({"error": f"Raider.io error for {name}: {str(e)}"}), 502
        results.append(data)

    try:
        analysis = analyze_party(results)
    except (groq.GroqError, ValueError) as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 502

    return jsonify({"characters": results, "analysis": analysis})
