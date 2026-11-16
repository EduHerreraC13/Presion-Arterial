"""Regression checks for the deployed anthropometry iframe and its assets."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_anthropometry_assets_are_present():
    for name in ("anthropometry.html", "anthropometry-i18n.js"):
        assert (ROOT / name).is_file()


def test_anthropometry_iframe_and_language_script():
    landing = (ROOT / "index.html").read_text(encoding="utf-8")
    module = (ROOT / "anthropometry.html").read_text(encoding="utf-8")
    assert 'src="anthropometry.html"' in landing
    assert '<script src="anthropometry-i18n.js" defer></script>' in module


def test_server_public_assets_include_anthropometry():
    src = (ROOT / "servidor_camara.py").read_text(encoding="utf-8")
    match = re.search(r"PUBLIC_ASSETS\s*=\s*frozenset\(\{(.*?)\}\)", src, re.S)
    assert match
    public = match.group(1)
    for asset in ("/anthropometry.html", "/anthropometry-i18n.js"):
        assert repr(asset) in public


def test_docker_image_copies_anthropometry():
    docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    copy_instructions = "\n".join(line for line in docker.splitlines() if line.startswith("COPY "))
    assert "anthropometry.html" in copy_instructions
    assert "anthropometry-i18n.js" in copy_instructions
