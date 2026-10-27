import sys
import argparse


def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description="VFS Shell Emulator")
    parser.add_argument("--user", type=str, default="user", help="Username for prompt")
    args = parser.parse_args()

    username = args.user

    # Основной цикл REPL
    while True:
        try:
            # Вывод приглашения к вводу
            command_input = input(f"{username}@vfs> ").strip()

            if not command_input:
                continue

            # Команда выхода
            if command_input == "exit":
                print("Завершение работы эмулятора.")
                break

            # Заглушка для обработки других команд
            print(f"Выполнена команда: {command_input}")

        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы эмулятора.")
            break


if __name__ == "__main__":
    main()