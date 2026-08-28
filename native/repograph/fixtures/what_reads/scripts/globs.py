from pathlib import Path


Path(".").glob("scripts/*.py")
Path(".").glob("data/nested/*.fixture.json")
Path(".").glob("data/*fixture.json")
Path(".").glob("*.json")
Path("data/nested").glob("*.fixture.json")
