from pydantic import BaseModel
from typing import Literal, Optional


class ARGB(BaseModel):
    value: int = 0
    alpha: int = 255
    red: int = 255
    green: int = 255
    blue: int = 255

    def __init__(self, value: int | str, **data):
        """
        Initialize ARGB color.
        Accepts int (0x11223344) or str ('#11223344' or '11223344')
        """
        if isinstance(value, str):
            value = int(value.replace("#", ""), 16)

        processed_value = value & 0xFFFFFFFF  # Ensure 32-bit value
        super().__init__(value=processed_value, **data)

    # def __init__(self, value: int | str):
    #     """
    #     Initialize ARGB color.
    #     Accepts int (0x11223344) or str ('#11223344' or '11223344')
    #     """
    #     if isinstance(value, str):
    #         # Remove '#' if present and convert to int
    #         value = int(value.replace('#', ''), 16)

    #     self._value = value & 0xFFFFFFFF  # Ensure 32-bit value


#     @property
#     def alpha(self) -> int:
#         """Alpha channel (0-255)"""
#         return (self._value >> 24) & 0xFF

#     @property
#     def red(self) -> int:
#         """Red channel (0-255)"""
#         return (self._value >> 16) & 0xFF

#     @property
#     def green(self) -> int:
#         """Green channel (0-255)"""
#         return (self._value >> 8) & 0xFF

#     @property
#     def blue(self) -> int:
#         """Blue channel (0-255)"""
#         return self._value & 0xFF

#     @property
#     def rgb(self) -> tuple[int, int, int]:
#         """Returns (red, green, blue) tuple"""
#         return (self.red, self.green, self.blue)

#     @property
#     def rgba(self) -> tuple[int, int, int, int]:
#         """Returns (red, green, blue, alpha) tuple"""
#         return (self.red, self.green, self.blue, self.alpha)

#     def __str__(self) -> str:
#         """Returns color in #AARRGGBB format"""
#         return f"#{self._value:08x}"

#     def __repr__(self) -> str:
#         return f"ARGB('{str(self)}')"

#     def __eq__(self, other: Any) -> bool:
#         if isinstance(other, ARGB):
#             return self._value == other._value
#         return False

#     def __int__(self) -> int:
#         """Returns color as integer"""
#         return self._value

#     @classmethod
#     def from_rgba(cls, red: int, green: int, blue: int, alpha: int = 255) -> 'ARGB':
#         """Create ARGB from individual components"""
#         value = (alpha << 24) | (red << 16) | (green << 8) | blue
#         return cls(value)


class Bar(BaseModel):
    color: str
    border_color: str
    position: Literal["top", "bottom"] = "top"
    height: int = 25
    notch_display_height: int = 0
    margin: int = 0
    y_offset: int = 0
    corner_radius: int = 0
    border_width: int = 0
    blur_radius: int = 0
    padding_left: int = 0
    padding_right: int = 0
    notch_width: int = 200
    notch_offset: int = 0
    display: Literal["main", "all"] | list[int] = "main"

    hidden: Literal["on", "off", "current"]
    topmost: Literal["on", "off", "window"]
    sticky: Literal["on", "off"]
    font_smoothing: Literal["on", "off"]
    shadow: Literal["on", "off"]

    show_in_fullscreen: Literal["on", "off"]
    drawing: Literal["on", "off"]

    items: Optional[list[str]] = None
