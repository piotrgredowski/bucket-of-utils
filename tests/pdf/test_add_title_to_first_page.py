import tempfile
from pathlib import Path

import pdf_annotate as pa

from src.bucket_of_utils.pdf.add_title_to_first_page import AnnotationConfig
from src.bucket_of_utils.pdf.add_title_to_first_page import add_file_name_annotation_to_pdf


def test_add_file_name_annotation_to_pdf():
    file_ = Path(__file__).parent / "dummy.pdf"
    doc = pa.PdfAnnotator(str(file_))

    config = AnnotationConfig()

    add_file_name_annotation_to_pdf(doc=doc, file_name=file_.name, config=config)
    with tempfile.NamedTemporaryFile() as tmpfile:
        name = tmpfile.name + ".pdf"
        doc.write(name)

    # TODO: add checking if annotation exists. For now if no error was raise - let's assume that it works
