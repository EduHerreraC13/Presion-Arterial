"""Regression checks for YanqhayCare display branding and English documentation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_homepage_uses_yanqhaycare_brand():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "<title>YanqhayCare" in page
    assert '<div class="brand">YanqhayCare ' in page
    for tab in ("tabBp", "tabFat", "tabAnth"):
        assert f'id="{tab}"' in page


def test_module_titles_use_yanqhaycare():
    fatigue = (ROOT / "fatiga_respiracion.html").read_text(encoding="utf-8")
    anthropometry = (ROOT / "anthropometry.html").read_text(encoding="utf-8")
    assert "<title>YanqhayCare" in fatigue
    assert "<title>YanqhayCare" in anthropometry


def test_readme_covers_mission_three_modules_and_anthropometry_workflow():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in (
        "# YanqhayCare",
        "NASA Space Apps Challenge 2026",
        "Module 1 — Cardiovascular monitoring",
        "Module 2 — Visual fatigue and breathing",
        "Module 3 — Anthropometry",
        "calibrate distance",
        "estimate body height",
        "extended-arm method",
        "analyze saved photos and videos",
        "calibrate the band's colors",
        "Research scope",
    ):
        assert phrase.lower() in readme.lower(), phrase


def test_internal_legacy_camera_contract_still_present():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    i18n = (ROOT / "heamon_i18n.js").read_text(encoding="utf-8")
    assert "window.HEAMONCamera" in page
    assert "window.HEAMONi18n" in page
    assert "window.HEAMONi18n" in i18n
    assert "HEAMON_LANGUAGE" in i18n
