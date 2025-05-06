import inspect
import json
import logging
import subprocess
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, List, Literal, Optional, TypeAlias, Union

from pydantic import BaseModel

from .__about__ import __version__
from .core import Bar, Constants, SBEvent, SBItem, SBItemRaw, flat_list, init_logging, onoff

PropertyValue: TypeAlias = Union[str, int, float]
Properties: TypeAlias = Dict[str, PropertyValue]


class Sketchybar(BaseModel):
    _event: SBEvent
    _item: SBItem = SBItem()
    _icon: str | None
    _label: str | None
    _logger: logging.Logger

    def __init__(self, _debug: bool = False, **data: Any):
        super().__init__(**data)
        self._logger = init_logging(_debug)
        self._event = SBEvent()

        if not self.event.name:
            self._logger.info(f'Loading {inspect.stack()[1].filename} using Sketchybar-py  version {__version__}')
            bar = data.get('bar', Constants.global_bar_properties)
            default = data.get('default', Constants.default_settings_for_new_items)
            self.do('--bar', bar)
            self.do('--default', default)

            self.post_init()
            self.do('--update')
        else:
            self.update(self.event)

    def post_init(self) -> None:
        pass

    @property
    def event(self):
        return self._event

    @property
    def name(self) -> str:
        return self.event.name

    @property
    def item(self) -> SBItem:
        if self.name and not self._item.name:
            self._item._raw = self.get_item(self.name)  # type: ignore
        return self._item

    @property
    def drawing(self) -> Literal['on', 'off'] | None:
        return self._item.geometry.drawing

    @drawing.setter
    def drawing(self, value: Any) -> None:
        self.set_item(self.name, f'drawing={onoff(value)}')

    @property
    def icon(self) -> str | None:
        return self._icon

    @icon.setter
    def icon(self, value: str) -> None:
        visible = 'icon.drawing=on' if value else 'icon.drawing=off'
        self.set_item(self.name, f'icon={value}', visible)
        self._icon = value

    @property
    def label(self) -> str | None:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        visible = 'label.drawing=on' if value else 'label.drawing=off'
        self.set_item(self.name, f'label={value}', visible)
        self._label = value

    def dbg(self, action: str = '', *args: Any) -> None:
        self._logger.debug(f'{action} {flat_list(args)}')

    def do(self, *args: int | str | dict[Any, Any] | list[Any]) -> Any:
        self.dbg('do:')
        self.dbg('-- args:', args)
        cmd = flat_list(['sketchybar'] + flat_list([flat_list(arg) for arg in args]))
        self.dbg('-- cmd:', cmd)
        return subprocess.run(cmd, text=True, capture_output=True)

    def run(self, args: str) -> Any:
        return subprocess.run(flat_list(args), shell=True, text=True, capture_output=True)

    def add_item(self, name: str, position: str) -> None:
        self.do('--add', 'item', name, position)

    def set_item(self, name: str | None = None, *properties: Any) -> None:
        name = name if name else self.name
        self.do('--set', name, flat_list(properties))

    def get_item(self, name: str | None = None) -> SBItemRaw:
        name = name if name else self.name
        if name:
            result = SBItemRaw(**json.loads(self.do('--query', name).stdout.strip('\n')))
            return result
        return SBItemRaw()

    def get_bar(self) -> Bar:
        bar = json.loads(self.do('--query', 'bar').stdout.strip('\n'))
        return Bar(**bar)

    def subscribe(self, name: str, *events: str | list[str]) -> None:
        self.do('--subscribe', name, flat_list(events))

    def update(self, event: SBEvent):
        method = getattr(self, event.name, None)
        if callable(method):
            return method()

    # decorator
    @staticmethod
    def AddItem(
        enabled: Optional[bool] = True,
        position: str = 'left',
        icon: str = '',
        label: str = '',
        script: str = '',
        subscribe: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        def inner_function(f: Any) -> Any:
            @wraps(f)
            def innermost_function(self: Any) -> None:
                if self.name:
                    return f(self)
                elif not enabled:
                    return

                item_name = f.__name__
                self.add_item(item_name, position)

                if subscribe:
                    self.subscribe(item_name, subscribe)

                if len(kwargs):
                    self.dbg('additional arguments', len(kwargs))
                    for key, val in kwargs.items():
                        if key == 'properties' and isinstance(val, dict):
                            properties: Properties = val
                            properties['icon'] = properties.get('icon', icon)
                            properties['label'] = properties.get('label', label)
                            properties['script'] = script if script else self.event.script

                            properties_parsed: list[PropertyValue] = list()

                            for property_name, value in properties.items():
                                properties_parsed.append(f'{property_name}={value}')

                            self.set_item(item_name, properties_parsed)

            return innermost_function

        return inner_function

    def wrapped_methods(self):
        return inspect.getmembers(self, predicate=lambda x: callable(x) and hasattr(x, '__wrapped__'))

    def autoload(self):
        self.dbg('autoload initiated. items detected:', len(self.wrapped_methods()))
        for name, method in self.wrapped_methods():
            self.dbg('try to load:', name)
            method()

    def animate(
        self,
        name: str | None = None,
        curve: str = 'linear',
        duration: int = 10,
        animation: str = 'label.color.alpha=0.0',
        wait: bool = True,
    ) -> None:
        name = name if name else self.name
        self.run(f'sketchybar --animate {curve} {duration} --set {name} {animation}')
        if wait:
            time.sleep(duration / 60 * 1.1)

    @contextmanager
    def animation(
        self,
        curve: str = 'linear',
        duration: int = 6,
        before: str = 'label.color.alpha=0.0',
        after: str = 'label.color.alpha=1.0',
    ) -> Any:
        try:
            self.animate(curve=curve, duration=duration, animation=before)
            yield
        finally:
            self.animate(curve=curve, duration=duration, animation=after)
            pass
