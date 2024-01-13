from pathlib import Path


def create_directory(directory_path: Path):
    """
    Create a directory if it does not exist.

    Parameters:
    - directory_path (Path): The path to the directory.
    """
    if not directory_path.is_dir():
        directory_path.mkdir(parents=True, exist_ok=True)
