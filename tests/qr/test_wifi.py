import os

from bucket_of_utils.qr import wifi


def test_getting_wifi_string():
    assert (
        wifi.get_qr_string(ssid="ssid", password="password", security="WPA", hidden=False)
        == "WIFI:S:ssid;T:WPA;P:password;H:False;;"
    )


def test_getting_wifi_string_with_no_password():
    assert (
        wifi.get_qr_string(ssid="ssid", password="", security="nopass", hidden=False)
        == "WIFI:S:ssid;T:nopass;P:;H:False;;"
    )


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
