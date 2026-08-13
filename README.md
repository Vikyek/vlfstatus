# vlfstatus / wlfstatus

Lightweight bash status bar generator for `i3bar` / `swaybar` using the i3bar JSON header protocol and Pango markup.

## Features

- **i3bar JSON Protocol Support**: Emits valid JSON stream for `i3bar` and `swaybar` status blocks.
- **Pango Markup Formatting**: Styled text with colors, font icons, and customizable separators (`//`).
- **Dynamic Color Scheme Integration**: Reads palette colors dynamically from `~/.cache/bar_colors.sh` with safe fallback defaults (`#FF0055`, `#0DCDCD`, `#FFFFFF`).
- **Wi-Fi Status Module**: Queries `nmcli` for active connection state (`wlp8s0`) with connected (`󰖩`) and disconnected (`󰤮`) icons.
- **Battery Status Module**: Dynamically monitors `/sys/class/power_supply/BAT0/capacity` with capacity thresholds and color-coded status icons (` `, ` `, ` `, ` `, ` `).
- **Date & Time Module**: Displays real-time formatted date and time (`󰃰 `).

## Configuration & Usage

### 1. Color Palette Integration
Create or update `~/.cache/bar_colors.sh` with your desired hex colors:

```bash
COLOR_WIFI="#FF0055"
COLOR_BAT_HIGH="#00FF7F"
COLOR_BAT_MID="#FFD700"
COLOR_BAT_LOW="#FF0055"
COLOR_TIME="#00E5FF"
COLOR_TEXT="#FFFFFF"
COLOR_SEP="#0DCDCD"
```

### 2. i3 / Sway Integration
In your `~/.config/i3/config` or `~/.config/sway/config`:

```i3config
bar {
    status_command /home/v/.local/bin/wlfstatus
    i3bar_command i3bar
    font pango:monospace 10
}
```

### 3. Manual Execution
Run directly from terminal:

```bash
./wlfstatus
```
