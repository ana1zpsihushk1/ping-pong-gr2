import json
import os
from datetime import datetime

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
ALPHABET_SET = set(ALPHABET)
ALPHABET_LEN = len(ALPHABET)
INPUT_LEN = 16

TO_CLIENT_FIFO = "to_client.fifo"
TO_SERVER_FIFO = "to_server.fifo"

def validate_request(input_string):
    # Возвращаем: Статус (True/False), Сообщение об ошибке, Текст, Сдвиг.
    if not isinstance(input_string, str):
        return False, "Input must be a string.", None, None
    if len(input_string) != INPUT_LEN:
        return False, f"Invalid length: {len(input_string)}, expected 16.", None, None

    text = input_string[:(INPUT_LEN-1)]
    shift_char = input_string[INPUT_LEN-1]

    if not shift_char.isdigit():
        return False, "Last symbol must be a digit (0-9)", None, None

    shift = int(shift_char)

    for symbol in text:
        if symbol not in ALPHABET_SET:
            return False, f"Invalid character. Symbol '{symbol}' is not in ALPHABET.", None, None

    return True, None, text, shift

def caesar_encode(text, shift):
    result = []
    for symbol in text:
        if symbol in ALPHABET_SET:
            index = ALPHABET.index(symbol)
            new_index = (index + shift) % ALPHABET_LEN
            result.append(ALPHABET[new_index])
        else:
            #Перестраховка. Валидация должна пресечь эту ситуацию.
            result.append(symbol)
    return ''.join(result)

def log_message(sender, message, log_file: str = "session.log"):
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] [{sender}] {message}\n")

def main():
    for fifo in [TO_CLIENT_FIFO, TO_SERVER_FIFO]:
        if not os.path.exists(fifo):
            os.mkfifo(fifo)
    log_message("SERVER", "Started. Waiting for requests...")
    try:
        while True:
            with open(TO_SERVER_FIFO, "r") as f:
                line = f.readline().strip()
                if not line:
                    continue
            log_message("SERVER", f"Received request: '{line}'")
            is_valid, error, text, shift = validate_request(line)
            if not is_valid:
                response = {
                    "status": "error",
                    "message": error
                }
                log_message("SERVER", f"Validation failed: {error}")
            else:
                encoded = caesar_encode(text, shift)
                response = {
                    "status": "ok",
                    "encoded": encoded
                }
                log_message("SERVER", f"Encoded '{text}' with shift {shift}: '{encoded}'")

            try:
                with open(TO_CLIENT_FIFO, "w") as f:
                    f.write(json.dumps(response) + "\n")
            except BrokenPipeError:
                log_message("SERVER", "Client disconnected unexpectedly")

    except KeyboardInterrupt:
        log_message("SERVER", "Server stopped.")


if __name__ == "__main__":
    main()
