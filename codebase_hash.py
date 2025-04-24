import hashlib
import os
from pathlib import Path
from typing import Iterable


def generate_folder_hash(base_path: Path, ignore_dirs: Iterable | None = None, verbose: int = 0):
    if ignore_dirs is None:
        ignore_dirs = []
    hash_obj = hashlib.sha256()
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file_name in sorted(files):
            file_path = os.path.join(root, file_name)
            if verbose != 0:
                print(file_path)
            with open(file_path, 'rb') as file:
                while chunk := file.read(8192):
                    hash_obj.update(chunk)
    return hash_obj.hexdigest()


if __name__ == '__main__':
    ignore = {'.idea', '.git', '.venv', 'meta', '__pycache__', 'demos'}
    project_path = Path(__file__).parent
    total_hash = generate_folder_hash(project_path, ignore, verbose=1)
    print(f"Project hash: {total_hash}")