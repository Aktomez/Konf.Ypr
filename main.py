import argparse
import zipfile
import os
import time


class VFSEmulator:
    def __init__(self, vfs_path, script_path, username):
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.username = username

        self.virtual_fs = set()
        self.permissions = {}  # Словарь для хранения прав в памяти (chmod)
        self.current_dir = "/"
        self.start_time = time.time()

        self.load_vfs()

    def load_vfs(self):
        """Загрузка структуры zip-архива"""
        try:
            self.virtual_fs = set()
            with zipfile.ZipFile(self.vfs_path, 'r') as archive:
                for filename in archive.namelist():
                    norm_path = "/" + filename.strip("/")
                    self.virtual_fs.add(norm_path)
                    # Устанавливаем права по умолчанию (например, 755), если их еще нет
                    if norm_path not in self.permissions:
                        self.permissions[norm_path] = "755"
            print(f"[VFS] Успешно загружено объектов: {len(self.virtual_fs)}")
        except FileNotFoundError:
            print(f"[VFS Error] Архив '{self.vfs_path}' не найден!")
        except zipfile.BadZipFile:
            print(f"[VFS Error] Файл '{self.vfs_path}' поврежден или не является zip-архивом.")

    def _get_absolute_path(self, path):
        """Превращает относительный путь в абсолютный с учетом current_dir"""
        if not path or path == ".":
            return self.current_dir
        if path == "..":
            parts = [p for p in self.current_dir.split("/") if p]
            if parts:
                parts.pop()
            return "/" + "/".join(parts)
        if path.startswith("/"):
            parts = [p for p in path.split("/") if p]
            return "/" + "/".join(parts)
        else:
            base = self.current_dir.rstrip("/")
            combined = f"{base}/{path}"
            parts = [p for p in combined.split("/") if p]
            return "/" + "/".join(parts)

    def cmd_ls(self):
        """Вывод содержимого текущей директории"""
        current = self.current_dir.rstrip("/") + "/"
        items = set()

        for path in self.virtual_fs:
            if path == self.current_dir or path == "/":
                continue
            if path.startswith(current):
                rel = path[len(current):]
                first_part = rel.split("/")[0]
                if first_part:
                    items.add(first_part)

        for item in sorted(items):
            print(item)

    def cmd_cd(self, args):
        """Смена текущей директории"""
        if not args:
            self.current_dir = "/"
            return

        target = args[0]
        new_path = self._get_absolute_path(target)

        if new_path == "/" or any(p.startswith(new_path.rstrip("/") + "/") for p in self.virtual_fs):
            self.current_dir = new_path if new_path.endswith("/") else new_path + "/"
        else:
            print(f"cd: нет такой директории: {target}")

    def cmd_tree(self):
        """Вывод дерева каталогов"""
        print(self.current_dir)
        base = self.current_dir.rstrip("/")

        for path in sorted(self.virtual_fs):
            if path == "/":
                continue
            if path.startswith(base if base == "/" else base + "/"):
                rel = path[len(base):].lstrip("/")
                if not rel:
                    continue
                parts = rel.split("/")
                indent = "    " * (len(parts) - 1)
                print(f"{indent}{parts[-1]}")

    def cmd_uptime(self):
        """Время работы эмулятора"""
        elapsed = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed, 60)
        print(f"Эмулятор запущен: {minutes} мин. {seconds} сек. назад.")

    def cmd_whoami(self):
        """Имя текущего пользователя"""
        print(self.username)

    def cmd_chmod(self, args):
        """Изменение прав доступа к файлу/директории (в памяти)"""
        if len(args) < 2:
            print("chmod: пропущены аргументы. Использование: chmod <режим> <путь>")
            return

        mode = args[0]
        target = args[1]
        abs_path = self._get_absolute_path(target)

        # Проверяем существование файла или папки в виртуальной системе
        exists = (
            abs_path in self.virtual_fs or
            abs_path.rstrip("/") in self.virtual_fs or
            any(p.startswith(abs_path.rstrip("/") + "/") for p in self.virtual_fs)
        )

        if abs_path == "/" or exists:
            self.permissions[abs_path] = mode
            print(f"Права для '{target}' успешно изменены на {mode}")
        else:
            print(f"chmod: нет такого файла или директории: {target}")

    def cmd_vfs_load(self, args):
        """Загрузка нового VFS архива с диска"""
        if not args:
            print("vfs-load: не указан путь к архиву")
            return

        new_path = args[0]
        if os.path.exists(new_path):
            self.vfs_path = new_path
            self.load_vfs()
            self.current_dir = "/"  # Сброс в корень при смене файловой системы
        else:
            print(f"vfs-load: архив не найден: {new_path}")

    def execute_command(self, command_line):
        parts = command_line.split()
        if not parts:
            return True

        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            print("Завершение работы эмулятора.")
            return False
        elif cmd == "ls":
            self.cmd_ls()
        elif cmd == "cd":
            self.cmd_cd(args)
        elif cmd == "tree":
            self.cmd_tree()
        elif cmd == "uptime":
            self.cmd_uptime()
        elif cmd == "whoami":
            self.cmd_whoami()
        elif cmd == "chmod":
            self.cmd_chmod(args)
        elif cmd == "vfs-load":
            self.cmd_vfs_load(args)
        else:
            print(f"Неизвестная команда: {cmd}")
        return True

    def run_interactive(self):
        print(f"Добро пожаловать, {self.username}! Введите 'exit' для выхода.")
        while True:
            try:
                prompt_dir = self.current_dir
                command = input(f"{self.username}@vfs:{prompt_dir}$ ").strip()
                if not command:
                    continue

                if not self.execute_command(command):
                    break
            except EOFError:
                break

    def run_script(self):
        if self.script_path and os.path.exists(self.script_path):
            print(f"--- Начало выполнения скрипта: {self.script_path} ---")
            with open(self.script_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_str = line.strip()
                    if not line_str or line_str.startswith("#"):
                        continue
                    print(f"{self.username}@vfs:{self.current_dir}$ {line_str}")
                    if not self.execute_command(line_str):
                        break
            print("--- Конец выполнения скрипта ---")


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