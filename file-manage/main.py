import os
import sys
import time
import shutil

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source_dirs = ["/Users/soso/Downloads", "/Users/soso/Desktop"]

dest_dir_image = "/Users/soso/Downloads Images"
dest_dir_video = "/Users/soso/Downloads Videos"
dest_dir_audio = "/Users/soso/Downloads Audios"
dest_dir_document = "/Users/soso/Downloads Documents"

image_extensions = [
    ".jpg",
    ".jpeg",
    ".jpe",
    ".jif",
    ".jfif",
    ".jfi",
    ".png",
    ".gif",
    ".webp",
    ".tiff",
    ".tif",
    ".psd",
    ".raw",
    ".arw",
    ".cr2",
    ".nrw",
    ".k25",
    ".bmp",
    ".dib",
    ".heif",
    ".heic",
    ".ind",
    ".indd",
    ".indt",
    ".jp2",
    ".j2k",
    ".jpf",
    ".jpf",
    ".jpx",
    ".jpm",
    ".mj2",
    ".svg",
    ".svgz",
    ".ai",
    ".eps",
    ".ico",
]

video_extensions = [
    ".webm",
    ".mpg",
    ".mp2",
    ".mpeg",
    ".mpe",
    ".mpv",
    ".ogg",
    ".mp4",
    ".mp4v",
    ".m4v",
    ".avi",
    ".wmv",
    ".mov",
    ".qt",
    ".flv",
    ".swf",
    ".avchd",
]

audio_extensions = [
    ".m4a",
    ".flac",
    "mp3",
    ".wav",
    ".wma",
    ".aac",
]

document_extensions = [
    ".doc",
    ".docx",
    ".odt",
    ".pdf",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
]


def make_unique(dest, name):
    counter = 1
    filename, extension = os.path.splitext(name)
    print(filename, extension)
    while True:
        new_name = f"{filename}_{counter}{extension}"
        if not os.path.exists(f"{dest}/{new_name}"):
            return new_name
        counter += 1


def move_file(dest, entry, name):
    file_exists = os.path.exists(f"{dest}/{name}")
    if file_exists:
        unique_name = make_unique(dest, name)
        shutil.move(entry, f"{dest}/{unique_name}")
    else:
        shutil.move(entry, f"{dest}/{name}")


class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print()
        for source_dir in source_dirs:
            with os.scandir(source_dir) as entries:
                for entry in entries:
                    print(entry.name)
                    name = entry.name
                    dest = source_dir

                    if self.check_image_file(entry, name):
                        print("\n=========== Move Image ===========")
                        dest = dest_dir_image
                        move_file(dest, entry, name)

                    if self.check_video_file(entry, name):
                        print("\n=========== Move Video ===========")
                        dest = dest_dir_video
                        move_file(dest, entry, name)

                    if self.check_audio_file(entry, name):
                        print("\n=========== Move Video ===========")
                        dest = dest_dir_audio
                        move_file(dest, entry, name)

                    if self.check_document_file(entry, name):
                        print("\n=========== Move Document ===========")
                        dest = dest_dir_document
                        move_file(dest, entry, name)

    def check_image_file(self, entry, name):
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                return True
        return False

    def check_video_file(self, entry, name):
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                return True
        return False

    def check_audio_file(self, entry, name):
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                return True
        return False

    def check_document_file(self, entry, name):
        for document_extension in document_extensions:
            if name.endswith(document_extension) or name.endswith(
                document_extension.upper()
            ):
                return True
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    observers = []
    event_handler = MoverHandler()

    for path in source_dirs:
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        observers.append(observer)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
