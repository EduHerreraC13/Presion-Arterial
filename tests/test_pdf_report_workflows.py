"""PDF report workflow contracts, without camera or external services."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def test_pdf_library_is_deployed_and_allowed():
    assert (ROOT / "yanqhaycare_pdf.js").is_file()
    assert "yanqhaycare_pdf.js" in _read("Dockerfile")
    assert "'/yanqhaycare_pdf.js'" in _read("servidor_camara.py")
    helper = _read("yanqhaycare_pdf.js")
    assert "window.print()" in helper
    assert "Save as PDF" in helper


def test_cardio_report_requires_completed_valid_median():
    html = _read("camara_dashboard.html")
    assert 'id="cardioPdf" type="button" disabled' in html
    assert 'src="yanqhaycare_pdf.js"' in html
    assert "const selected={bpm:numericMedian('bpm')" in html
    assert "if(selected.bpm!==null)" in html
    assert "pdfMedian={...selected" in html
    assert "pdfWaveform=r.waveform.slice()" in html
    assert "function waveformForPDF(data)" in html
    assert "function cardioPdfReport()" in html
    assert "pdfMedian=null;pdfLive=null;pdfWaveform=null" in html


def test_respiration_pdf_uses_completed_assessment():
    html = _read("fatiga_respiracion.html")
    assert 'id="respPdf" type="button" disabled' in html
    assert "function exportRespAssessment()" in html
    assert "Dx.render(dx, '#hdx-panel')" in html
    assert "renderCompare(res, prev)" in html
    assert "renderHistory()" in html
    assert "drawChart(S.winEnd)" in html
    assert "lastPdfAssessment={res,prev,trendImage}" in html
    assert "if(!lastPdfAssessment)return" in html
    assert "const history=S.results.map" in html
    assert "lastPdfAssessment=null" in html


def test_reports_support_language_selection():
    html = _read("fatiga_respiracion.html")
    cardio = _read("camara_dashboard.html")
    translations = _read("heamon_i18n.js")
    assert "window.HEAMONi18n?.language==='es'" in html
    assert "window.HEAMONi18n?.language==='es'" in cardio
    assert "Export Results" in translations
    assert "Download PDF Report" in translations
