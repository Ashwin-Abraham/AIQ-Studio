"""Report requirements for the AIQ Rhino site model workflow."""

import importlib.metadata
import importlib.util
import json
import platform
import sys


PACKAGES = ("rhino3dm", "shapely", "pyproj", "overturemaps")


def main() -> int:
    packages = {}
    for package in PACKAGES:
        found = importlib.util.find_spec(package) is not None
        try:
            version = importlib.metadata.version(package) if found else None
        except importlib.metadata.PackageNotFoundError:
            version = "installed"
        packages[package] = {"available": found, "version": version}
    report = {
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "operating_system": platform.system(),
        "packages": packages,
        "rhino_8": "Confirm that Rhino 8 is installed and can open the target model.",
        "vector_authoring": "For native .ai output, confirm an application that can save and check .ai files.",
    }
    print(json.dumps(report, indent=2))
    return 0 if all(item["available"] for item in packages.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
