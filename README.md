# wezterm-color-profiles
Get all the color schemes. This script clones both the [iTerm2-Color-Schemes](https://github.com/mbadolato/iTerm2-Color-Schemes) and [kitty-themes](https://github.com/kovidgoyal/kitty-themes) repositories and converts all of their themes into a single JSON file that can be ingested by WezTerm.

## Usage
```
usage: to-wezterm.py [-h] [-i] [-k] [-a] [-o OUTFILE]

Convert iTerm2 and/or Kitty Term color themes to a format WezTerm can read

options:
  -h, --help            show this help message and exit
  -i, --iterm2          Convert iTerm2 color themes
  -k, --kitty           Convert Kitty term color themes
  -a, --all             Convert both iTerm2 and Kitty term color themes
  -o, --outfile OUTFILE
                        Specify an output filename
```

## Ingesting in WezTerm
This is a simplified version of how I do it. Please see the full repo [here](https://github.com/gdanko/wezterm-light) for details.

`user_config`
```lua
{
    "display": {
        "color_scheme": {
            "enable_gradient": false,
            "randomize_color_scheme": false,
            "scheme_name": "1984 Dark",
        },
        "initial_cols": 132,
        "initial_rows": 40,
        "tab_bar_font": {
            "family": "Roboto",
            "size": 10,
            "stretch": "Condensed",
            "weight": "Bold",
        },
        "terminal_font": {
            "family": "Noto Sans Mono",
            "size": 10,
            "stretch": "Normal",
            "weight": "Regular",
        },
        "window_background_opacity": 1,
        "window_padding": {
            "bottom": 0,
            "left": 10,
            "right": 20,
            "top": 0,
        },
    },
    "keymod": "SHIFT|CTRL",
    "os_name": "linux",
    "tabs": {
        "title_is_cwd": true,
    },
}
```

`wezterm.lua`
```lua
local color_config = require "color-config"

color_scheme_map = color_config.get_color_scheme(
    user_config.display.color_scheme.scheme_name,
    user_config.display.color_scheme.randomize_color_scheme
)
```

`color-config.lua`
```lua
local color_scheme_map = {}
local schemes_filename = util.path_join({wezterm.config_dir, "wezterm-color-schemes.json"})
local all_color_schemes = util.json_parse_file(schemes_filename)
if all_color_schemes[scheme_name] ~= nil then
    scheme = all_color_schemes[scheme_name]
    color_scheme_map = {
        ansi         = scheme.ansi,
        background   = scheme.background,
        brights      = scheme.brights,
        cursor_bg    = scheme.cursor_bg,
        cursor_fg    = scheme.cursor_fg,
        foreground   = scheme.foreground,
        selection_bg = scheme.selection_fg,
        selection_fg = scheme.selection_bg,
    }
else
    color_scheme_map = default_color_scheme
end

return color_config
```

