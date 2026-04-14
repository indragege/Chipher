from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Caesar Cipher
def caesar_cipher(text, shift, mode):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            if mode == 'encode':
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += chr((ord(char) - base - shift) % 26 + base)
        else:
            result += char
    return result


def caesar_steps(text, shift, mode):
    lines = []
    direction = 'encode' if mode == 'encode' else 'decode'
    shift_value = shift if mode == 'encode' else -shift
    lines.append(f"Caesar cipher {direction} with shift = {shift}.")
    lines.append(f"Shift direction: {shift_value}.")

    count = 0
    for index, char in enumerate(text):
        if count >= 10:
            break
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            original_pos = ord(char.upper()) - ord('A')
            shifted = (original_pos + shift_value) % 26
            target = chr(shifted + base)
            lines.append(f"[{count + 1}] '{char}' (pos {original_pos}) -> '{target}' (pos {shifted})")
            count += 1
    if count == 0:
        lines.append('No alphabetic characters to process.')
    elif len([c for c in text if c.isalpha()]) > 10:
        lines.append('...more letters are processed with the same rule.')
    return lines


def caesar_bruteforce(text):
    candidates = []
    for s in range(1, 26):
        decoded = caesar_cipher(text, s, 'decode')
        candidates.append({'shift': s, 'result': decoded})
    return candidates


# Vigenère Cipher
def vigenere_cipher(text, key, mode):
    key_shifts = [ord(k.upper()) - ord('A') for k in key if k.isalpha()]
    if not key_shifts:
        return text

    result = ""
    key_index = 0
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = key_shifts[key_index % len(key_shifts)]
            if mode == 'encode':
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += chr((ord(char) - base - shift) % 26 + base)
            key_index += 1
        else:
            result += char
    return result


def vigenere_steps(text, key, mode):
    key_shifts = [ord(k.upper()) - ord('A') for k in key if k.isalpha()]
    if not key_shifts:
        return ['Key does not contain letters.']

    repeated = []
    letter_count = 0
    for char in text:
        if char.isalpha():
            repeated.append(key[letter_count % len(key)])
            letter_count += 1
        else:
            repeated.append(char)
    repeated_key = ''.join(repeated)

    lines = [f"Vigenère {mode} using key '{key}'.", 'Non-letter characters are preserved.']
    lines.append(f"Key pattern for first letters: {''.join(repeated_key[:min(10, len(repeated_key))])}")

    count = 0
    key_index = 0
    for char in text:
        if count >= 8:
            break
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            original_pos = ord(char.upper()) - ord('A')
            shift = key_shifts[key_index % len(key_shifts)]
            if mode == 'encode':
                result_pos = (original_pos + shift) % 26
            else:
                result_pos = (original_pos - shift) % 26
            result_char = chr(result_pos + base)
            key_char = key[key_index % len(key)]
            lines.append(f"[{count + 1}] '{char}' with key '{key_char}' -> '{result_char}'")
            key_index += 1
            count += 1
    if count == 0:
        lines.append('No alphabetic characters to process.')
    elif len([c for c in text if c.isalpha()]) > 8:
        lines.append('...more letters are processed in the same repeating key pattern.')
    return lines


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json() or {}
    cipher = data.get('cipher')
    mode = data.get('mode', 'encode')
    text = data.get('text', '')
    params = data.get('params', {})

    try:
        if cipher == 'caesar':
            shift = int(params.get('shift', 3))
            result = caesar_cipher(text, shift, mode)
            steps = caesar_steps(text, shift, mode)
            brute_force = caesar_bruteforce(text) if mode == 'decode' else []
        elif cipher == 'vigenere':
            key = params.get('key', 'KEY').strip() or 'KEY'
            result = vigenere_cipher(text, key, mode)
            steps = vigenere_steps(text, key, mode)
            brute_force = []
        else:
            result = 'Unknown cipher'
            steps = []
            brute_force = []

        return jsonify({
            'result': result,
            'steps': steps,
            'brute_force': brute_force,
            'input_chars': len(text),
            'output_chars': len(result)
        })
    except Exception as e:
        return jsonify({'error': 'Invalid input or parameters', 'details': str(e)})

if __name__ == '__main__':
    app.run(debug=True)