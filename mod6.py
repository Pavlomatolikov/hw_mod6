import os
import shutil
from pathlib import Path
import re
import string
import sys
import random


IMAGES = ('JPEG', 'PNG', 'JPG', 'SVG', 'BMP')
DOCUMENTS = ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
AUDIO = ('MP3', 'OGG', 'WAV', 'AMR')
VIDEO = ('AVI', 'MP4', 'MOV', 'MKV')
ARCHIVES = ('ZIP', 'GZ', 'TAR')
IGNORE_LIST = ("images", "documents", "audio", "video",
               "archives")
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
DIGITS = "0123456789"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

list_of_items = {"rename": [], "empty_folders": [], "images": [],
                 "documents": [], "audio": [], "video": [], "archives": [], "unknown": []}
list_of_known_items = set()
list_of_unknown_items = set()
sorting_folder_path = ""


def main():
    """
    Скрипт обрабатывает все файлы и папки в указанном каталоге и подкаталогах и нормализирует имена,\
    собирает все файлы с известными разрешениями в соответствующие папки, а так же удаляет пустые папки.
    """
    global sorting_folder_path
    sorting_folder_path = folder_address()
    recursive_scan(sorting_folder_path)
    normalize(list_of_items)
    recursive_scan(sorting_folder_path)
    move_known_files(list_of_items, sorting_folder_path)
    remove_empty_folders(sorting_folder_path)
    unzip_archives(list_of_items, sorting_folder_path)
    print("Done")


def folder_address():
    if len(sys.argv) == 1:
        if input("I'll sort content of current folder, OK?\nEnter 'Y' to continue or 'N' to close me ") in ("Y", "y"):
            return Path()
        else:
            sys.exit()
    elif Path((sys.argv[1])).exists():
        return Path(sys.argv[1])
    else:
        print("Please restart script and specify correct folder address")
        sys.exit()


def recursive_scan(path):
    if path.is_dir() and path.stem not in IGNORE_LIST:
        if next(os.scandir(path), None) == None:
            list_of_items['empty_folders'].append(path)
        if re.search(r'(?i)[^{}{}_]'.format(string.ascii_letters, string.digits), path.stem) and path != Path(sorting_folder_path):
            list_of_items['rename'].append(path)
        for element in path.iterdir():
            recursive_scan(element)
    else:
        if re.search(r'(?i)[^{}{}_]'.format(string.ascii_letters, string.digits), path.stem):
            list_of_items['rename'].append(path)
        if path.suffix.upper()[1::] in IMAGES:
            list_of_items['images'].append(path)
            list_of_known_items.add(path.suffix.upper()[1::])
        elif path.suffix.upper()[1::] in DOCUMENTS:
            list_of_items['documents'].append(path)
            list_of_known_items.add(path.suffix.upper()[1::])
        elif path.suffix.upper()[1::] in AUDIO:
            list_of_items['audio'].append(path)
            list_of_known_items.add(path.suffix.upper()[1::])
        elif path.suffix.upper()[1::] in VIDEO:
            list_of_items['video'].append(path)
            list_of_known_items.add(path.suffix.upper()[1::])
        elif path.suffix.upper()[1::] in ARCHIVES:
            list_of_items['archives'].append(path)
            list_of_known_items.add(path.suffix.upper()[1::])
        else:
            list_of_items['unknown'].append(path)
            list_of_unknown_items.add(path.suffix.upper()[1::])


def remove_empty_folders(path):
    for d in os.listdir(path):
        a = os.path.join(path, d)
        if os.path.isdir(a):
            remove_empty_folders(a)
            if not os.listdir(a):
                os.rmdir(a)
                print(a, 'удалена')


def move_known_files(files_list, parent_folder):
    for key, value in files_list.items():
        if key not in ("empty_folders", "archives", "unknown", "rename"):
            if value:
                target_folder = Path(
                    os.path.join(parent_folder, key))
                if not target_folder.exists():
                    os.mkdir(target_folder)
                for i in value:
                    try:
                        shutil.move(i, target_folder)
                    except shutil.Error:
                        target_folder = Path(os.path.join(
                            target_folder, i.stem + str(random.randint(1, 100)) + i.suffix))
                        shutil.move(i, target_folder)


def unzip_archives(files_list, parent_folder):
    for key, value in files_list.items():
        if key in ("archives"):
            if value:
                target_folder = Path(
                    os.path.join(parent_folder, key))
                if not target_folder.exists():
                    os.mkdir(target_folder)
                for i in value:
                    target_folder = Path(
                        os.path.join(target_folder, i.stem))
                    shutil.unpack_archive(i, target_folder)
                    os.remove(i)


def normalize(files_list):
    TRANS = {}
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()

        def rename(old_name):
            transliterated = old_name.stem.translate(TRANS)
            normalized_name = re.sub(r'(?i)[^{}{}]'.format(
                string.ascii_letters, string.digits), "_", transliterated)
            new_path = Path(
                str(re.sub(r'{}'.format(old_name.stem), normalized_name, str(old_name))))
            os.rename(old_name, new_path)
    for i in files_list['rename']:
        if not i.is_dir():
            rename(i)
    for i in files_list['rename']:
        if i.is_dir():
            rename(i)
    for value in files_list.values():
        value.clear()


if __name__ == "__main__":
    main()
