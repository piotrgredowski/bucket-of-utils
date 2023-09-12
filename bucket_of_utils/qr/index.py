import enum

from bucket_of_utils import panel_autogenerator as pag
from bucket_of_utils.qr.wifi import SecurityTypes
from bucket_of_utils.qr.wifi import generate_qr_code

default_args_values = {
    "security": "WPA",
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
