import argparse
import sys
import os


class VFSEmulator:
    def __init__(self, vfs_path, script_path, username="user"):
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.username = username
        self.current_dir = "/"

    def get_prompt(self):
        return f"{self.username}@vfs:{self.current_dir}> "

    def execute_command(self, cmd_line):
        """Выполнение одной команды эмулятора"""
        cmd_line = cmd_line.strip()
        if not cmd_line or cmd_line.startswith("#"):
            return True  # Пропускаем пустые строки и комментарии

        # Требование: вывод в формате "ввод и вывод" (имитация диалога)
        print(f"{self.get_prompt()}{cmd_line}")
        parts = cmd_line.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            print("Завершение работы эмулятора.")
            return False
        elif cmd == "ls":
            print("[stub] Вывод содержимого директории (будет реализован на след. этапе)")
        elif cmd == "cd":
            target = args[0] if args else ""
            print(f"[stub] Переход в директорию: {target} (будет реализован на след. этапе)")
        else:
            # Требование: сообщение об ошибке во время исполнения скрипта
            print(f"Ошибка: неизвестная команда '{cmd}'")
            return False  # Требование: остановка при первой ошибке

        return True

    def run_script(self):
        """Выполнение команд из стартового скрипта"""
        if not self.script_path:
            return

        if not os.path.exists(self.script_path):
            print(f"Ошибка: Стартовый скрипт '{self.script_path}' не найден.")
            sys.exit(1)

        print(f"--- Начало выполнения скрипта: {self.script_path} ---")
        try:
            with open(self.script_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not self.execute_command(line):
                        print(f"Прерывание скрипта из-за ошибки/команды exit.")
                        sys.exit(1)
        except Exception as e:
            print(f"Ошибка при чтении скрипта: {e}")
            sys.exit(1)
        print("--- Конец выполнения скрипта ---")

    def run_interactive(self):
        """Интерактивный режим REPL"""
        while True:
            try:
                command_input = input(self.get_prompt()).strip()
                if not command_input:
                    continue

                if not self.execute_command(command_input):
                    break

            except (KeyboardInterrupt, EOFError):
                print("\nЗавершение работы эмулятора.")
                break


def main():
    parser = argparse.ArgumentParser(description="VFS Shell Emulator - Stage 2 (Configuration)")

    # Требование 1: Параметры командной строки (путь к VFS и путь к стартовому скрипту)
    parser.add_argument("--vfs", type=str, required=True, help="Путь к физическому расположению VFS")
    parser.add_argument("--script", type=str, default="", help="Путь к стартовому скрипту")
    parser.add_argument("--user", type=str, default="user", help="Имя пользователя для приглашения")

    args = parser.parse_args()

    # Требование 1: Отладочный вывод всех заданных параметров при запуске
    print("=== [DEBUG] Заданные параметры эмулятора ===")
    print(f"  Путь к VFS          : {args.vfs}")
    print(f"  Путь к скрипту      : {args.script if args.script else 'Не задан'}")
    print(f"  Имя пользователя    : {args.user}")
    print("===========================================")

    emulator = VFSEmulator(vfs_path=args.vfs, script_path=args.script, username=args.user)

    # Если передан стартовый скрипт — выполняем его
    if args.script:
        emulator.run_script()

    # Запуск интерактивного режима
    emulator.run_interactive()


if __name__ == "__main__":
    main()