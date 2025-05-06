class Constants:
    SB_ENV_VARS: list[str] = [
        '_',
        'BAR_NAME',
        'INFO',
        'NAME',
        'SENDER',
        'CONFIG_DIR',
        'BUTTON',
        'MODIFIER',
        'SCROLL_DELTA',
    ]

    global_bar_properties = {
        'position': 'top',
        'height': '28',
        'blur_radius': '20',
        'color': '0xdd222222',
        'padding_right': 4,
        'padding_left': 4,
        'corner_radius': 9,
        'y_offset': 3,
        'margin': 3,
    }

    default_settings_for_new_items = {
        'background.color': '0x99777777',
        'background.corner_radius': 5,
        'background.height': 18,
        'padding_left': 3,
        'padding_right': 3,
        'icon.font': 'sketchybar-app-font:Regular:16.0',
        'label.font': 'FiraCode Nerd Font:Bold:12.0',
        'icon.color': '0xffffffff',
        'label.color': '0xffffffff',
        'icon.padding_left': 6,
        'icon.padding_right': 6,
        'label.padding_left': 4,
        'label.padding_right': 4,
    }
