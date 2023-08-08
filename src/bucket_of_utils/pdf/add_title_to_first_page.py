from dataclasses import dataclass
from dataclasses import field
from typing import Literal

import pdf_annotate as pa


@dataclass
class AnnotationConfig:
    x_start: int = field(default=20)
    x_end: int = field(default=320)
    y_start: int = field(default=20)
    y_end: int = field(default=100)
    page: Literal["*"] | int = field(default="*")
    font_size: int = field(default=10)
    text_pattern: str = field(default="{file_name}")


def add_file_name_annotation_to_pdf(
    *,
    doc: pa.PdfAnnotator,
    file_name: str,
    config: AnnotationConfig | None = None,
):
    """
    Adds file name to first page of PDF file.
    """
    if config is None:
        config = AnnotationConfig()
    text_appearance = pa.Appearance(
        font_size=config.font_size,
        text_baseline="bottom",
        fill=[0, 0, 0],
    )
    text = config.text_pattern.format(file_name=file_name)

    if config.page == "*":
        # FIXME: is there better way to get number of pages?
        page_no = doc._pdf._reader.numPages  # noqa: SLF001
        pages = list(range(0, page_no))
    else:
        pages = [config.page]

    for page in pages:
        doc.add_annotation(
            "text",
            pa.Location(x1=config.x_start, y1=config.y_start, x2=config.x_end, y2=config.y_end, page=page),
            appearance=text_appearance.copy(content=text),
        )

    return doc
