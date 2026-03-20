from flask import Flask, request, jsonify
from parser import parser
from interpreter import run, global_env, NovaError

app = Flask(__name__)

@app.route("/")
def home():
    return "NovaLang API is running 🚀"

@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        ast = parser.parse(code)

        if ast is None:
            return jsonify({"error": "Syntax error"}), 400

        import io, sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        run(ast, global_env)

        sys.stdout = old_stdout
        output = buffer.getvalue()

        return jsonify({"output": output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)