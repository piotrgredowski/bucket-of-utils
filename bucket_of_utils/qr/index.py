import enum

from bucket_of_utils.panel_autogenerator.main import PANEL_ELEMENTS_MAP
from bucket_of_utils.panel_autogenerator.main import WidgetDict
from bucket_of_utils.panel_autogenerator.main import generate_panel_code
from bucket_of_utils.qr.wifi import SecurityTypes
from bucket_of_utils.qr.wifi import generate_qr_code

default_args_values = {
    "security": "WPA",
    "hidden": False,
}
additional_widget_map: dict[type:WidgetDict] = {
    SecurityTypes: PANEL_ELEMENTS_MAP[enum.Enum],
}

widget_box = generate_panel_code(
    generate_qr_code,
    args_to_skip=["directory_to_save_qr_code", "overwrite"],
    default_args_values=default_args_values,
    additional_widget_map=additional_widget_map,
)
widget_box.servable(target="main")
