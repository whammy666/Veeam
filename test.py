import os
import hashlib
import shutil
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync.log"),
        logging.StreamHandler()
    ]
)

def hash_calculator(file_path):
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(4096):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def all_files_hash_calculator(folder_path):
    files_hashes = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            files_hashes[relative_path] = hash_calculator(file_path)
    return files_hashes


def synchro_folders(main, clone):
    main_hashes = all_files_hash_calculator(main)
    clone_hashes = all_files_hash_calculator(clone)

    for relative_path, source_hash in main_hashes.items():
        main_file_path = os.path.join(main, relative_path)
        clone_file_path = os.path.join(clone, relative_path)

        if relative_path not in clone:
            os.makedirs(os.path.dirname(clone_file_path), exist_ok=True)
            shutil.copy2(main_file_path, clone_file_path)
            logging.info(f"Copied: {main_file_path} to {clone_file_path}")
        elif clone_hashes[relative_path] != source_hash:
            shutil.copy2(main_file_path, clone_file_path)
            logging.info(f"Updated: {clone_file_path}")

    for relative_path in clone_hashes.keys():
        if relative_path not in main_hashes:
            clone_file_path = os.path.join(clone, relative_path)
            os.remove(clone_file_path)
            logging.info(f"Deleted: {clone_file_path}")


main = "main_folder"
clone = "clone_folder"

while True:
    synchro_folders(main, clone)
    time.sleep(900)
