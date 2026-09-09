#!/bin/bash
set -e

# Color setup supporting NO_COLOR
if [ -z "${NO_COLOR}" ] && [ -t 1 ]; then
    C_RESET='\033[0m'
    C_INFO='\033[1;34m'
    C_SUCCESS='\033[1;32m'
    C_WARN='\033[1;33m'
    C_ERROR='\033[1;31m'
    C_BOLD='\033[1m'
    C_DIM='\033[2m'
else
    C_RESET=''
    C_INFO=''
    C_SUCCESS=''
    C_WARN=''
    C_ERROR=''
    C_BOLD=''
    C_DIM=''
fi

step() { echo -e "${C_DIM}---${C_RESET}\n${C_BOLD}$*${C_RESET}"; }
info() { echo -e "  ${C_INFO}•${C_RESET} $*"; }
success() { echo -e "  ${C_SUCCESS}✔${C_RESET} $*"; }
warn() { echo -e "  ${C_WARN}⚠${C_RESET} $*"; }
error() { echo -e "  ${C_ERROR}✖ ERROR:${C_RESET} $*" >&2; }

trap 'error "Installation failed at line $LINENO (exit code $?)"' ERR

echo -e "\n${C_BOLD}🚀 Starting vlfstatus installation${C_RESET}"

step "1. Legacy Configuration"
# 1. Check for legacy configuration files and migrate them
CONFIG_SRC=""
if [ -f "$HOME/.config/wlfstatus/config" ]; then
    CONFIG_SRC="$HOME/.config/wlfstatus/config"
elif [ -f "$HOME/.wlfstatusrc" ]; then
    CONFIG_SRC="$HOME/.wlfstatusrc"
fi

if [ -n "$CONFIG_SRC" ]; then
    step "Configuration Migration"
    info "Found legacy configuration at ${C_BOLD}$CONFIG_SRC${C_RESET}. Migrating..."
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
    success "Migration completed: variables saved to ${C_BOLD}$HOME/.config/vlfstatus/config${C_RESET}"
else
    info "No legacy config found, skipping."
fi

step "2. i3 / Sway Integration"
# 2. Update i3 status command configuration to use vlfstatus instead of wlfstatus
I3_CONFIG="$HOME/.config/i3/config"
if [ -f "$I3_CONFIG" ]; then
    if grep -q "status_command.*wlfstatus" "$I3_CONFIG"; then
        step "Updating Window Manager Config"
        info "Updating i3 status command in ${C_BOLD}$I3_CONFIG${C_RESET}..."
        sed -i 's/status_command.*wlfstatus/status_command $HOME\/.local\/bin\/vlfstatus/g' "$I3_CONFIG"
        success "Updated i3 config"
    else
        info "No legacy wlfstatus command found in i3 config."
    fi
else
    info "No i3 config found at ${C_BOLD}$I3_CONFIG${C_RESET}."
fi

step "3. Legacy Binaries"
# 3. Remove old wlfstatus symlink or binary
if [ -e "$HOME/.local/bin/wlfstatus" ] || [ -L "$HOME/.local/bin/wlfstatus" ]; then
    step "Cleanup Legacy Executable"
    info "Removing legacy wlfstatus executable..."
    rm -f "$HOME/.local/bin/wlfstatus"
    success "Cleaned up old binaries"
else
    info "No old binaries to remove."
fi

step "4. Core Installation"
# 4. Install the new vlfstatus script and quota daemon
info "Copying binaries..."
mkdir -p "$HOME/.local/bin"
cp -f vlfstatus "$HOME/.local/bin/vlfstatus"
chmod +x "$HOME/.local/bin/vlfstatus"
cp -f fetch_quota.py "$HOME/.local/bin/fetch_quota.py"
chmod +x "$HOME/.local/bin/fetch_quota.py"
success "Scripts installed to ${C_BOLD}$HOME/.local/bin/${C_RESET}"

step "5. Service Restart"
# 5. Reload/restart i3 status bar
info "Restarting i3 wm/bar to apply changes..."
# Find active i3 socket
I3_SOCKET=$(ls -1 /run/user/$(id -u)/i3/ipc-socket.* 2>/dev/null | head -n 1 || true)
if [ -S "$I3_SOCKET" ]; then
    i3-msg -s "$I3_SOCKET" restart >/dev/null 2>&1 || true
    success "Restarted via socket"
else
    i3-msg restart >/dev/null 2>&1 || true
    success "Restarted via generic command"
fi

echo -e "\n${C_SUCCESS}✨ vlfstatus setup completed successfully!${C_RESET}\n"
