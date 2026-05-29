import subprocess
from pathlib import Path

from docx import Document

from app.core.file_utils import get_temp_path


LIBREOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


def word_to_pdf(file_path: Path) -> Path:
    output = get_temp_path("converted.pdf")
    subprocess.run(
        [LIBREOFFICE, "--headless", "--convert-to", "pdf",
         "--outdir", str(output.parent), str(file_path)],
        check=True, timeout=120,
    )
    actual = output.parent / f"{file_path.stem}.pdf"
    if actual != output:
        actual.rename(output)
    return output


def markdown_convert(text: str, output_format: str) -> Path:
    import markdown

    html_body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
th {{ background-color: #f5f5f5; }}
pre, code {{ background-color: #f4f4f4; }}
pre {{ padding: 12px; border-radius: 4px; }}
code {{ padding: 2px 4px; }}
blockquote {{ border-left: 3px solid #ccc; padding-left: 12px; color: #666; }}
hr {{ border: none; border-top: 1px solid #ddd; }}
</style></head><body>{html_body}</body></html>"""

    html_path = get_temp_path("source.html")
    html_path.write_text(full_html, encoding="utf-8")

    if output_format == "pdf":
        from weasyprint import HTML
        output = get_temp_path("converted.pdf")
        HTML(string=full_html).write_pdf(str(output))
        return output

    if output_format == "docx":
        output = get_temp_path("converted.docx")
        subprocess.run(
            [LIBREOFFICE, "--headless", "--infilter=HTML (StarWriter)",
             "--convert-to", "docx",
             "--outdir", str(output.parent), str(html_path)],
            check=True, timeout=120,
        )
        actual = output.parent / f"{html_path.stem}.docx"
        if actual != output:
            actual.rename(output)
        return output

    raise ValueError(f"Unsupported format: {output_format}")
