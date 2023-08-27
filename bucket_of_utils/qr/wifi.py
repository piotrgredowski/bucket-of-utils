import enum
from pathlib import Path
from typing import Annotated

import PIL
import qrcode
import qrcode.image.svg
import typer
from PIL import ImageDraw
from PIL import ImageFont
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer


def get_qr_string(*, ssid: str, password: str, security: str, hidden: bool):
    """Generate a QR string for a given wifi network"""
    return f"WIFI:S:{ssid};T:{security};P:{password};H:{hidden};;"


class SecurityTypes(enum.StrEnum):
    WPA = enum.auto()
    WEP = enum.auto()
    nopass = enum.auto()


def get_font():
    path_to_font = "_static/fonts/Lato-Regular.ttf"
    return ImageFont.truetype(path_to_font, 30)


def add_text_to_image(image: PIL.Image, text: str, y: int, font: ImageFont):
    draw = ImageDraw.Draw(image)

    image_width = image.size[0]

    draw.textlength(text, font=font)
    text_width = draw.textbbox(xy=(0, 0), text=text, font=font)[2]

    x = (image_width - text_width) / 2
    draw.text(xy=(x, y), text=text, fill=0, font=font, align="center")
    return image


def add_border_to_image(image: PIL.Image, border: tuple[int, int, int, int], fill="white"):
    from PIL import ImageOps

    return ImageOps.expand(image, border=border, fill=fill)


def get_width_to_add(image: PIL.Image, text: str, font: ImageFont):
    draw = ImageDraw.Draw(image)

    image_width = image.size[0]

    draw.textlength(text, font=font)
    text_width = draw.textbbox(xy=(0, 0), text=text, font=font)[2]

    spacer = 20
    if text_width + spacer > image_width:
        return text_width - image_width + spacer

    return 0


def make_image_fit_to_text(image: PIL.Image, text: str, font: ImageFont):
    if width_to_add := get_width_to_add(image, text=text, font=font):
        to_add = int(width_to_add / 2) + 1
        image = add_border_to_image(image, border=(to_add, 0, to_add, 0))

    return image


def save_image(*, image: PIL.Image, image_file_name: str, directory_to_save: str, overwrite: bool) -> str:
    file_name, file_extension = image_file_name.split(".")
    import os

    if not overwrite and os.path.exists(image_file_name):
        i = 1
        while os.path.exists(f"{file_name}_{i}.{file_extension}"):
            i += 1
        image_file_name = f"{file_name}_{i}.{file_extension}"
    directory = Path(directory_to_save)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / image_file_name

    image.save(path)
    return str(path)


def generate_qr_code(  # noqa: PLR0913
    ssid: Annotated[str, typer.Option(help="The SSID of the wifi network")],
    password: Annotated[str, typer.Option(help="The password of the wifi network")],
    security: Annotated[SecurityTypes, typer.Option(help="The security of the wifi network")],
    hidden: Annotated[bool, typer.Option(help="Whether the wifi network is hidden")] = False,  # noqa: FBT002
    directory_to_save_qr_code: Annotated[str, typer.Option(help="The directory to save the QR code to")] = ".",
    overwrite: Annotated[
        bool,
        typer.Option(help="Whether to overwrite the QR code if it already exists"),
    ] = False,  # noqa: FBT002
):
    """Generate a QR code for a given WIFI network"""
    string = get_qr_string(ssid=ssid, password=password, security=security.value, hidden=hidden)

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(string)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=SquareModuleDrawer(),
    )

    image = add_border_to_image(image, border=(0, 100, 0, 0))

    font = get_font()

    ssid_text = f"SSID: {ssid}"
    image = make_image_fit_to_text(image, text=ssid_text, font=font)
    image = add_text_to_image(image, text=ssid_text, y=20, font=font)

    password_text = f"Password: {password}"

    image = make_image_fit_to_text(image, text=password_text, font=font)
    image = add_text_to_image(image, text=password_text, y=70, font=font)

    image_file_name = f"{ssid.lower()}.png"

    image = add_border_to_image(image, border=(5, 5, 5, 5), fill="black")

    path = save_image(
        image=image,
        image_file_name=image_file_name,
        directory_to_save=directory_to_save_qr_code,
        overwrite=overwrite,
    )

    print(f"QR code saved to: {path}")


def main():
    typer.run(generate_qr_code)


if __name__ == "__main__":
    main()
