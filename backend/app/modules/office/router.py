import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.core.file_utils import get_temp_path
from app.modules.office.services.pdf import pdf_merge, pdf_split, pdf_to_word, pdf_to_image
from app.modules.office.services.convert import word_to_pdf, markdown_convert

router = APIRouter()


def _save_temp(upload: UploadFile, suffix: str) -> Path:
    path = get_temp_path(f"upload_{suffix}")
    with open(path, "wb") as f:
        shutil.copyfileobj(upload.file, f)
    return path


@router.post("/pdf/to-word")
async def pdf_to_word_api(file: UploadFile = File(...)):
    tmp = _save_temp(file, ".pdf")
    result = pdf_to_word(tmp)
    return FileResponse(result, filename=result.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@router.post("/pdf/merge")
async def pdf_merge_api(files: list[UploadFile] = File(...)):
    paths = [_save_temp(f, ".pdf") for f in files]
    result = pdf_merge(paths)
    return FileResponse(result, filename="merged.pdf", media_type="application/pdf")


@router.post("/pdf/split")
async def pdf_split_api(
    file: UploadFile = File(...),
    mode: str = Form(...),
    pages: str = Form(...),
):
    tmp = _save_temp(file, ".pdf")
    result = pdf_split(tmp, mode, pages)
    return FileResponse(result, filename="split.zip", media_type="application/zip")


@router.post("/pdf/to-image")
async def pdf_to_image_api(
    file: UploadFile = File(...),
    fmt: str = Form(default="png"),
):
    tmp = _save_temp(file, ".pdf")
    result = pdf_to_image(tmp, fmt)
    return FileResponse(result, filename="images.zip", media_type="application/zip")


@router.post("/convert/word-to-pdf")
async def word_to_pdf_api(file: UploadFile = File(...)):
    tmp = _save_temp(file, ".docx")
    result = word_to_pdf(tmp)
    return FileResponse(result, filename=result.name, media_type="application/pdf")


@router.post("/convert/markdown")
async def markdown_convert_api(
    text: str = Form(default=""),
    output_format: str = Form(...),
    file: UploadFile | None = None,
):
    if file:
        content = (await file.read()).decode("utf-8")
    else:
        content = text
    result = markdown_convert(content, output_format)
    media_type = "application/pdf" if output_format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(result, filename=result.name, media_type=media_type)
