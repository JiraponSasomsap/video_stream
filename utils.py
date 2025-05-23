from pathlib import Path

def version():
    v = Path(__file__).parent / "VERSION"
    return v.read_text().strip()