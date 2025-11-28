import os
import json
import sys

TO_CLIENT_FIFO = "to_client.fifo"
TO_SERVER_FIFO = "to_server.fifo"
INPUT_LEN = 16


def send_request(request):
    with open(TO_SERVER_FIFO, "w") as to_server:
        to_server.write(request + "\n")

    with open(TO_CLIENT_FIFO, "r") as to_client:
        response_line = to_client.readline().strip()

    try:
        response = json.loads(response_line)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": f"Invalid JSON from server: {response_line}"
        }

    return response


def main():
    print("Клиент запущен")
    print("Формат запроса: 15 латинских букв (a-z) + 1 цифра (0-9)")
    print("Пример: hello54321abcde9f")
    print("Чтобы выйти, введите пустую строку")
    print()

    while True:
        user_input = input("Введите запрос: ").strip().lower()

        if user_input == "":
            print("Клиент завершает работу.")
            break

        if len(user_input) != INPUT_LEN:
            print(f"Локальная ошибка: строка должна быть длиной {INPUT_LEN} символов.", file=sys.stderr)
            continue

        response = send_request(user_input)
        status = response.get("status")

        if status == "ok":
            encoded = response.get("encoded", "")
            print(f"Ответ сервера (закодированная строка): {encoded}")
        elif status == "error":
            message = response.get("message", "Unknown error")
            print(f"Ошибка сервера: {message}", file=sys.stderr)
        else:
            print(f"Неожиданный ответ сервера: {response}", file=sys.stderr)


if __name__ == "__main__":
    if not os.path.exists(TO_CLIENT_FIFO) or not os.path.exists(TO_SERVER_FIFO):
        print("Ошибка: FIFO-файлы не найдены. Убедитесь, что сервер был запущен и создал их.", file=sys.stderr)
        sys.exit(1)

    main()
