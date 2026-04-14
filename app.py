import streamlit as st


def caesar_cipher(text: str, shift: int, mode: str = 'encode') -> str:
    shift %= 26
    if mode == 'decode':
        shift = -shift

    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)


def vigenere_cipher(text: str, key: str, mode: str = 'encode') -> str:
    key = ''.join([c.upper() for c in key if c.isalpha()])
    if not key:
        return text

    result = []
    key_index = 0
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(key[key_index % len(key)]) - ord('A')
            if mode == 'decode':
                shift = -shift
            result.append(chr((ord(char) - base + shift) % 26 + base))
            key_index += 1
        else:
            result.append(char)
    return ''.join(result)


def caesar_steps(text: str, shift: int, mode: str = 'encode') -> list[str]:
    shift %= 26
    if mode == 'decode':
        shift = -shift

    steps = [f"Caesar {mode} with shift {abs(shift)}."]
    for i, char in enumerate(text):
        if i >= 8:
            break
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            transformed = chr((ord(char) - base + shift) % 26 + base)
            steps.append(f"{i + 1}. '{char}' -> '{transformed}'")
        else:
            steps.append(f"{i + 1}. '{char}' preserved")

    if len([c for c in text if c.isalpha()]) > 8:
        steps.append('...more letters are processed using the same shift pattern.')
    return steps


def vigenere_steps(text: str, key: str, mode: str = 'encode') -> list[str]:
    cleaned_key = ''.join([c.upper() for c in key if c.isalpha()])
    if not cleaned_key:
        return ['Please provide a valid alphabetic key.']

    key_shifts = [ord(ch) - ord('A') for ch in cleaned_key]
    steps = [f"Vigenère {mode} using key '{cleaned_key}'."]
    key_index = 0

    for i, char in enumerate(text):
        if i >= 8:
            break
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = key_shifts[key_index % len(key_shifts)]
            if mode == 'decode':
                shift = -shift
            transformed = chr((ord(char) - base + shift) % 26 + base)
            steps.append(
                f"{i + 1}. '{char}' with key '{cleaned_key[key_index % len(cleaned_key)]}' -> '{transformed}'"
            )
            key_index += 1
        else:
            steps.append(f"{i + 1}. '{char}' preserved")

    if sum(c.isalpha() for c in text) > 8:
        steps.append('...more letters are processed in the same repeating key pattern.')
    return steps


def caesar_bruteforce(text: str) -> list[tuple[int, str]]:
    return [(shift, caesar_cipher(text, shift, mode='decode')) for shift in range(1, 26)]


def render_page_style() -> None:
    st.markdown(
        '''
        <style>
        .stApp {
            background: linear-gradient(135deg, #020617 0%, #111827 100%);
            color: #e2e8f0;
        }
        .css-18e3th9 {
            padding-top: 1rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 1rem;
        }
        .stButton > button {
            background-color: #2563eb;
            color: #ffffff;
            border-radius: 0.75rem;
        }
        .stButton > button:hover {
            background-color: #1d4ed8;
        }
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            background-color: #111827;
            color: #e2e8f0;
        }
        .stMarkdown, .stExpanderHeader, .stText, .stCode {
            color: #cbd5e1;
        }
        </style>
        ''',
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title='CipherLab',
        page_icon='🔐',
        layout='wide',
    )
    render_page_style()

    st.markdown('# CipherLab 2.0')
    st.markdown('**Caesar and Vigenère cipher helper with instant encode/decode and walk-through steps.**')

    with st.sidebar:
        st.header('Controls')
        cipher = st.selectbox('Cipher type', ['Caesar Cipher', 'Vigenère Cipher'])
        mode = st.radio('Action', ['Encode', 'Decode'])
        text = st.text_area('Enter your text', value='Type or paste text here...', height=220)

        if cipher == 'Caesar Cipher':
            shift = st.slider('Shift value', 1, 25, 3)
            key = ''
        else:
            shift = 0
            key = st.text_input('Keyword', value='INDRA').strip()
            if not key:
                st.warning('Enter a keyword with letters only for Vigenère.')

        show_steps = st.checkbox('Show step-by-step details', value=True)
        show_bruteforce = st.checkbox('Show brute-force table for Caesar decode', value=False)

    if not text or text.strip() == 'Type or paste text here...':
        st.info('Enter text in the sidebar to start encoding or decoding.')
        return

    current_mode = 'encode' if mode == 'Encode' else 'decode'
    if cipher == 'Caesar Cipher':
        result = caesar_cipher(text, shift, current_mode)
        steps = caesar_steps(text, shift, current_mode)
        brute_force = caesar_bruteforce(text) if current_mode == 'decode' else []
        cipher_info = f'Caesar shift = {shift}. Non-letter characters stay unchanged.'
    else:
        result = vigenere_cipher(text, key, current_mode)
        steps = vigenere_steps(text, key, current_mode)
        brute_force = []
        cipher_info = f"Vigenère key = '{key.upper()}'. Non-letter characters stay unchanged."

    st.markdown('---')
    columns = st.columns([2, 0.25, 2])
    with columns[0]:
        st.subheader('Input')
        st.write(text)
        st.caption(f'Input length: {len(text)} characters')
    with columns[2]:
        st.subheader('Result')
        st.code(result, language='text')
        st.caption(f'Output length: {len(result)} characters')

    st.markdown('---')
    st.markdown(f'**Cipher info:** {cipher_info}')

    if show_steps:
        with st.expander('Step-by-step explanation', expanded=True):
            for step in steps:
                st.write(step)

    if brute_force and show_bruteforce:
        with st.expander('Caesar brute-force candidates', expanded=False):
            st.table(
                [{'Shift': shift, 'Candidate': candidate} for shift, candidate in brute_force]
            )

    with st.expander('How to use this app', expanded=False):
        st.markdown(
            '- Use **Encode** to encrypt and **Decode** to reverse the ciphertext.\n'
            '- For **Caesar**, choose a shift from 1 to 25.\n'
            '- For **Vigenère**, enter a valid keyword with letters only.\n'
            '- Punctuation, spaces, and digits remain unchanged during transformation.'
        )


if __name__ == '__main__':
    main()

