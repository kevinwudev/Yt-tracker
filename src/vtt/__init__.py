from pathlib import Path

__version__ = "0.1.0"

src_path = Path(__file__).resolve().parent
root_path = src_path.parent.parent
data_path = root_path / "data"

