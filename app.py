from flask import Flask, request, jsonify, send_from_directory
from parser import parser
from interpreter import run, global_env, NovaError
import io
import sys

app = Flask(__name__, static_folder=".")

# ---------------------------
# GUI ROUTE (FRONTEND)
# ---------------------------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# ---------------------------
# API ROUTE (BACKEND EXECUTION)
# ---------------------------
@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.get_json()

        if not data or "code" not in data:
            return jsonify({"error": "No code provided"}), 400

        code = data["code"]

        # Parse code into AST
        ast = parser.parse(code)

        if ast is None:
            return jsonify({"error": "Syntax error"}), 400

        # Capture interpreter output
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        run(ast, global_env)

        sys.stdout = old_stdout
        output = buffer.getvalue()

        return jsonify({
            "output": output
        })

    except NovaError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)