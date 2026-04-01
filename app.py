from flask import Flask, request, jsonify, send_from_directory
from parser import parser
from lexer import lexer
from interpreter import run, global_env, NovaError
import io
import sys
import os

app = Flask(__name__, static_folder='.')

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SKIP_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}


def _safe_path(relative_path):
    """Resolve a user path safely inside project root."""
    if not relative_path:
        raise ValueError('Missing file path')

    normalized = relative_path.replace('\\', '/').strip().lstrip('/')
    absolute = os.path.abspath(os.path.join(PROJECT_ROOT, normalized))

    if not absolute.startswith(PROJECT_ROOT):
        raise ValueError('Invalid file path')
    if not absolute.endswith('.nl'):
        raise ValueError('Only .nl files are allowed')

    return absolute, normalized


def _list_novalang_files():
    files = []
    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith('.nl'):
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, PROJECT_ROOT).replace('\\', '/')
                files.append(rel_path)
    return sorted(files)


# ---------------------------
# GUI ROUTE (FRONTEND)
# ---------------------------
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


# ---------------------------
# API ROUTE (BACKEND EXECUTION)
# ---------------------------
@app.route('/run', methods=['POST'])
def run_code():
    old_stdout = sys.stdout
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing request payload'}), 400

        code = data.get('code')
        file_path = data.get('path')
        used_path = None

        if file_path:
            abs_path, used_path = _safe_path(file_path)
            if not os.path.exists(abs_path):
                return jsonify({'error': f"File not found: {file_path}"}), 404
            with open(abs_path, 'r', encoding='utf-8') as f:
                code = f.read()

        if code is None:
            return jsonify({'error': 'No code provided'}), 400

        # Reset lexer line counter for each parse so syntax errors report correct lines.
        lexer.lineno = 1
        ast = parser.parse(code, lexer=lexer)
        if ast is None:
            return jsonify({'error': 'Syntax error'}), 400

        sys.stdout = buffer = io.StringIO()
        run(ast, global_env)
        output = buffer.getvalue()

        return jsonify({'output': output, 'path': used_path})

    except NovaError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        sys.stdout = old_stdout


@app.route('/api/files', methods=['GET'])
def list_files():
    return jsonify({'files': _list_novalang_files()})


@app.route('/api/file', methods=['GET'])
def read_file():
    file_path = request.args.get('path', '')
    try:
        abs_path, normalized = _safe_path(file_path)
        if not os.path.exists(abs_path):
            return jsonify({'error': f"File not found: {file_path}"}), 404

        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({'path': normalized, 'code': content})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/create', methods=['POST'])
def create_file():
    data = request.get_json() or {}
    file_path = data.get('path', '')
    content = data.get('code', '')
    try:
        abs_path, normalized = _safe_path(file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        if os.path.exists(abs_path):
            return jsonify({'error': f"File already exists: {normalized}"}), 409

        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return jsonify({'message': 'File created', 'path': normalized}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/save', methods=['POST'])
def save_file():
    data = request.get_json() or {}
    file_path = data.get('path', '')
    content = data.get('code')
    if content is None:
        return jsonify({'error': 'Missing code content'}), 400

    try:
        abs_path, normalized = _safe_path(file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': 'File saved', 'path': normalized})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
