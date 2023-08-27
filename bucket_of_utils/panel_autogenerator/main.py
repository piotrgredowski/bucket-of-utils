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
import PIL


def _get_all_args_and_kwargs_names(function: Callable) -> tuple:
    args = function.__code__.co_varnames[: function.__code__.co_argcount]
    kw_start_index = function.__code__.co_argcount
    kw_end_index = kw_start_index + function.__code__.co_kwonlyargcount
    kwargs = function.__code__.co_varnames[function.__code__.co_argcount : kw_end_index]
    return args, kwargs


def get_type_of_arg(function: Callable, arg_name: str) -> str:
    try:
        type_ = function.__annotations__.get(arg_name).__args__
        return type_[0]
    except (AttributeError, IndexError):
        return function.__annotations__.get(arg_name, typing.Any)


class WidgetDict(TypedDict):
    widget: pn.widgets.Widget
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
    PIL.Image.Image: pn.pane.PNG,
}


def get_help_for_arg(function: Callable, arg_name: str) -> str | None:
    arg = function.__annotations__.get(arg_name, None)
    try:
        return arg.__metadata__[0].help
    except AttributeError:
        return None


def generate_panel_code(  # noqa: C901,PLR0915
    function: Callable,
    *,
    default_args_values: Optional[dict[str, typing.Any]] = None,
    args_to_skip: Optional[list[str]] = None,
    additional_widget_map: Optional[dict[type, pn.widgets.Widget]] = None,
) -> str:
    if default_args_values is None:
        default_args_values = {}
    if args_to_skip is None:
        args_to_skip = []
    if additional_widget_map is None:
        additional_widget_map = {}
    args, kwargs = _get_all_args_and_kwargs_names(function)

    args_types = {arg_name: get_type_of_arg(function, arg_name) for arg_name in args}
    kwargs_types = {kwarg_name: get_type_of_arg(function, kwarg_name) for kwarg_name in kwargs}

    widgets = {}

    elements_map = {**PANEL_ELEMENTS_MAP, **additional_widget_map}

    for arg_name, arg_type in [*args_types.items(), *kwargs_types.items()]:
        if arg_name in args_to_skip:
            continue
        widget_dict = elements_map.get(arg_type, None)
        if widget_dict is None:
            continue
        args_factory = widget_dict.get("args_factory", None)

        def widget_factory_wrapper(*, widget_dict, args_factory, arg_type):
            def widget_factory(*args, **kwargs):
                additional_args = {}

                if args_factory is not None:
                    additional_args = args_factory(arg_type)

                return widget_dict["widget"](*args, **kwargs, **additional_args)

            return widget_factory

        widgets[arg_name] = widget_factory_wrapper(
            widget_dict=widget_dict,
            args_factory=args_factory,
            arg_type=arg_type,
        )

    function_name = " ".join(function.__name__.upper().split("_"))

    doc_of_function = function.__doc__ or None
    if doc_of_function:
        header = pn.pane.Markdown(
            f"""
# {function_name}

**{doc_of_function}**
""".strip(),
        )

    widgets_list = []
    for arg_name, widget_type in widgets.items():
        name = arg_name
        if help_text := get_help_for_arg(function, arg_name):
            name = f"{arg_name} ({help_text})"
        value = default_args_values.get(arg_name, None)
        widget_kwargs = {"name": name}
        if value is not None:
            widget_kwargs["value"] = value

        pass
        # widget_kwargs["options"] = [e.name for e in arg_type]
        widgets_list.append(widget_type(**widget_kwargs))

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
