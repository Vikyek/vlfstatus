## 2024-05-24 - Battery Charging Indicator
**Learning:** Users experience anxiety when checking battery capacity if they are unsure if the device is actively charging, even when plugged in. A raw percentage or static battery icon doesn't communicate the charging state clearly.
**Action:** Always include a distinct visual indicator (e.g., a lightning bolt or charging icon) when a device is actively receiving power.
## 2026-09-01 - Dynamic Volume Icons for Status Bar
**Learning:** For continuous numeric readouts (like volume levels), users benefit from discrete visual cues representing varying magnitude thresholds (high, medium, low) rather than a single static icon.
**Action:** When displaying system or environment values (e.g., volume, battery, brightness), check if existing single icons can be split into multi-state icons to improve scannability without relying solely on the text readout.
## 2026-09-02 - Preserve Contextual Values Behind States
**Learning:** Hiding continuous values (like volume percentage) when entering a binary override state (like muted) creates user anxiety, as they lose context of what will happen when the state is toggled off.
**Action:** Always maintain the display of underlying numeric or continuous state values even when a binary override state is active.
## 2024-10-03 - Granular Charging Feedback
**Learning:** A single generic "Charging" icon lacks the context users need when their device is charging but they don't want to rely solely on the numerical text percentage. Showing an indicator that combines the 'charging' status with a visual capacity estimate is significantly more informative.
**Action:** When creating status displays that contain multi-dimensional variables (like charging status + capacity), attempt to use icons that communicate both variables simultaneously to reduce cognitive load.
## 2026-10-04 - Consistent AC Power Indication
**Learning:** Users can become anxious if they lose visual confirmation of external power when a device stops actively charging (e.g., reaches "Full" or "Not charging" due to a battery threshold). Group 'Charging', 'Full', and 'Not charging' states under the same 'plugged in' visual indicators to maintain consistent UX and prevent false alarms.
**Action:** Ensure the "plugged-in" visual state applies not just when actively charging, but whenever the device is receiving external power.
## 2026-09-06 - Progressive Stale Data Indicators
**Learning:** When displaying data fetched asynchronously, simply showing the data age text (e.g., "5m ago") isn't enough. Users may not notice the text updating or understand when the delay indicates a background task failure versus a normal polling interval.
**Action:** Use progressive color cues (e.g., shifting from normal to warning to critical colors) mapped to specific time thresholds to provide pre-attentive feedback about stale asynchronous data.
## 2024-10-07 - Contextual Warning Colors for Disconnected States
**Learning:** Hard-coded warning text for disconnected states (e.g., "Not connected") can be overwhelming in bright or contrasting colors like white, adding to visual noise rather than clear communication.
**Action:** Use dim or subtle colors for the text of a disconnected state to reduce visual noise, and reserve attention-grabbing colors (like red/critical) specifically for the icon itself to indicate the lack of connectivity at a glance.
## 2025-02-12 - Dim Text for Disabled/Muted States
**Learning:** Using high-contrast text for disabled or disconnected states (like a muted volume indicator) adds visual noise and competes with other active status elements.
**Action:** Use dim or subtle colors for the text of muted or disconnected states, reserving warning colors specifically for the icon. This establishes a clear visual hierarchy and reduces visual clutter.
## 2024-11-20 - Prevent Layout Jitter in High-Frequency Updates
**Learning:** In dynamically updating UI components like status bars, displaying unpadded countdown timers (e.g., `5m9s` to `5m10s`) causes the string width to change. This forces all subsequent elements in the layout to continuously jump back and forth, creating distracting visual noise.
**Action:** Always zero-pad continuously updating numeric time units (minutes, seconds) to ensure a consistent character width and stable layout.

## 2026-09-12 - Prevent Layout Jitter in High-Frequency Updates
**Learning:** In dynamically updating UI components like status bars, displaying unpadded countdown timers causes the string width to change. This forces all subsequent elements in the layout to continuously jump back and forth, creating distracting visual noise.
**Action:** Always zero-pad continuously updating numeric time units (minutes, seconds) to ensure a consistent character width and stable layout.

**Action:** Always format dates using a natural semantic order (e.g., "Mon 16 Sep") to reduce cognitive load and improve scannability.
## 2026-09-16 - Natural Semantic Date Ordering
**Learning:** Formatting dates in concise UI components like status bars with unnatural ordering (e.g., "16 Mon") increases cognitive parsing effort as users are accustomed to natural language phrasing.
**Action:** When displaying dates in tight UI components, prefer natural semantic ordering (e.g., "Mon 16 Sep") to minimize cognitive load.
## 2024-09-27 - Volume Over-Amplification Warning
**Learning:** Users lack immediate visual feedback when audio volume is pushed beyond 100%, which can lead to clipping, distortion, or hardware strain.
**Action:** Apply warning colors (e.g., $COLOR_BAT_LOW) to the volume icon when output exceeds 100% to clearly indicate over-amplification risks.
## 2024-09-28 - Semantic Default Colors
**Learning:** Hardcoding all default fallback theme colors to a critical/warning color (like pure red) creates visual fatigue and false alarms, forcing users to constantly check if there is an actual problem or just a missing configuration file.
**Action:** Always provide semantically appropriate default colors (e.g., green for healthy battery, neutral colors for time) to ensure the interface is immediately usable and informative even before user customization.
## 2024-10-15 - Rejected UX Change: Wi-Fi Default Color
**Learning:** A proposed change to alter the default fallback Wi-Fi color from `#FF0055` (red) to a neutral/safe color (like cyan) was explicitly rejected by the user. The design constraint dictates that the default Wi-Fi color *must* remain red to serve a specific, intended purpose in the interface, likely as a clear visual indicator that the user is relying on fallback configurations rather than a fully customized setup.
**Action:** Do not attempt to change the default fallback colors (e.g., `COLOR_WIFI="#FF0055"`) in `vlfstatus` unless explicitly prompted by the user to do so.
