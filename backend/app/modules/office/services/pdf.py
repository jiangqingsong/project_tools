import io
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.core.file_utils import get_temp_path

ALLOWED_IMAGE_FORMATS = {"png", "jpg", "jpeg"}


def pdf_merge(file_paths: list[Path]) -> Path:
    if not file_paths:
        raise ValueError("请至少选择一个 PDF 文件")
    writer = PdfWriter()
    for fp in file_paths:
        reader = PdfReader(str(fp))
        for page in reader.pages:
            writer.add_page(page)
    output = get_temp_path("merged.pdf")
    writer.write(str(output))
    return output


def pdf_split(file_path: Path, mode: str, pages: str) -> Path:
    reader = PdfReader(str(file_path))
    total = len(reader.pages)
    if total == 0:
        raise ValueError("PDF 文件没有页面")
    ranges = _parse_split_ranges(mode, pages, total)

    zip_path = get_temp_path("split.zip")
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        for i, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            for p in range(start, end + 1):
                writer.add_page(reader.pages[p])
            buf = io.BytesIO()
            writer.write(buf)
            zf.writestr(f"part_{i + 1:03d}.pdf", buf.getvalue())
    return zip_path


def _parse_split_ranges(mode: str, pages: str, total: int) -> list[tuple[int, int]]:
    if mode == "range":
        ranges = []
        for part in pages.split(","):
            try:
                start, end = part.split("-")
                s, e = int(start) - 1, int(end) - 1
            except ValueError:
                raise ValueError(f"页码范围格式错误: {part}，应为 起始-结束")
            if s < 0 or e >= total or s > e:
                raise ValueError(f"页码范围超出 PDF 页数范围(1-{total}): {part}")
            ranges.append((s, e))
        return ranges
    if mode == "count":
        try:
            count = int(pages)
        except ValueError:
            raise ValueError(f"每份页数必须是数字: {pages}")
        if count <= 0:
            raise ValueError("每份页数必须大于 0")
        return [(i, min(i + count - 1, total - 1)) for i in range(0, total, count)]
    if mode == "parts":
        try:
            parts = int(pages)
        except ValueError:
            raise ValueError(f"份数必须是数字: {pages}")
        if parts <= 0:
            raise ValueError("份数必须大于 0")
        if parts > total:
            raise ValueError(f"份数({parts})不能大于总页数({total})")
        per_part = total // parts
        remainder = total % parts
        ranges = []
        start = 0
        for i in range(parts):
            size = per_part + (1 if i < remainder else 0)
            end = start + size - 1
            ranges.append((start, end))
            start = end + 1
        return ranges
    raise ValueError(f"不支持的拆分模式: {mode}，可选 range/count/parts")


def pdf_to_word(file_path: Path) -> Path:
    import pdfplumber
    from docx import Document

    doc = Document()
    with pdfplumber.open(str(file_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                doc.add_paragraph(text)
    output = get_temp_path("converted.docx")
    doc.save(str(output))
    return output


def pdf_to_image(file_path: Path, fmt: str = "png") -> Path:
    from pdf2image import convert_from_path

    fmt_lower = fmt.lower()
    if fmt_lower not in ALLOWED_IMAGE_FORMATS:
        raise ValueError(f"不支持的图片格式: {fmt}，可选 png/jpg")

    images = convert_from_path(str(file_path))
    zip_path = get_temp_path("images.zip")
    with zipfile.ZipFile(str(zip_path), "w") as zf:
        for i, img in enumerate(images):
            buf = io.BytesIO()
            img.save(buf, format=fmt.upper())
            zf.writestr(f"page_{i + 1:03d}.{fmt_lower}", buf.getvalue())
    return zip_path
