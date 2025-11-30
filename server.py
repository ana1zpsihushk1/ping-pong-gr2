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
    if not isinstance(input_string, str):
        return False, "Input must be a string.", None, None
    if len(input_string) != INPUT_LEN:
        return False, f"Invalid length: {len(input_string)}, expected 16.", None, None

    text = input_string[:15]
    shift_char = input_string[15]

    if not shift_char.isdigit():
        return False, "Last symbol must be a digit (0-9)", None, None

    shift = int(shift_char)

    for s in text:
        if s not in ALPHABET_SET:
            return False, f"Invalid character: '{s}'", None, None

    return True, None, text, shift


def caesar_encode(text, shift):
    result = []
    for symbol in text:
        idx = ALPHABET.index(symbol)
        new_idx = (idx + shift) % ALPHABET_LEN
        result.append(ALPHABET[new_idx])
    return ''.join(result)


def log_message(sender, message, log_file="session.log"):
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] [{sender}] {message}\n")


def main():
    for fifo in [TO_CLIENT_FIFO, TO_SERVER_FIFO]:
        if not os.path.exists(fifo):
            os.mkfifo(fifo)

    log_message("SERVER", "Started. Waiting for requests...")

    while True:
        with open(TO_SERVER_FIFO, "r") as fr:
            line = fr.readline().strip()

        if not line:
            continue

        log_message("SERVER", f"Received: {line}")

        is_valid, error, text, shift = validate_request(line)

        if not is_valid:
            response = {"status": "error", "message": error}
        else:
            encoded = caesar_encode(text, shift)
            response = {"status": "ok", "encoded": encoded}

        with open(TO_CLIENT_FIFO, "w") as fw:
            fw.write(json.dumps(response) + "\n")

        log_message("SERVER", f"Responded: {response}")


if __name__ == "__main__":
    main()
