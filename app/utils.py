import tomllib
import os


def get_version() -> str:
    """Get version from pyproject.toml file."""
    try:
        # Get the project root directory (parent of app directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        pyproject_path = os.path.join(project_root, "pyproject.toml")

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data.get("project", {}).get("version", "0.1.0")
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        # Fallback version if file is not found or version is not in file
        return "0.1.0"
