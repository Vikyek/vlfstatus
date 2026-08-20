# vlfstatus

> Lightweight, feature-packed bash status bar generator for `i3bar` and `swaybar` using the i3bar JSON header protocol and Pango markup. (Evolved from legacy `wlfstatus`).

## Overview

`vlfstatus` is a high-performance, minimal-dependency status generator script designed for Linux tiling window managers such as i3 and Sway. It produces a compliant `i3bar` JSON protocol stream enhanced with Pango rich text markup, custom color themes, dynamic device state polling, and Nerd Font iconography.

Originally created as `wlfstatus`, the project has evolved into `vlfstatus` while retaining full backwards compatibility via symbolic links (`wlfstatus -> vlfstatus`).

---

## Authored Advancements & Technical Features

- **i3bar JSON Protocol Compliance**: Emits standard `{ "version": 1 }` stream header followed by an infinite JSON block stream (`[{"full_text": "...", "markup": "pango"}]`).
- **Live AI Agent Quota Tracking**: Integrates a background daemon (`fetch_quota.py`) that securely reads Antigravity tokens from Linux Secret Service (via keyring) and queries Google Cloud Code APIs, displaying remaining 5-hour Gemini/Claude quotas and reset timers.
- **Pango Rich Text Markup**: Supports inline styling with custom colors and styled section separators (`//`).
- **Dynamic Theme Cache Integration**: Sourced dynamically from `~/.cache/bar_colors.sh` on every iteration, enabling real-time color scheme updates with built-in fallback hex color tokens (`COLOR_WIFI`, `COLOR_BAT_HIGH`, `COLOR_BAT_MID`, `COLOR_BAT_LOW`, `COLOR_TIME`, `COLOR_TEXT`, `COLOR_SEP`).
- **Robust Wi-Fi State Detection**: Automatically inspects wireless connection status on `wlp8s0` via `nmcli`, displaying active connection names or disconnected states alongside Nerd Font wireless icons (`󰤨` / `󰤭` and `󰖩` / `󰤮`).
- **Adaptive Battery Monitoring**: Directly monitors `/sys/class/power_supply/BAT0/capacity` with fallback handling (`echo 100`), 5-stage capacity icons (` `, ` `, ` `, ` `, ` `), and dynamic color thresholds (`COLOR_BAT_HIGH`, `COLOR_BAT_MID`, `COLOR_BAT_LOW`).
- **Date & Time Module**: Displays real-time formatted date and time (`%d %a %H:%M:%S`) with Nerd Font calendar icon (`󰃰`).
- **Backwards Compatibility**: Includes symlink support for existing `wlfstatus` configurations so legacy status bar setups operate seamlessly.

---

## Installation & Setup

### 1. Repository Setup & Binary Installation

Copy `vlfstatus` to your local binary directory (`~/.local/bin/`) and establish the backwards-compatible symlink:

```bash
# Clone or navigate to the repository
cd ~/Projects/vlfstatus

# Install primary executable and backwards-compatible symlink
cp vlfstatus ~/.local/bin/vlfstatus
chmod 755 ~/.local/bin/vlfstatus
ln -sf vlfstatus ~/.local/bin/wlfstatus
```

Ensure `~/.local/bin` is in your shell `$PATH`.

---

## Configuration

### 1. Dynamic Theme Cache (`~/.cache/bar_colors.sh`)

`vlfstatus` dynamically sources `~/.cache/bar_colors.sh` at each cycle interval. Create or edit `~/.cache/bar_colors.sh` to customize your color palette:

```bash
COLOR_WIFI="#FF0055"
COLOR_BAT_HIGH="#00FF7F"
COLOR_BAT_MID="#FFD700"
COLOR_BAT_LOW="#FF0055"
COLOR_TIME="#00E5FF"
COLOR_TEXT="#FFFFFF"
COLOR_SEP="#0DCDCD"
```

*Note: If `~/.cache/bar_colors.sh` is absent, safe default fallback colors are automatically applied.*

### 2. i3 / Sway Window Manager Integration

Update your `~/.config/i3/config` or `~/.config/sway/config` file to use `vlfstatus` (or `wlfstatus` for legacy setups):

```i3config
bar {
    status_command $HOME/.local/bin/vlfstatus
    i3bar_command i3bar
    font pango:monospace 10
}
```

*Backwards compatibility note:* If your i3 bar configuration uses `status_command $HOME/.local/bin/wlfstatus` or `status_command $HOME/.local/bin/vlfstatus`, both path options execute the updated script identically via the symlink.

---

## Manual Testing & Verification

To verify that `vlfstatus` produces a clean JSON stream, execute the script directly in your terminal:

```bash
# Direct execution
~/.local/bin/vlfstatus

# Or test via backwards-compatible symlink
~/.local/bin/wlfstatus
```

**Expected Stream Output:**
```json
{ "version": 1 }
[
[]
,[{"full_text": " <span color='#0DCDCD'>//</span> <span color='#FF0055'>󰖩 </span><span color='#FFFFFF'>wifi_name</span> <span color='#0DCDCD'>//</span> <span color='#FF0055'> </span><span color='#FFFFFF'>100%</span> <span color='#0DCDCD'>//</span> <span color='#FF0055'>󰃰 </span><span color='#FFFFFF'>13 Thu 04:58:00</span> ", "markup": "pango"}]
```

Press `Ctrl+C` to stop execution.
