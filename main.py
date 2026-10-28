import argparse
import zipfile
import os


class VFSEmulator:
    def __init__(self, vfs_path, script_path, username):
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.username = username

        self.virtual_fs = {}
        self.current_dir = "/"

        self.load_vfs()

    def load_vfs(self):
        """Загрузка zip-архива в оперативную память"""
        try:
            with zipfile.ZipFile(self.vfs_path, 'r') as archive:
                for filename in archive.namelist():
                    self.virtual_fs[filename] = archive.read(filename)
            print(f"[VFS] Успешно загружено файлов: {len(self.virtual_fs)}")
        except FileNotFoundError:
            print(f"[VFS Error] Архив '{self.vfs_path}' не найден!")
        except zipfile.BadZipFile:
            print(f"[VFS Error] Файл '{self.vfs_path}' поврежден или не является zip-архивом.")

    def run_interactive(self):
        print(f"Добро пожаловать, {self.username}! Введите 'exit' для выхода.")
        while True:
            try:
                command = input(f"{self.username}@vfs:{self.current_dir}$ ").strip()
                if not command:
                    continue

                parts = command.split()
                cmd = parts[0]
                args = parts[1:]

                if cmd == "exit":
                    print("Завершение работы эмулятора.")
                    break
                elif cmd == "ls":
                    print("Содержимое виртуальной файловой системы:")
                    for path in self.virtual_fs.keys():
                        print(f"  {path}")
                elif cmd == "cd":
                    if args:
                        self.current_dir = f"/{args[0]}"
                        print(f"Переход в директорию: {self.current_dir}")
                    else:
                        print("cd: укажите директорию")
                else:
                    print(f"Неизвестная команда: {cmd}")
            except EOFError:
                break

    def run_script(self):
        # Заглушка для выполнения скрипта, если он есть
        if self.script_path and os.path.exists(self.script_path):
            with open(self.script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    print(f"> {line.strip()}")


def main():
    parser = argparse.ArgumentParser(description="VFS Emulator")
    parser.add_argument('--vfs', type=str, default='vfs.zip', help='Путь к vfs.zip')
    parser.add_argument('--script', type=str, default=None, help='Путь к скрипту')
    parser.add_argument('--user', type=str, default='Artem', help='Имя пользователя')

    args = parser.parse_args()

    emulator = VFSEmulator(vfs_path=args.vfs, script_path=args.script, username=args.user)

    if args.script:
        emulator.run_script()

    emulator.run_interactive()


if __name__ == "__main__":
    main()