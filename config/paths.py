from dataclasses import dataclass
from pathlib import Path
import os, yaml

ROOT = Path(__file__).resolve().parents[1]  

@dataclass(frozen=True)
class Paths:
    info: Path
    menu: Path
    reviews: Path

    @staticmethod
    def from_yaml(path_file: Path) -> "Paths":

        data = yaml.safe_load(path_file.read_text())
        paths = Paths(**{k: (ROOT / v).resolve() for k, v in data.items()})

        return paths

# instantiate once – module-level singleton
PATHS = Paths.from_yaml(ROOT / "config" / "paths.yaml")
