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
from parser import parser, NovaSyntaxError
from lexer import lexer
from interpreter import run, global_env, NovaError, Env, add_builtins
import io
import sys
import os
import json
import re
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import datetime, timezone

app = Flask(__name__, static_folder='.')

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SKIP_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
SIMULATION_LOG_FILE = os.path.join(LOG_DIR, 'simulations.jsonl')


def _load_env_file(env_path):
    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            if key and key not in os.environ:
                os.environ[key] = value


_load_env_file(os.path.join(PROJECT_ROOT, '.env'))

OPENAI_API_URL = os.environ.get('OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_RESPONSE_FORMAT = os.environ.get('OPENAI_RESPONSE_FORMAT', 'auto').strip().lower()
OPENAI_HTTP_REFERER = os.environ.get('OPENAI_HTTP_REFERER', '').strip()
OPENAI_X_TITLE = os.environ.get('OPENAI_X_TITLE', '').strip()
try:
    OPENAI_TIMEOUT_SEC = int(os.environ.get('OPENAI_TIMEOUT_SEC', '60'))
except ValueError:
    OPENAI_TIMEOUT_SEC = 60
try:
    ASSIST_MAX_RETRIES = int(os.environ.get('ASSIST_MAX_RETRIES', '2'))
except ValueError:
    ASSIST_MAX_RETRIES = 2


class LLMSimulationError(Exception):
    pass


def _is_local_ollama_url(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or '').lower()
        port = parsed.port
    except Exception:
        return False
    return host in ('localhost', '127.0.0.1') and port == 11434


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


def _resolve_code_and_path(data):
    if not data:
        raise ValueError('Missing request payload')

    code = data.get('code')
    file_path = data.get('path')
    used_path = None

    if file_path:
        abs_path, used_path = _safe_path(file_path)
        if not os.path.exists(abs_path):
            raise ValueError(f"File not found: {file_path}")
        with open(abs_path, 'r', encoding='utf-8') as f:
            code = f.read()

    if code is None:
        raise ValueError('No code provided')

    return code, used_path


def _normalize_simulation_payload(payload):
    steps = payload.get('steps')
    if not isinstance(steps, list):
        steps = []

    final_output = payload.get('final_output', '')
    if final_output is None:
        final_output = ''
    final_output = str(final_output)

    error = payload.get('error')
    if error is not None:
        error = str(error)

    normalized_steps = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        normalized_steps.append({
            'line': step.get('line'),
            'statement': str(step.get('statement', '')).strip(),
            'note': str(step.get('note', '')).strip(),
            'output': str(step.get('output', '')).strip(),
        })

    derived_final_output = '\n'.join(step['output'] for step in normalized_steps if step.get('output'))
    if derived_final_output:
        if not final_output or _normalize_text_for_compare(final_output) != _normalize_text_for_compare(derived_final_output):
            final_output = derived_final_output

    return {
        'steps': normalized_steps,
        'final_output': final_output,
        'error': error,
    }


def _extract_json_object(text):
    if not isinstance(text, str):
        raise LLMSimulationError('Model response content is not text.')

    text = text.strip()
    if not text:
        raise LLMSimulationError('Model returned an empty response.')

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise LLMSimulationError('Failed to parse model response as JSON.')


def _call_llm_json(system_prompt, user_prompt):
    api_key = (os.environ.get('OPENAI_API_KEY') or '').strip()
    is_ollama = _is_local_ollama_url(OPENAI_API_URL)
    if api_key.lower() in ('your_key_here', 'changeme', 'replace_me'):
        api_key = ''
    if not api_key and not is_ollama:
        raise LLMSimulationError('Missing OPENAI_API_KEY. Add it to your environment to use LLM simulation.')

    request_payload = {
        'model': OPENAI_MODEL,
        'temperature': 0,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
    }
    if OPENAI_RESPONSE_FORMAT == 'json':
        request_payload['response_format'] = {'type': 'json_object'}
    elif OPENAI_RESPONSE_FORMAT == 'auto' and not is_ollama:
        request_payload['response_format'] = {'type': 'json_object'}
    elif OPENAI_RESPONSE_FORMAT in ('none', 'off', 'false', '0'):
        pass

    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    if OPENAI_HTTP_REFERER:
        headers['HTTP-Referer'] = OPENAI_HTTP_REFERER
    if OPENAI_X_TITLE:
        headers['X-Title'] = OPENAI_X_TITLE

    body = json.dumps(request_payload).encode('utf-8')
    req = urllib.request.Request(
        OPENAI_API_URL,
        data=body,
        method='POST',
        headers=headers,
    )

    try:
        with urllib.request.urlopen(req, timeout=OPENAI_TIMEOUT_SEC) as response:
            raw = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        details = e.read().decode('utf-8', errors='replace')
        raise LLMSimulationError(f'OpenAI API error ({e.code}): {details}')
    except urllib.error.URLError as e:
        raise LLMSimulationError(f'OpenAI network error: {e.reason}')

    try:
        parsed = json.loads(raw)
        content = parsed['choices'][0]['message']['content']
    except Exception:
        raise LLMSimulationError('Failed to read model response payload.')

    if isinstance(content, list):
        content = ''.join(part.get('text', '') for part in content if isinstance(part, dict))

    return _extract_json_object(content)


def _simulate_with_openai(code):
    system_prompt = (
        "You are NOVALANG-SIM, a deterministic NOVALANG execution simulator. "
        "Simulate execution line by line from top to bottom. "
        "If any syntax or runtime error occurs, stop immediately and do not execute remaining lines. "
        "Return only a valid JSON object with exactly these keys: "
        "steps (array), final_output (string), error (string or null). "
        "Each steps item should include: line (number or null), statement (string), note (string), output (string). "
        "Do not include markdown."
    )

    user_prompt = (
        "Simulate this NOVALANG program:\n"
        "```novalang\n"
        f"{code}\n"
        "```"
    )

    simulation = _call_llm_json(system_prompt, user_prompt)

    return _normalize_simulation_payload(simulation)


def _assist_code_with_openai(code, instruction):
    system_prompt = (
        "You are NOVALANG-CODE-ASSISTANT. "
        "Edit NOVALANG source code based on the user instruction. "
        "Return only a JSON object with keys: updated_code (string), summary (string). "
        "Never return markdown.\n"
        "NOVALANG syntax rules:\n"
        "- Variable declaration: let x = 10\n"
        "- Display: display expr\n"
        "- Conditionals: if cond ... else ... end\n"
        "- While loop: while cond ... end\n"
        "- For loop: for i = 1 to 5 ... end\n"
        "- Functions: func name(a, b) ... return ... end\n"
        "- Try/catch: try ... catch ... end\n"
        "- Comments use --\n"
        "- Blocks close with end, not braces.\n"
        "- Preserve unrelated code unless requested.\n"
        "- updated_code must be pure executable NOVALANG source.\n"
        "- Do not include prose lines, numbered lists (like 1.), bullet points, or placeholders like ...\n"
        "- If user asks for a while loop from 1 to N, output MULTI-LINE code with one statement per line."
    )

    user_prompt = (
        "Instruction:\n"
        f"{instruction}\n\n"
        "Current code:\n"
        "```novalang\n"
        f"{code}\n"
        "```"
    )

    attempts = max(1, ASSIST_MAX_RETRIES)
    last_error = None
    last_summary = ''

    for _ in range(attempts):
        payload = _call_llm_json(system_prompt, user_prompt)
        updated_code = payload.get('updated_code')
        summary = str(payload.get('summary', '')).strip()

        if not isinstance(updated_code, str) or not updated_code.strip():
            last_error = 'Model did not return updated_code.'
            user_prompt = (
                "The previous response was invalid because updated_code was missing. "
                "Return valid JSON with updated_code and summary.\n\n"
                "Instruction:\n"
                f"{instruction}\n\n"
                "Current code:\n"
                "```novalang\n"
                f"{code}\n"
                "```"
            )
            continue

        normalized_code = _sanitize_assistant_code(updated_code)
        syntax_error = _validate_novalang_code(normalized_code)
        if syntax_error is None:
            return {
                'updated_code': normalized_code,
                'summary': summary,
            }

        if "at ','" in (syntax_error or ''):
            repaired_code = _repair_top_level_commas(normalized_code)
            repaired_error = _validate_novalang_code(repaired_code)
            if repaired_error is None:
                repaired_summary = summary or 'Applied automatic comma-to-newline repair.'
                return {
                    'updated_code': repaired_code,
                    'summary': repaired_summary,
                }

        last_error = f'Generated NOVALANG syntax error: {syntax_error}'
        last_summary = summary
        user_prompt = (
            "Your previous edited code has NOVALANG syntax errors.\n"
            f"Parser error: {syntax_error}\n"
            "Fix the code while preserving user intent.\n"
            "Return strict NOVALANG source in updated_code only (no numbered lines, no prose).\n\n"
            "Instruction:\n"
            f"{instruction}\n\n"
            "Previous edited code:\n"
            "```novalang\n"
            f"{normalized_code}\n"
            "```"
        )

    raise LLMSimulationError(last_error or f'Unable to produce valid NOVALANG code. {last_summary}')


def _normalize_text_for_compare(text):
    text = '' if text is None else str(text)
    return text.replace('\r\n', '\n').strip()


def _sanitize_assistant_code(code_text):
    if not isinstance(code_text, str):
        return ''

    text = code_text.replace('\r\n', '\n').strip()

    fenced_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", text)
    if fenced_match:
        text = fenced_match.group(1).strip()

    cleaned_lines = []
    for line in text.split('\n'):
        line = re.sub(r'^\s*(?:\d+[.)]\s+|[-*]\s+)', '', line)
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


def _repair_top_level_commas(code_text):
    if not isinstance(code_text, str):
        return ''

    text = code_text.replace('\r\n', '\n')
    chars = []
    depth_paren = 0
    depth_brack = 0
    depth_brace = 0
    in_string = False
    escape = False

    for ch in text:
        if in_string:
            chars.append(ch)
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            chars.append(ch)
            continue

        if ch == '(':
            depth_paren += 1
            chars.append(ch)
            continue
        if ch == ')':
            depth_paren = max(0, depth_paren - 1)
            chars.append(ch)
            continue
        if ch == '[':
            depth_brack += 1
            chars.append(ch)
            continue
        if ch == ']':
            depth_brack = max(0, depth_brack - 1)
            chars.append(ch)
            continue
        if ch == '{':
            depth_brace += 1
            chars.append(ch)
            continue
        if ch == '}':
            depth_brace = max(0, depth_brace - 1)
            chars.append(ch)
            continue

        if ch == ',' and depth_paren == 0 and depth_brack == 0 and depth_brace == 0:
            chars.append('\n')
            continue

        chars.append(ch)

    repaired_lines = [line.strip() for line in ''.join(chars).split('\n')]
    return '\n'.join(line for line in repaired_lines if line).strip()


def _validate_novalang_code(code):
    if not isinstance(code, str):
        return 'Generated code is not text.'
    if not code.strip():
        return 'Generated code is empty.'

    try:
        lexer.lineno = 1
        parser.parse(code, lexer=lexer)
        return None
    except (NovaSyntaxError, SyntaxError) as e:
        return str(e)
    except Exception as e:
        return str(e)


def _execute_real_for_compare(code):
    old_stdout = sys.stdout
    buffer = io.StringIO()
    verification_env = Env()
    add_builtins(verification_env)

    def _blocked_input(prompt=''):
        raise NovaError('input() is not supported during simulation verification')

    verification_env.define_func('input', _blocked_input)

    try:
        sys.stdout = buffer
        lexer.lineno = 1
        ast = parser.parse(code, lexer=lexer)
        run(ast, verification_env)
        return {'output': buffer.getvalue(), 'error': None}
    except (NovaSyntaxError, SyntaxError, NovaError) as e:
        return {'output': buffer.getvalue(), 'error': str(e)}
    except Exception as e:
        return {'output': buffer.getvalue(), 'error': str(e)}
    finally:
        sys.stdout = old_stdout


def _build_consistency_warning(simulation, real_execution):
    sim_error = simulation.get('error')
    real_error = real_execution.get('error')
    sim_output = simulation.get('final_output', '')
    real_output = real_execution.get('output', '')

    warnings = []

    if bool(sim_error) != bool(real_error):
        warnings.append('LLM error presence does not match real execution.')
    elif sim_error and _normalize_text_for_compare(sim_error) != _normalize_text_for_compare(real_error):
        warnings.append('LLM error message differs from real execution.')

    if _normalize_text_for_compare(sim_output) != _normalize_text_for_compare(real_output):
        warnings.append('LLM final output differs from real execution.')

    if warnings:
        return ' '.join(warnings)
    return None


def _format_simulation_output(simulation, real_execution=None):
    lines = ['[LLM Simulation Trace]']
    steps = simulation.get('steps', [])

    if steps:
        for idx, step in enumerate(steps, 1):
            line_no = step.get('line')
            statement = step.get('statement') or '(unknown statement)'
            note = step.get('note')
            step_output = step.get('output')

            if line_no is None:
                lines.append(f'{idx}. {statement}')
            else:
                lines.append(f'{idx}. line {line_no}: {statement}')

            if note:
                lines.append(f'   note: {note}')
            if step_output:
                lines.append(f'   output: {step_output}')
    else:
        lines.append('(No step trace returned)')

    if simulation.get('error'):
        lines.append('')
        lines.append(f"Error: {simulation['error']}")
    else:
        lines.append('')
        lines.append('Error: none')

    final_output = simulation.get('final_output', '')
    lines.append('Final Output:')
    lines.append(final_output if final_output else '(No output)')

    consistency_warning = simulation.get('consistency_warning')
    if consistency_warning:
        lines.append('')
        lines.append(f'Verification Warning: {consistency_warning}')
        if real_execution:
            lines.append('Real Interpreter Error:')
            lines.append(real_execution.get('error') or '(No error)')
            lines.append('Real Interpreter Output:')
            real_output = real_execution.get('output') or ''
            lines.append(real_output if real_output else '(No output)')

    return '\n'.join(lines)


def _record_simulation(record):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(SIMULATION_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')


def _read_recent_simulations(limit=20):
    if not os.path.exists(SIMULATION_LOG_FILE):
        return []

    entries = []
    with open(SIMULATION_LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if limit < 1:
        limit = 1
    return list(reversed(entries[-limit:]))


# ---------------------------
# GUI ROUTE (FRONTEND)
# ---------------------------
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'})


# ---------------------------
# API ROUTE (BACKEND EXECUTION)
# ---------------------------
@app.route('/run', methods=['POST'])
def run_code():
    old_stdout = sys.stdout
    try:
        code, used_path = _resolve_code_and_path(request.get_json())

        # Reset lexer line counter for each parse so syntax errors report correct lines.
        lexer.lineno = 1
        ast = parser.parse(code, lexer=lexer)

        sys.stdout = buffer = io.StringIO()
        execution_env = Env()
        add_builtins(execution_env)
        run(ast, execution_env)
        output = buffer.getvalue()

        return jsonify({'output': output, 'path': used_path})

    except ValueError as e:
        message = str(e)
        status = 404 if message.startswith('File not found:') else 400
        return jsonify({'error': message}), status
    except (NovaSyntaxError, SyntaxError, NovaError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        sys.stdout = old_stdout


@app.route('/simulate', methods=['POST'])
def simulate_code():
    code = None
    used_path = None

    def _record_failure(error_text):
        if code is None:
            return
        try:
            _record_simulation({
                'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                'path': used_path,
                'model': OPENAI_MODEL,
                'code': code,
                'steps': [],
                'final_output': '',
                'error': error_text,
                'status': 'failed',
            })
        except Exception:
            pass

    try:
        code, used_path = _resolve_code_and_path(request.get_json())
        simulation = _normalize_simulation_payload(_simulate_with_openai(code))
        real_execution = _execute_real_for_compare(code)
        consistency_warning = _build_consistency_warning(simulation, real_execution)
        if consistency_warning:
            simulation['consistency_warning'] = consistency_warning

        record = {
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'path': used_path,
            'model': OPENAI_MODEL,
            'code': code,
            'steps': simulation['steps'],
            'final_output': simulation['final_output'],
            'error': simulation['error'],
            'real_output': real_execution['output'],
            'real_error': real_execution['error'],
            'consistency_warning': consistency_warning,
            'status': 'ok',
        }
        _record_simulation(record)

        output = _format_simulation_output(simulation, real_execution)
        log_path = os.path.relpath(SIMULATION_LOG_FILE, PROJECT_ROOT).replace('\\', '/')
        return jsonify({
            'path': used_path,
            'simulation': simulation,
            'output': output,
            'log_path': log_path,
            'model': OPENAI_MODEL,
            'consistency_warning': consistency_warning,
        })

    except ValueError as e:
        message = str(e)
        _record_failure(message)
        status = 404 if message.startswith('File not found:') else 400
        return jsonify({'error': message}), status
    except LLMSimulationError as e:
        message = str(e)
        _record_failure(message)
        status = 400 if message.startswith('Missing OPENAI_API_KEY') else 502
        return jsonify({'error': message}), status
    except Exception as e:
        message = str(e)
        _record_failure(message)
        return jsonify({'error': message}), 500


@app.route('/assist-code', methods=['POST'])
def assist_code():
    try:
        data = request.get_json()
        code, used_path = _resolve_code_and_path(data)
        instruction = (data.get('instruction') if data else '') or ''
        instruction = instruction.strip()
        if not instruction:
            return jsonify({'error': 'Missing instruction'}), 400

        result = _assist_code_with_openai(code, instruction)
        return jsonify({
            'path': used_path,
            'updated_code': result['updated_code'],
            'summary': result['summary'],
            'model': OPENAI_MODEL,
        })

    except ValueError as e:
        message = str(e)
        status = 404 if message.startswith('File not found:') else 400
        return jsonify({'error': message}), status
    except LLMSimulationError as e:
        message = str(e)
        if message.startswith('Missing OPENAI_API_KEY'):
            status = 400
        elif message.startswith('Generated NOVALANG syntax error') or message.startswith('Unable to produce valid NOVALANG code'):
            status = 422
        else:
            status = 502
        return jsonify({'error': message}), status
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    return jsonify({'files': _list_novalang_files()})


@app.route('/api/simulations', methods=['GET'])
def list_simulations():
    try:
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({'error': 'limit must be a number'}), 400
    return jsonify({'items': _read_recent_simulations(limit)})


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
