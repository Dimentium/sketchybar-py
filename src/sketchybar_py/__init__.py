import os
import subprocess
import inspect
import logging
from functools import wraps

SB_ENV_VARS: list = [
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


class Sketchybar:
    def __init__(self, logging_level="INFO"):
        self.logging_level: str = logging_level
        self.init_logging()

        for key in SB_ENV_VARS:
            self.__setattr__(key.lower(), os.environ.get(key))

        if self.name:
            self.update()
        else:
            self.dbg("post init executed")
            self.logger.info("Executing post_init()")
            self.post_init()
            self.do("--update")
            self.dbg("Forcing update", "")

    @property
    def icon(self) -> str:
        return self._icon

    @icon.setter
    def icon(self, value: str) -> None:
        self.set_item(self.name, f"icon={value}")
        self._icon = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        value = value.strip("\n")
        self.set_item(self.name, f"label={value}")
        self._label = value

    def flatten(self, items):
        flat_list = []
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

    def dbg(self, action="", *args):
        self.logger.debug((self.name or "Sketchybar") + " : " + str(action) + " " + str(self.flatten(args)))

    def do(self, *args) -> int:
        self.dbg("    args:", args)
        cmd = self.flatten(["sketchybar"] + self.flatten([self.flatten(arg) for arg in args]))
        self.dbg("    runs", cmd)
        return subprocess.run(cmd, text=True, capture_output=True)

    def run(self, args: str):
        return subprocess.run(self.flatten(args), shell=True, text=True, capture_output=True)

    def add_item(self, name: str, position: str):
        self.dbg("adding item ", name, position)
        self.do("--add", "item", name, position)
        self.do("--set", name, f"script={self._}")
        self.dbg("    item added", name)

    def set_item(self, name: str, *properties):
        self.dbg("updating item", name)
        self.do("--set", name, self.flatten(properties))
        self.dbg("    item updated", name)

    def subscribe(self, name: str, *events):
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

    def item(position="left", icon="", label="", subscribe=[], update_freq=0, **kwargs):
        def inner_function(f):
            @wraps(f)
            def innermost_function(self):
                if self.name:
                    return f(self)
                else:
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
                                for property, value in val.items():
                                    self.dbg("    property", property, value)
                                    self.set_item(item_name, [f"{property}={value}"])

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
