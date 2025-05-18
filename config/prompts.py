from dataclasses import dataclass
from pathlib import Path
import os, yaml

ROOT = Path(__file__).resolve().parents[1]  

@dataclass(frozen=True)
class Prompts:
    route: Path
    filter: Path
    rank: Path
    consolidate: Path

    @staticmethod
    def from_yaml(path_file: Path) -> "Prompts":

        data = yaml.safe_load(path_file.read_text())
        paths = Prompts(**{k: (ROOT / v).resolve() for k, v in data.items()})

        return paths

PROMPTS = Prompts.from_yaml(ROOT / "config" / "prompts.yaml")
