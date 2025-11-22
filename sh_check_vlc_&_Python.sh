#!/bin/bash
#
# Script: check_dependencies.sh
# Description: Detects the Linux distribution and checks if VLC, Python 3,
#              PIP, and the Python-VLC binding development headers are installed.

# --- Configuration ---
# Define the package names, which may vary slightly across distributions
VLC_PKG="vlc"
# The 'dev' or 'headers' package is crucial for the 'pip install python-vlc' to succeed.
VLC_DEV_PKG_DEB="libvlc-dev"
VLC_DEV_PKG_RPM="libvlc-devel" # Often 'libvlc-devel' on RPM-based systems
VLC_DEV_PKG_ARCH="vlc" # On Arch, the main 'vlc' package often includes dev files

PYTHON_PKG="python3"
PIP_PKG_DEB="python3-pip"
PIP_PKG_RPM="python3-pip"
PIP_PKG_ARCH="python-pip"

# --- Helper Functions ---

# Function to display status
status_check() {
    local name=$1
    local is_installed=$2
    local install_cmd=$3
    local description=$4

    if [ "$is_installed" -eq 0 ]; then
        echo -e "\n✅ $name is INSTALLED."
    else
        echo -e "\n❌ $name is NOT INSTALLED. Package needed: ${description}. Resolve by running:"
        echo -e "   > $install_cmd"
        # Special note for Python-VLC installation
        if [[ "$name" == "VLC Development/Headers" ]]; then
            echo -e "   (Required by 'pip install python-vlc' for successful compilation.)"
        elif [[ "$name" == "Python-VLC Binding (pip check)" ]]; then
             echo -e "   (If other checks passed, run: 'pip install python-vlc')"
        fi
    fi
}

# --- Distribution Detection ---

echo "--- System & Dependency Check ---"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    # Use ID_LIKE if ID is not specific enough (e.g., Mint -> debian)
    ID=${ID_LIKE:-$ID}
    echo "Detected Distribution: $PRETTY_NAME"
else
    echo "Error: Cannot determine Linux distribution. Exiting."
    exit 1
fi

echo "Using primary package ID: $ID"
echo "----------------------------------"

# --- Check Function for Debian/Ubuntu (using dpkg) ---
check_debian() {
    echo "Checking dependencies using 'dpkg' (Debian/Ubuntu/Mint/etc...)"
    local vlc_status vlc_dev_status python_status pip_status

    # 1. Check VLC
    dpkg -s "$VLC_PKG" >/dev/null 2>&1
    vlc_status=$?
    status_check "VLC Core Libraries" $vlc_status "sudo apt install $VLC_PKG" "VLC Media Player and its essential runtime libraries ($VLC_PKG)"

    # 2. Check VLC Development Headers (required for 'pip install python-vlc')
    dpkg -s "$VLC_DEV_PKG_DEB" >/dev/null 2>&1
    vlc_dev_status=$?
    status_check "VLC Development/Headers" $vlc_dev_status "sudo apt install $VLC_DEV_PKG_DEB" "Header files for compiling Python bindings ($VLC_DEV_PKG_DEB)"

    # 3. Check Python 3
    dpkg -s "$PYTHON_PKG" >/dev/null 2>&1
    python_status=$?
    status_check "Python 3 Interpreter" $python_status "sudo apt install $PYTHON_PKG" "The main Python 3 interpreter ($PYTHON_PKG)"

    # 4. Check PIP
    dpkg -s "$PIP_PKG_DEB" >/dev/null 2>&1
    pip_status=$?
    status_check "PIP Package Installer" $pip_status "sudo apt install $PIP_PKG_DEB" "The Python 3 package installer utility ($PIP_PKG_DEB)"
}

