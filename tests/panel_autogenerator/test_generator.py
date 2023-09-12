import enum

import panel as pn

from bucket_of_utils.panel_autogenerator import PANEL_ELEMENTS_MAP
from bucket_of_utils.panel_autogenerator import Style
from bucket_of_utils.panel_autogenerator import TitleType
from bucket_of_utils.panel_autogenerator import WidgetDict
from bucket_of_utils.panel_autogenerator import generate_panel_code
from bucket_of_utils.qr.wifi import SecurityTypes
from bucket_of_utils.qr.wifi import generate_qr_code


def test_it():
    default_args_values = {
        "security": "WPA",
        "hidden": False,
    }
    additional_widget_map: dict[type:WidgetDict] = {
        SecurityTypes: PANEL_ELEMENTS_MAP[enum.Enum],
    }

    panel_box = generate_panel_code(
        generate_qr_code,
        args_to_skip=["directory_to_save_qr_code", "overwrite"],
        default_args_values=default_args_values,
        arg_type_widget_map=additional_widget_map,
    )
    panel_box.append(pn.pane.Markdown("Possible security types are: `WEP`, `WPA` and no security - leave blank"))

    # pn.serve(panel_box)


def test_another():
    def adding_two_numbers(a: int, b: float) -> str:
        """Function adding two numbers and returning it as a formatted string"""
        return f"{a} + {b} = {a + b}"

    panel_box = generate_panel_code(
        adding_two_numbers,
        options_for_widgets={
            "a": {"start": 1, "end": 10, "step": 2},
            "b": {"start": 2, "step": 0.01},
        },
        arg_name_widget_map={"b": pn.widgets.FloatInput},
        style=Style(
            title=TitleType.CAPITALIZED_FIRST_WORD,
        ),
    )

    # pn.serve(panel_box)
    pass
