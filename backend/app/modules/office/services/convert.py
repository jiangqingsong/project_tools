from pathlib import Path

from docx import Document

from app.core.file_utils import get_temp_path


def word_to_pdf(file_path: Path) -> Path:
    from docx2pdf import convert
    output = get_temp_path("converted.pdf")
    convert(str(file_path), str(output))
    return output


def markdown_convert(text: str, output_format: str) -> Path:
    import markdown

    html = markdown.markdown(text, extensions=["tables", "fenced_code", "codehilite"])

    if output_format == "pdf":
        from weasyprint import HTML
        output = get_temp_path("converted.pdf")
        HTML(string=html).write_pdf(str(output))
        return output

    if output_format == "docx":
        from htmldocx import HtmlToDocx
        doc = Document()
        HtmlToDocx().add_html_to_document(html, doc)
        output = get_temp_path("converted.docx")
        doc.save(str(output))
        return output

    raise ValueError(f"Unsupported format: {output_format}")
