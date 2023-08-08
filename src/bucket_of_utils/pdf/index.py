import io
import tempfile
import zipfile
from dataclasses import asdict
from pathlib import Path

import pdf_annotate
import pdfrw
from add_title_to_first_page import AnnotationConfig
from add_title_to_first_page import add_file_name_annotation_to_pdf
from js import Blob
from js import document
from js import window
from pyodide.ffi import create_proxy
from pyodide.ffi import to_js

CONFIG_DISABLED = True


def build_config_box():
    config_div = document.getElementById("config")
    config = AnnotationConfig()
    if CONFIG_DISABLED:
        description = document.createElement("p")
        description.innerText = "For now you can't change config."
        config_div.appendChild(description)

    for key, value in asdict(config).items():
        label = document.createElement("label")
        if key == "page":
            label.innerText = key + ", * means all pages"
        else:
            label.innerText = key
        label.className = "form-label"
        # span = document.createElement("span")
        # label.appendChild(span)
        input_ = document.createElement("input")
        input_.value = value
        input_.className = "form-control"
        if CONFIG_DISABLED:
            input_.disabled = True
        div = document.createElement("div")
        div.className = ""
        div.appendChild(label)
        div.appendChild(input_)
        config_div.appendChild(div)


files = []


async def _show_files(e):
    file_list = e.target.files.to_py()
    global files  # noqa: PLW0603
    files = file_list

    output_upload = document.getElementById("output_upload")
    output_upload.innerHTML = ""
    header = document.createElement("h4")
    header.innerText = "Uploaded files"
    output_upload.appendChild(header)
    ul = document.createElement("ul")
    ul.style.maxHeight = "400px"
    ul.style.overflowY = "auto"
    output_upload.appendChild(ul)

    for file_ in file_list:
        li = document.createElement("li")
        li.innerText = file_.name
        ul.appendChild(li)

    document.getElementById("convert-files").disabled = False


async def get_bytes_from_file(file):
    array_buf = await file.arrayBuffer()
    return array_buf.to_bytes()


async def _process_files(*_, **__):
    global files  # noqa: PLW0602

    converted_files = []

    results = document.getElementById("results")

    for file_ in files:
        file_bytes = await get_bytes_from_file(file_)
        stream = io.BytesIO(file_bytes)
        reader = pdfrw.PdfReader(stream)
        doc = pdf_annotate.PdfAnnotator(reader)

        converted = add_file_name_annotation_to_pdf(doc=doc, file_name=file_.name)
        with tempfile.NamedTemporaryFile() as f:
            converted.write(f)
            f.seek(0)
            content = f.read()

        converted_files.append((file_.name, content))

    results_file_name = "results.zip"
    with zipfile.ZipFile(results_file_name, mode="w") as zf:
        for file_name, content in converted_files:
            zf.writestr(zipfile.ZipInfo(file_name), data=content)

    zip_file_content = Path.open(zf.filename, "rb").read()

    blob = Blob.new([to_js(zip_file_content)], {type: "application/octet-stream"})
    download_link = document.createElement("a")
    download_link.href = window.URL.createObjectURL(blob)
    download_link.download = results_file_name
    download_button = document.createElement("button")
    download_button.innerHTML = "Download results"
    download_button.className = "btn btn-secondary"

    download_link.appendChild(download_button)

    results.appendChild(download_link)
    results.style = {"display": "auto"}


show_files = create_proxy(_show_files)
process_files = create_proxy(_process_files)
build_config_box()

document.getElementById("file-upload").addEventListener("change", show_files)
document.getElementById("convert-files").addEventListener("click", process_files)
