import os
import json
import sys

TO_CLIENT_FIFO = "to_client.fifo"
TO_SERVER_FIFO = "to_server.fifo"
INPUT_LEN = 16


def send_request(request):
    with open(TO_SERVER_FIFO, "w") as fw:
        fw.write(request + "\n")

    with open(TO_CLIENT_FIFO, "r") as fr:
        response_line = fr.readline().strip()

    try:
        return json.loads(response_line)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": f"Invalid JSON from server: {response_line}"
        }


def main():
    print("Клиент запущен")
    print("Формат запроса: 15 букв a-z + 1 цифра (0-9)")
    print("Пример: helloabcdeabcde5\n")

    while True:
        user_input = input("Введите запрос: ").strip().lower()

        if user_input == "":
            print("Клиент завершает работу.")
            break

        if len(user_input) != INPUT_LEN:
            print(f"Локальная ошибка: длина должна быть {INPUT_LEN}.", file=sys.stderr)
            continue

        response = send_request(user_input)
        status = response.get("status")

        if status == "ok":
            print(f"Ответ сервера: {response.get('encoded')}")
        else:
            print(f"Ошибка сервера: {response.get('message')}", file=sys.stderr)


if __name__ == "__main__":
    if not os.path.exists(TO_CLIENT_FIFO) or not os.path.exists(TO_SERVER_FIFO):
        print("Ошибка: FIFO не найдены. Запустите через run.sh", file=sys.stderr)
        sys.exit(1)

    main()
