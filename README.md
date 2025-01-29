# sketchybar-py

A Python library for configuring [SketchyBar](https://github.com/FelixKratz/SketchyBar) - a highly customizable macOS status bar replacement. This library allows you to configure your SketchyBar using Python instead of traditional bash scripting, making the configuration process more intuitive and maintainable.

## Features

- Configure SketchyBar using Python syntax instead of bash
- Define bar items as functions, combining creation and behavior in one place
- More structured and maintainable configuration approach
- Native Python integration with SketchyBar's functionality
- No external dependencies

## Prerequisites

- macOS
- [SketchyBar](https://github.com/FelixKratz/SketchyBar) installed
- Python 3.10+ or [uv](https://github.com/astral-sh/uv)

## Installation

### Option 1: Using with uv shebang (Recommended)

Add the following shebang declaration to the top of your script:

```python
#!/usr/bin/env -S uv run -q
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "sketchybar-py"
# ]
# ///
```

### Option 2: Manual Import

`pip install sketchybar-py`

## Usage

Add the following line to your `sketchybarrc`:
```bash
$CONFIG_DIR/sketchybar.py
```

Make the Python configuration file executable:
```bash
chmod +x sketchybar.py
```

## Example

Here's a complete example of `sketchybar.py` showing how to configure SketchyBar using sketchybar-py (with uv):

```python
#!/usr/bin/env -S uv run -q
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "sketchybar-py"
# ]
# ///

from sketchybar_py import Sketchybar

global_bar_properties = {
    "position": "top",
    "height": "24",
    "blur_radius": "0",
    "color": "0x44444444",
}

default_settings_for_new_items = {
    "padding_left": 5,
    "padding_right": 5,
    "icon.font": "FiraCode Nerd Font:Bold:12.0",
    "label.font": "FiraCode Nerd Font:Bold:12.0",
    "icon.color": "0xffffffff",
    "label.color": "0xffffffff",
    "icon.padding_left": 4,
    "icon.padding_right": 4,
    "label.padding_left": 4,
    "label.padding_right": 4,
}


class MyAwesomeSketchyBar(Sketchybar):
    def post_init(self):
        print("Init...")
        self.do("--bar", global_bar_properties)
        self.do("--default", default_settings_for_new_items)
        self.do("--hotload", "true")
        self.autoload()

    @Sketchybar.item(
        enabled=True,
        position="left",
        icon="",
        properties={"label.drawing": "off"}
    )
    def l0_chevron(self):
        pass

    @Sketchybar.item(
        position="left",
        icon="++",
        subscribe=["front_app_switched"],
        properties={"icon.drawing": "off"},
    )
    def l1_front_app(self):
        if self.sender == "front_app_switched":
            self.label = self.info

    @Sketchybar.item(
        position="right",
        update_freq=60,
        subscribe=["system_woke", "power_source_change"],
    )
    def r2_battery(self):
        percentage = (
            self.run("pmset -g batt | grep -Eo '\\d+%'").stdout.strip().rstrip("%")
        )
        charging = "AC Power" in self.run("pmset -g batt").stdout
        self.icon = "" if charging else "󱟟"
        self.label = percentage + "%"

    @Sketchybar.item(
        position="right",
        update_freq=10,
        properties={"icon.drawing": "off"}
    )
    def r1_clock(self):
        now = self.run("date '+%d/%m %H:%M'").stdout
        self.label = now

    @Sketchybar.item(
        position="center",
        properties={"icon.drawing": "off"},
        label="notch_placeholder_0",
    )
    def c0_notch(self):
        pass


if __name__ == "__main__":
    sb = MyAwesomeSketchyBar()
```

## API Reference

### Sketchybar Class
Main class for configuring SketchyBar.

#### Methods
- `post_init()`: Contains initial configuration settings and setup. Also item initialization occurs here.
- `do()`: Executes sketchybar with provided arguments.
- `run()`: Executes any shell command with arguments.
- `autoload()`: Finds *all* decorated methods in the class and runs them in *alphabetical* order.
  Alternatively, you can call them manually in `post_init()` in your preferred order.

### Decorators
- `@Sketchybar.item`: Define a new bar item with properties

#### Item Properties
Common properties that can be used in item definitions:
- `enabled`: True or False - used for `autoload()` control
- `position`: "left", "right", or "center".
- `update_freq`: Update frequency in seconds.
- `subscribe`: List of events to subscribe to.
- `properties`: Dictionary of additional properties.
- You can use any sketchybar item properties.

## License

This project is licensed under the MIT License

## Author

Dmitry Kuznetsov
- GitHub: [@dimentium](https://github.com/dimentium)

## Related

- [SketchyBar](https://github.com/FelixKratz/SketchyBar) - The original SketchyBar project