# --- Check Function for Red Hat/Fedora/CentOS (using rpm) ---
check_rpm() {
    echo "Checking dependencies using 'rpm' (Red Hat/Fedora/CentOS/etc...)"
    local vlc_status vlc_dev_status python_status pip_status

    # 1. Check VLC
    rpm -q "$VLC_PKG" >/dev/null 2>&1
    vlc_status=$?
    status_check "VLC Core Libraries" $vlc_status "sudo dnf install $VLC_PKG" "VLC Media Player and its essential runtime libraries ($VLC_PKG)"

    # 2. Check VLC Development Headers (required for 'pip install python-vlc')
    rpm -q "$VLC_DEV_PKG_RPM" >/dev/null 2>&1
    vlc_dev_status=$?
    status_check "VLC Development/Headers" $vlc_dev_status "sudo dnf install $VLC_DEV_PKG_RPM" "Header files for compiling Python bindings ($VLC_DEV_PKG_RPM)"

    # 3. Check Python 3
    rpm -q "$PYTHON_PKG" >/dev/null 2>&1
    python_status=$?
    status_check "Python 3 Interpreter" $python_status "sudo dnf install $PYTHON_PKG" "The main Python 3 interpreter ($PYTHON_PKG)"

    # 4. Check PIP
    rpm -q "$PIP_PKG_RPM" >/dev/null 2>&1
    pip_status=$?
    status_check "PIP Package Installer" $pip_status "sudo dnf install $PIP_PKG_RPM" "The Python 3 package installer utility ($PIP_PKG_RPM)"
}

# --- Check Function for Arch/Manjaro (using pacman) ---
check_arch() {
    echo "Checking dependencies using 'pacman' (Arch/Manjaro/etc...)"
    local vlc_status vlc_dev_status python_status pip_status

    # 1. Check VLC (The main 'vlc' package often includes dev files on Arch)
    pacman -Qi "$VLC_PKG" >/dev/null 2>&1
    vlc_status=$?
    status_check "VLC Core Libraries" $vlc_status "sudo pacman -S $VLC_PKG" "VLC Media Player and its essential runtime libraries ($VLC_PKG)"

    # 2. Check VLC Development Headers (On Arch, this is the same package as VLC)
    pacman -Qi "$VLC_PKG" >/dev/null 2>&1
    vlc_dev_status=$?
    status_check "VLC Development/Headers" $vlc_dev_status "sudo pacman -S $VLC_PKG" "Header files for compiling Python bindings ($VLC_PKG)"


    # 3. Check Python 3
    pacman -Qi "$PYTHON_PKG" >/dev/null 2>&1
    python_status=$?
    status_check "Python 3 Interpreter" $python_status "sudo pacman -S $PYTHON_PKG" "The main Python 3 interpreter ($PYTHON_PKG)"

    # 4. Check PIP
    pacman -Qi "$PIP_PKG_ARCH" >/dev/null 2>&1
    pip_status=$?
    status_check "PIP Package Installer" $pip_status "sudo pacman -S $PIP_PKG_ARCH" "The Python 3 package installer utility ($PIP_PKG_ARCH)"
}

# --- Main Logic: Call the appropriate check function ---

case "$ID" in
    debian|ubuntu|mint)
        check_debian
        ;;
    fedora|centos|rhel|almalinux|rocky)
        check_rpm
        ;;
    arch|manjaro)
        check_arch
        ;;
    *)
        echo -e "\nWarning: Unsupported distribution '$ID'. Only checks for Debian/RPM/Arch-based systems are implemented."
        echo "Please check dependencies manually."
        ;;
esac

echo -e "\n--- Final Check: Python Module Import ---\n"

# Check for the 'pip' installed module as a final verification for python-vlc
if command -v python3 &>/dev/null; then
    echo "Attempting to import 'vlc' module using Python 3..."
    # The 'vlc' module needs the core VLC libraries (libvlc.so) installed via the system package manager.
    python3 -c "import vlc; print('✅ Success: Python 3 can import the vlc module (pip installation is working).')" 2>/dev/null
    if [ $? -ne 0 ]; then
        status_check "Python-VLC Binding (pip check)" 1 "" ""
        echo "   Possible Solutions:"
        echo "   1. Ensure the VLC Core Libraries and Development Headers are installed (see above)."
        echo "   2. Run the pip installation command:"
        echo "      > pip install python-vlc"
    fi
else
    echo "Skipping final 'vlc' import check because Python 3 is not installed or not in PATH."
fi
echo -e "\n----------------------------------------"
