import enum
import os
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

versions = {
    "PIL": PIL.__version__,
    "typer": typer.__version__,
}

print(versions)


def get_qr_string(*, ssid: str, password: str, security: str, hidden: bool):
    """Generate a QR string for a given wifi network"""
    return f"WIFI:S:{ssid};T:{security.upper()};P:{password};H:{hidden};;"


class SecurityTypes(enum.StrEnum):
    WPA = enum.auto()
    WEP = enum.auto()
    no_password = ""


def get_font():
    path_to_font = "_static/fonts/FiraCode-Regular.ttf"

    try:
        return ImageFont.truetype(path_to_font, 30)
    except OSError:
        return ImageFont.load_default()


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


def get_formatted_ssid_and_password_texts(*, ssid: str, password: str):
    ssid_prefix = "SSID"
    password_prefix = "Password"

    max_prefix_length = max(len(ssid_prefix), len(password_prefix))
    ssid_prefix = ssid_prefix.rjust(max_prefix_length)
    password_prefix = password_prefix.rjust(max_prefix_length)

    ssid_text = f"{ssid_prefix}: {ssid}"
    password_text = f"{password_prefix}: {password}"

    max_text_length = max(len(ssid_text), len(password_text))
    ssid_text = ssid_text.ljust(max_text_length)
    password_text = password_text.ljust(max_text_length)

    return ssid_text, password_text


def generate_qr_code(  # noqa: PLR0913
    ssid: Annotated[str, typer.Option(help="The SSID of the wifi network")],
    password: Annotated[str, typer.Option(help="The password of the wifi network")],
    security: Annotated[SecurityTypes, typer.Option(help="The security of the wifi network")],
    hidden: Annotated[bool, typer.Option(help="Whether the wifi network is hidden")] = False,  # noqa: FBT002
    directory_to_save_qr_code: Annotated[str, typer.Option(help="The directory to save the QR code to")] = ".",
    overwrite: Annotated[
        bool,
        typer.Option(help="Whether to overwrite the QR code if it already exists"),
    ] = False,
) -> PIL.Image:
    """Generate a QR code for a given WIFI network"""
    security = SecurityTypes(security.lower())
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

    ssid_text, password_text = get_formatted_ssid_and_password_texts(ssid=ssid, password=password)

    image = make_image_fit_to_text(image, text=ssid_text, font=font)
    image = add_text_to_image(image, text=ssid_text, y=20, font=font)

    image = make_image_fit_to_text(image, text=password_text, font=font)
    image = add_text_to_image(image, text=password_text, y=70, font=font)

    image_file_name = f"{ssid.lower()}.png"

    image = add_border_to_image(image, border=(5, 5, 5, 5), fill="black")

    if str(os.environ.get("DEBUG")) == "1":
        image.show()

    path = save_image(
        image=image,
        image_file_name=image_file_name,
        directory_to_save=directory_to_save_qr_code,
        overwrite=overwrite,
    )

    print(f"QR code saved to: {path}")

    return image


def main():
    typer.run(generate_qr_code)


def serve():
    from bucket_of_utils import panel_autogenerator as pag

    default_args_values = {
        "security": "wpa",
        "hidden": False,
    }

    additional_widget_map: dict[type, pag.WidgetDict] = {
        SecurityTypes: pag.PANEL_ELEMENTS_MAP[enum.Enum],
    }

    widget_box = pag.generate_panel_code(
        generate_qr_code,
        args_to_skip=["directory_to_save_qr_code", "overwrite"],
        default_args_values=default_args_values,
        arg_type_widget_map=additional_widget_map,
    )
    widget_box.servable(target="main")


if __name__ == "__main__":
    main()
