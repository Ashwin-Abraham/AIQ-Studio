"""Paths for tests of the packaged Rhino site model."""

from pathlib import Path


SCRIPTS_PATH = (
    Path(__file__).resolve().parents[2]
    / "plugins"
    / "aiq-site-tools"
    / "skills"
    / "rhino-site-data-model"
    / "scripts"
)
