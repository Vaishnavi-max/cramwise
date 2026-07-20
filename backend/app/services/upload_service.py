from pathlib import Path
import shutil


class UploadService:

    def save_file(self, file, destination: Path):
        destination.parent.mkdir(parents=True, exist_ok=True)

        with open(destination, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return destination