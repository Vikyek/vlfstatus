#!/bin/bash
set -e

echo "Installing vlfstatus..."

# 1. Check for legacy configuration files and migrate them
CONFIG_SRC=""
if [ -f "$HOME/.config/wlfstatus/config" ]; then
    CONFIG_SRC="$HOME/.config/wlfstatus/config"
elif [ -f "$HOME/.wlfstatusrc" ]; then
    CONFIG_SRC="$HOME/.wlfstatusrc"
fi

if [ -n "$CONFIG_SRC" ]; then
    echo "Found legacy configuration at $CONFIG_SRC. Migrating..."
    # Ensure the new config directory exists
    mkdir -p "$HOME/.config/vlfstatus"
    
    # Read variables from old config and map them to vlfstatus variables
    {
        echo "# Migrated from legacy wlfstatus config"
        while IFS= read -r line || [ -n "$line" ]; do
            # Replace WLF_COLOR_ with COLOR_
            if [[ "$line" =~ ^WLF_COLOR_ ]]; then
                echo "${line#WLF_}"
            else
                echo "$line"
            fi
        done < "$CONFIG_SRC"
    } > "$HOME/.config/vlfstatus/config"
    
    echo "Migration completed: variables saved to $HOME/.config/vlfstatus/config"
fi

# 2. Update i3 status command configuration to use vlfstatus instead of wlfstatus
I3_CONFIG="$HOME/.config/i3/config"
if [ -f "$I3_CONFIG" ]; then
    if grep -q "status_command.*wlfstatus" "$I3_CONFIG"; then
        echo "Updating i3 status command in $I3_CONFIG..."
        sed -i 's/status_command.*wlfstatus/status_command $HOME\/.local\/bin\/vlfstatus/g' "$I3_CONFIG"
    fi
fi

# 3. Remove old wlfstatus symlink or binary
if [ -e "$HOME/.local/bin/wlfstatus" ] || [ -L "$HOME/.local/bin/wlfstatus" ]; then
    echo "Removing legacy wlfstatus executable..."
    rm -f "$HOME/.local/bin/wlfstatus"
fi

# 4. Install the new vlfstatus script and quota daemon
mkdir -p "$HOME/.local/bin"
cp -f vlfstatus "$HOME/.local/bin/vlfstatus"
chmod +x "$HOME/.local/bin/vlfstatus"
cp -f fetch_quota.py "$HOME/.local/bin/fetch_quota.py"
chmod +x "$HOME/.local/bin/fetch_quota.py"
echo "vlfstatus script and quota daemon installed to $HOME/.local/bin/"

# 5. Reload/restart i3 status bar
echo "Restarting i3 wm/bar to apply changes..."
# Find active i3 socket
I3_SOCKET=$(ls -1 /run/user/$(id -u)/i3/ipc-socket.* 2>/dev/null | head -n 1 || true)
if [ -S "$I3_SOCKET" ]; then
    i3-msg -s "$I3_SOCKET" restart || true
else
    i3-msg restart || true
fi

echo "vlfstatus installation and migration completed successfully!"
