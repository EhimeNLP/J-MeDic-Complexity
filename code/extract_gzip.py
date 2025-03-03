import gzip
import shutil
from pathlib import Path
import os

def extract_gzip_files(folder):
    path = Path(folder)

    for gz_file in path.glob("*.gz"):
        output_file = path / gz_file.stem

        with gzip.open(gz_file, "rb") as f_in, open(output_file, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

def main():
    cwd = os.getcwd()
    extract_gzip_files(os.path.join(cwd, "../data"))

if __name__ == "__main__":
    main()
