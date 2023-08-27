import os

from imgcompare import is_equal
from PIL import Image

from bucket_of_utils.qr import wifi


def test_getting_wifi_string():
    assert (
        wifi.get_qr_string(ssid="ssid", password="password", security="WPA", hidden=False)
        == "WIFI:S:ssid;T:WPA;P:password;H:False;;"
    )


def test_getting_wifi_string_with_no_password():
    assert wifi.get_qr_string(ssid="ssid", password="", security="", hidden=False) == "WIFI:S:ssid;T:;P:;H:False;;"


def test_generating_qr_code():
    wifi.generate_qr_code(
        ssid="ssid",
        password="password",
        security=wifi.SecurityTypes.WPA,
        hidden=False,
        directory_to_save_qr_code="tests/qr/_generated",
        overwrite=True,
    )

    assert os.path.exists("tests/qr/_generated/ssid.png")


def test_generated_qr_code_is_the_same():
    wifi.generate_qr_code(
        ssid="my_ssid",
        password="my_password",
        security=wifi.SecurityTypes.WPA,
        hidden=False,
        directory_to_save_qr_code="tests/qr/_generated",
        overwrite=True,
    )
    assert os.path.exists("tests/qr/_generated/my_ssid.png")

    base_image = Image.open("tests/qr/_generated/my_ssid.png")
    compare_image = Image.open("_static/images/my_ssid.png")

    assert is_equal(base_image, compare_image, tolerance=1) is True
