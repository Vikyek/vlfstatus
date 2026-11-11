# vlfstatus

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Sponsor Vikyek](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=github-sponsors&logoColor=white)](https://github.com/sponsors/Vikyek)

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

## Dependencies

### Mandatory Dependencies
The core script features require the following tools:
- **`bash`**: Core runtime interpreter.
- **`networkmanager`**: Provides `nmcli` for Wi-Fi SSID and state tracking.
- **`libpulse`**: Provides `pactl` for master volume/mute level querying.

### Optional Dependencies
To enable the **AI Agent Quota Tracker** (`fetch_quota.py`) module:
- **`python`**: Runs the daemon process.
- **`python-secretstorage`**: Reads token authentication credentials securely from your desktop's keyring.
- **`agy-cli`**: Required to enable quota tracking (the status bar will hide the module entirely if `agy` is not installed on the system).

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

---

## 💖 Support & Sponsorship

`vlfstatus` is authored and maintained by **[Vikyek](https://github.com/Vikyek)** as an independent open-source project. Everything is 100% open-source, telemetry-free, and public.

<div align="center">

<!-- Official GitHub Sponsors Button & Card (Rendered in web/HTML environments; GitHub markdown sanitizer strips iframes, falling back to native badges) -->
<iframe src="https://github.com/sponsors/Vikyek/button" title="Sponsor Vikyek" height="32" width="114" style="border: 0; border-radius: 6px;"></iframe>
<iframe src="https://github.com/sponsors/Vikyek/card" title="Sponsor Vikyek" height="225" width="600" style="border: 0;"></iframe>

[![Sponsor Vikyek](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa?logo=github&style=for-the-badge)](https://github.com/sponsors/Vikyek)
[![Donate on Liberapay](https://img.shields.io/badge/Donate-Liberapay-f6c915?style=for-the-badge&logo=liberapay&logoColor=black)](https://liberapay.com/Vikyek)
[![Sponsor on Polar](https://img.shields.io/badge/Sponsor-Polar-0062FF?style=for-the-badge&logo=polar&logoColor=white)](https://polar.sh/vikyek)
[![Donate with Stripe](https://img.shields.io/badge/Donate-Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://profile.stripe.com/@vikyek)

</div>

> ### 🎯 Active Sponsorship Goal: Monthly Living Essentials
> **Target:** **2,710 PLN / ~$675 USD per month** (`630 PLN / week`) — Rent & Essential Utilities  
> Covering basic living essentials directly unlocks dedicated, sustainable full-time independent open-source engineering across desktop environment tooling and Linux system utilities free from corporate telemetry, ads, or paywalls.

If `vlfstatus` powers your desktop status bar, consider supporting ongoing work:

- **GitHub Sponsors**: [github.com/sponsors/Vikyek](https://github.com/sponsors/Vikyek) *(Monthly tiers and one-time tips)*
- **Liberapay**: [liberapay.com/Vikyek](https://liberapay.com/Vikyek) *(0% platform fee recurrent patronage in EUR/USD/PLN)*
- **Polar**: [polar.sh/vikyek](https://polar.sh/vikyek) *(Developer subscriptions & commercial passes)*
- **Direct Stripe Profile**: [profile.stripe.com/@vikyek](https://profile.stripe.com/@vikyek) *(Direct one-time tips & sponsorship)*

Every contribution—monthly or one-time—directly supports active maintenance, hardware testbeds, and new feature development!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

