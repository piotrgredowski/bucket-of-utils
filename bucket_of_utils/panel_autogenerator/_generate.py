"""
WIP.

This is a module that generates a `panel` app for a function.

It's in some places specific for `typer` and needs a lot of work to be more generic.
For now - it allows me to generate some `panel` code for functions.
"""

import enum
import typing
from collections.abc import Callable
from typing import Optional
from typing import TypedDict

import panel as pn
from PIL import Image

from ._style import Style


def _get_all_args_and_kwargs_names(function: Callable) -> tuple:
    args = function.__code__.co_varnames[: function.__code__.co_argcount]
    kw_start_index = function.__code__.co_argcount
    kw_end_index = kw_start_index + function.__code__.co_kwonlyargcount
    kwargs = function.__code__.co_varnames[function.__code__.co_argcount : kw_end_index]
    return args, kwargs


def get_type_of_arg(function: Callable, arg_name: str) -> typing.Any:
    annotation = function.__annotations__.get(arg_name, typing.Any)
    if getattr(annotation, "__origin__", None) is typing.Annotated:
        return annotation.__args__[0]
    if type_ := getattr(annotation, "__origin__", None):
        return type_
    return annotation


class WidgetDict(TypedDict):
    widget: type[pn.widgets.Widget]
    args_factory: Optional[Callable]


PANEL_ELEMENTS_MAP: dict[type, WidgetDict] = {
    int: WidgetDict(widget=pn.widgets.IntSlider, args_factory=None),
    bool: WidgetDict(widget=pn.widgets.Checkbox, args_factory=None),
    str: WidgetDict(widget=pn.widgets.TextInput, args_factory=None),
    float: WidgetDict(widget=pn.widgets.FloatSlider, args_factory=None),
    enum.Enum: WidgetDict(widget=pn.widgets.Select, args_factory=lambda enum_: {"options": [e.value for e in enum_]}),
}

_PANEL_RESULTS_MAP = {
    str: pn.pane.Str,
    Image.Image: pn.pane.PNG,
}


def get_help_for_arg(function: Callable, arg_name: str) -> Optional[str]:
    annotation = function.__annotations__.get(arg_name)
    if metadata := getattr(annotation, "__metadata__", None):
        return getattr(metadata[0], "help", None)

    if getattr(annotation, "__origin__", None) is typing.Annotated:
        for arg in annotation.__args__[1:]:
            if isinstance(arg, str):
                return arg
    return None


def __widget_factory_wrapper(*, widget_dict, args_factory, arg_type, additional_args):
    def widget_factory(*args, **kwargs):
        nonlocal additional_args
        additional_args_ = additional_args.copy()

        if args_factory is not None:
            additional_args_ = {**args_factory(arg_type), **additional_args_}

        return widget_dict["widget"](*args, **kwargs, **additional_args_)

    return widget_factory


def __initialize_arg_dicts(
    *arg_dicts,
    **__,
):
    return (arg_dict or {} for arg_dict in arg_dicts)


def _build_widgets(widgets, default_args_values, function):
    widgets_list = []
    for arg_name, widget_type in widgets.items():
        name = arg_name
        if help_text := get_help_for_arg(function, arg_name):
            name = f"{arg_name} ({help_text})"
        value = default_args_values.get(arg_name, None)
        widget_kwargs = {"name": name}
        if value is not None:
            widget_kwargs["value"] = value

        widgets_list.append(widget_type(**widget_kwargs))

    return widgets_list


def generate_panel_code(  # noqa: C901, PLR0913
    function: Callable,
    *,
    default_args_values: Optional[dict[str, typing.Any]] = None,
    args_to_skip: Optional[list[str]] = None,
    arg_type_widget_map: Optional[dict[type, pn.widgets.Widget]] = None,
    arg_name_widget_map: Optional[dict[str, pn.widgets.Widget]] = None,
    options_for_widgets: Optional[dict[str, dict[str, typing.Any]]] = None,
    style: Optional[Style] = None,
) -> str:
    (
        default_args_values,
        args_to_skip,
        arg_type_widget_map,
        arg_name_widget_map,
        options_for_widgets,
    ) = __initialize_arg_dicts(
        default_args_values,
        args_to_skip,
        arg_type_widget_map,
        arg_name_widget_map,
        options_for_widgets,
    )

    if style is None:
        style = Style()
    args, kwargs = _get_all_args_and_kwargs_names(function)

    args_types = {arg_name: get_type_of_arg(function, arg_name) for arg_name in args}
    kwargs_types = {kwarg_name: get_type_of_arg(function, kwarg_name) for kwarg_name in kwargs}

    widgets = {}

    elements_map = {**PANEL_ELEMENTS_MAP, **arg_type_widget_map}

    for arg_name, arg_type in [*args_types.items(), *kwargs_types.items()]:
        if arg_name in args_to_skip:
            continue
        widget_dict = elements_map.get(arg_type)
        if arg_name in arg_name_widget_map:
            widget_dict = WidgetDict(widget=arg_name_widget_map[arg_name], args_factory=widget_dict["args_factory"])
        if widget_dict is None:
            continue
        args_factory = widget_dict.get("args_factory", None)

        widgets[arg_name] = __widget_factory_wrapper(
            widget_dict=widget_dict,
            args_factory=args_factory,
            arg_type=arg_type,
            additional_args=options_for_widgets.get(arg_name, {}),
        )

    function_name = style.format_title(function.__name__)

    doc_of_function = function.__doc__ or None
    if doc_of_function:
        header = pn.pane.Markdown(
            f"""
# {function_name}

**{doc_of_function}**
""".strip(),
        )

    widgets_list = _build_widgets(widgets=widgets, default_args_values=default_args_values, function=function)

    button = pn.widgets.Button(name="Run", button_type="primary")
    widgets_list.append(button)

    args_column = pn.Column(*widgets_list)

    results_container = pn.Column(pn.pane.Markdown("# Result"))

    results_column = pn.Column()

    def _run(column: pn.Column, clicked: pn.widgets.Button):
        if not clicked:
            return

        func_args = []
        for widget in column:
            for arg_name in [*args, *kwargs]:
                if not widget.name.startswith(arg_name):
                    continue
                func_args.append(widget.value)
        result = function(*func_args)
        results_column.clear()

        results_type = type(result)

        result_widget = _PANEL_RESULTS_MAP.get(results_type, pn.pane.Str)(result)
        results_column.append(result_widget)
        results_container.append(results_column)
        row.append(results_container)

    _runner = pn.bind(_run, args_column, clicked=button)
    args_column.append(_runner)
    row = pn.Row(pn.Column(header, args_column))

    return pn.WidgetBox(row)
