import inspect
import json
import logging
import os
import subprocess
import time

from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, List, Optional, TypeAlias, Union

from .core import Bar
from __about__ import __version__


SB_ENV_VARS: List[str] = [
    "_",
    "BAR_NAME",
    "INFO",
    "NAME",
    "SENDER",
    "CONFIG_DIR",
    "BUTTON",
    "MODIFIER",
    "SCROLL_DELTA",
]

PropertyValue: TypeAlias = Union[str, int, float]
Properties: TypeAlias = Dict[str, PropertyValue]


class Sketchybar:
    _: str = ""
    info: str = ""
    name: str = ""
    sender: str = ""

    def __init__(self, logging_level: str = "INFO"):
        self.logging_level: str = logging_level
        self.init_logging()

        for key in SB_ENV_VARS:
            self.__setattr__(key.lower(), os.environ.get(key))

        if self.name:
            self.update()
        else:
            self.dbg("post init executed")
            self.logger.info(f"Loading {__file__} using Sketchybar-py library version {__version__}")
            self.post_init()
            self.do("--update")
            self.dbg("Forcing update", "")

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str) -> None:
        value = value.strip("\n")
        visible = "icon.drawing=on" if value else "icon.drawing=off"
        self.set_item(self.name, f"icon={value}", visible)
        self._icon = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        value = value.strip("\n")
        visible = "label.drawing=on" if value else "label.drawing=off"
        self.set_item(self.name, f"label={value}", visible)
        self._label = value

    def flatten(self, items: Any) -> List[Any]:
        flat_list: List[Any] = []
        if not isinstance(items, (str, dict)):
            for item in items:
                if isinstance(item, (list, set)):
                    flat_list.extend(self.flatten(item))
                else:
                    flat_list.append(item)
        elif isinstance(items, dict):
            for k, v in items.items():
                self.dbg("dict_parse", k, v)
                flat_list.append(f"{k}={v}")
        else:
            flat_list.append(items)
        return flat_list

    def dbg(self, action: str = "", *args: Any) -> None:
        self.logger.debug(f"{self.name or 'Sketchybar'} : {action} {self.flatten(args)}")

    def do(self, *args: int | str | dict[Any, Any] | list[Any]) -> Any:
        self.dbg("    args:", args)
        cmd = self.flatten(["sketchybar"] + self.flatten([self.flatten(arg) for arg in args]))
        self.dbg("    runs", cmd)
        return subprocess.run(cmd, text=True, capture_output=True)

    def run(self, args: str) -> Any:
        return subprocess.run(self.flatten(args), shell=True, text=True, capture_output=True)

    def add_item(self, name: str, position: str) -> None:
        self.dbg("adding item ", name, position)
        self.do("--add", "item", name, position)
        self.do("--set", name, f"script={self._}")
        self.dbg("    item added", name)

    def set_item(self, name: str, *properties: Any) -> None:
        self.dbg("updating item", name)
        self.do("--set", name, self.flatten(properties))
        self.dbg("    item updated", name)

    def get_item(self, name: str) -> Dict[Any, Any]:
        self.dbg("query item", name)
        return json.loads(self.do("--query", name).stdout.strip("\n"))

    def get_bar(self) -> Bar:
        self.dbg("query bar")
        dict = json.loads(self.do("--query", "bar").stdout.strip("\n"))
        return Bar(**dict)

    def subscribe(self, name: str, *events: str | list[str]) -> None:
        self.dbg("subscribing item", name, events)
        self.do("--subscribe", name, self.flatten(events))
        self.dbg("    item subscribed", name)

    def post_init(self):
        pass

    def update(self):
        self.dbg("updating")
        method = getattr(self, self.name, None)
        if callable(method):
            self.dbg(f"    method '{self.name}' found.")
            return method()
        else:
            self.logger.warning(f"    method '{self.name}' not found.")

    @staticmethod
    def item(
        enabled: Optional[bool] = True,
        position: str = "left",
        icon: str = "",
        label: str = "",
        subscribe: Optional[List[str]] = None,
        update_freq: int = 0,
        **kwargs: Any,
    ) -> Any:
        def inner_function(f: Any) -> Any:
            @wraps(f)
            def innermost_function(self: Any) -> None:
                if self.name:
                    return f(self)
                else:
                    if not enabled:
                        return
                    item_name = f.__name__
                    self.add_item(item_name, position)
                    self.set_item(item_name, f"icon={icon or '+'}", f"label={label or item_name}")
                    if subscribe:
                        self.subscribe(item_name, subscribe)
                    if update_freq:
                        self.set_item(item_name, [f"update_freq={update_freq}"])

                    if len(kwargs):
                        for key, val in kwargs.items():
                            if key == "properties" and isinstance(val, dict):
                                self.dbg("additional properties", len(kwargs))
                                properties: Properties = val
                                for property_name, value in properties.items():
                                    self.dbg("    property", property_name, value)
                                    self.set_item(item_name, [f"{property_name}={value}"])

            return innermost_function

        return inner_function

    def wrapped_methods(self):
        return inspect.getmembers(self, predicate=lambda x: callable(x) and hasattr(x, "__wrapped__"))

    def autoload(self):
        self.dbg("autoload initiated. items detected:", len(self.wrapped_methods()))
        for name, method in self.wrapped_methods():
            self.dbg("found item definition:", name)
            method()

    def init_logging(self):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger("sketchybar-py")
        self.logger.addHandler(handler)
        match self.logging_level:
            case "DEBUG" | logging.DEBUG:
                self.logger.setLevel(logging.DEBUG)
            case "INFO" | logging.INFO:
                self.logger.setLevel(logging.INFO)
            case "WARNING" | logging.WARNING:
                self.logger.setLevel(logging.WARNING)
            case _:
                self.logger.setLevel(logging.NOTSET)

    def animate(
        self, name: str = "", curve: str = "linear", duration: int = 10, animation: str = "label.color.alpha=0.0"
    ) -> None:
        name = name if name else self.name
        self.run(f"sketchybar --animate {curve} {duration} --set {name} {animation}")
        time.sleep(duration / 60 * 1.1)

    @contextmanager
    def animation(
        self,
        curve: str = "linear",
        duration: int = 10,
        before: str = "label.color.alpha=0.0",
        after: str = "label.color.alpha=1.0",
    ) -> Any:
        try:
            self.animate(curve=curve, duration=duration, animation=before)
            yield
        finally:
            self.animate(curve=curve, duration=duration, animation=after)
            pass
