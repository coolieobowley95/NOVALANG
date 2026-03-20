"""
# Group Members: 
# Member 1:
    Name: Tashana Henry 
    ID: 1804274
    Email: Henrytashana09@gmail.com
# Member 2:
    Name: Orine Stephenson, 
    ID: 2005009
    Email: orinestephenson4@gmail.com
# Member 3:
    Name: Coolieo Bowley 
    ID: 2003923 
    Email: coolieobowley95@gmail.com
# Member 4:
    Name: Jonathan Masters
    ID#: 2100098
    Email: jonathanmasters2018@gmail.com
# Member 5:
    Name: Shavon Scale
    ID#: 2008093
    Email: shavonscale@gmail.com
    
NOVALANG Interpreter - Semantic Analysis & Execution Module
Executes the AST and manages runtime state
"""

from flask import Flask, request, jsonify, send_from_directory
from parser import parser
from interpreter import run, Env, NovaError
import io
import sys

app = Flask(__name__, static_folder=".")


# ---------------------------
# FRONTEND ROUTE
# ---------------------------
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# ---------------------------
# RUN CODE ROUTE
# ---------------------------
@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.get_json()

        if not data or "code" not in data:
            return jsonify({"error": "No code provided"}), 400

        code = data["code"]

        # Parse AST
        ast = parser.parse(code)

        if ast is None:
            return jsonify({"error": "Syntax error"}), 400

        # Capture print output
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        # 🔥 FIX: NEW ENVIRONMENT EVERY RUN
        env = Env()
        run(ast, env)

        sys.stdout = old_stdout
        output = buffer.getvalue()

        return jsonify({"output": output})

    except NovaError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# START SERVER
# ---------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)