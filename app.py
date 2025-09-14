#Backend 

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pw_manager as pwm

app = Flask(__name__)

CORS(app)
# --- Store master key globally for simplicity (later use session/auth) ---
master_key = None

@app.route("/")
def index():
    return ("its workingg rahh")

@app.route("/set_master", methods=["POST"])
def set_master():
    global master_key
    data = request.json
    master_password = data.get("master_password")
    if not master_password:
        return jsonify({"error": "Master password required"}), 400
    master_key = pwm.generate_key(master_password)
    return jsonify({"message": "Master password set ✅", "redirect": "/manage"})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    length = data.get("length", 12)
    uppercase = data.get("uppercase", True)
    digits = data.get("digits", True)
    symbols = data.get("symbols", True)
    password = pwm.generate_password(length, uppercase, digits, symbols)
    return jsonify({"password": password})

@app.route("/add", methods=["POST"])
def add():
    if not master_key:
        return jsonify({"error": "Set master password first"}), 400
    data = request.json
    account = data.get("account")
    password = data.get("password")
    if not account or not password:
        return jsonify({"error": "Account and password required"}), 400
    encrypted = pwm.encrypt_password(master_key, password)
    pwm.add_entry(account, encrypted)
    return jsonify({"message": f"Password for {account} saved ✅"})

@app.route("/get/<account>", methods=["GET"])
def get(account):
    if not master_key:
        return jsonify({"error": "Set master password first"}), 400
    encrypted = pwm.get_entry(account)
    if not encrypted:
        return jsonify({"error": "Account not found"}), 404
    try:
        password = pwm.decrypt_password(master_key, encrypted)
        return jsonify({"account": account, "password": password})
    except Exception:
        return jsonify({"error": "Failed to decrypt. Wrong master password?"}), 401

@app.route("/list", methods=["GET"])
def list_accounts():
    accounts = pwm.list_accounts()
    return jsonify({"accounts": accounts})

if __name__ == "__main__":
    app.run(debug=True)
