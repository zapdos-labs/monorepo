from __future__ import annotations
import bentoml
from pathlib import Path

# Define the shared directory path relative to the service file
SHARED_DIR = Path(__file__).parent.parent / "shared_data"
SHARED_DIR.mkdir(exist_ok=True) # Ensure the directory exists

@bentoml.service
class SharedDataService:
    """
    A single service that handles both reading and writing to a shared directory.
    """
    @bentoml.api
    def write_data(self, content: str) -> dict:
        file_path = SHARED_DIR / "some_data.txt"
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Successfully wrote to {file_path}")
        return {"status": "success", "path": str(file_path)}

    @bentoml.api
    def read_data(self) -> str:
        file_path = SHARED_DIR / "some_data.txt"
        if not file_path.exists():
            return "File not found. Please call 'write_data' first."
        
        with open(file_path, "r") as f:
            return f.read()