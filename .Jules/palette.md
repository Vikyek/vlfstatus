## 2024-05-24 - Battery Charging Indicator
**Learning:** Users experience anxiety when checking battery capacity if they are unsure if the device is actively charging, even when plugged in. A raw percentage or static battery icon doesn't communicate the charging state clearly.
**Action:** Always include a distinct visual indicator (e.g., a lightning bolt or charging icon) when a device is actively receiving power.
## 2026-09-01 - Dynamic Volume Icons for Status Bar
**Learning:** For continuous numeric readouts (like volume levels), users benefit from discrete visual cues representing varying magnitude thresholds (high, medium, low) rather than a single static icon.
**Action:** When displaying system or environment values (e.g., volume, battery, brightness), check if existing single icons can be split into multi-state icons to improve scannability without relying solely on the text readout.
## 2026-09-02 - Preserve Contextual Values Behind States
**Learning:** Hiding continuous values (like volume percentage) when entering a binary override state (like muted) creates user anxiety, as they lose context of what will happen when the state is toggled off.
**Action:** Always maintain the display of underlying numeric or continuous state values even when a binary override state is active.
