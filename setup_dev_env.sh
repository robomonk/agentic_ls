#!/bin/bash

# --- Install Miniconda ---
# You can choose a specific version or the latest
MINICONDA_INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
MINICONDA_INSTALLER_URL="https://repo.anaconda.com/miniconda/${MINICONDA_INSTALLER}"
MINICONDA_INSTALL_PATH="$HOME/miniconda3"

echo "Downloading Miniconda installer..."
wget "${MINICONDA_INSTALLER_URL}" -O /tmp/"${MINICONDA_INSTALLER}"

echo "Installing Miniconda..."
# Use -b for batch mode (non-interactive), -u to update existing installation, -p to specify the install path
bash /tmp/"${MINICONDA_INSTALLER}" -b -u -p "${MINICONDA_INSTALL_PATH}"

# Remove the installer script
rm /tmp/"${MINICONDA_INSTALLER}"

# Initialize conda for your shell (adjust 'bash' if using a different shell)
# This modifies your shell's configuration file (e.g., ~/.bashrc)
echo "Initializing conda..."
"${MINICONDA_INSTALL_PATH}"/bin/conda init bash

# Source the conda.sh script to make the 'conda' command and 'activate' function
# available in the current script session. This is more reliable than sourcing ~/.bashrc,
# which might have guards against running in non-interactive shells.
source "${MINICONDA_INSTALL_PATH}/etc/profile.d/conda.sh"
 
# Deactivate any active environment within the script's session to ensure a clean, predictable state.
conda deactivate &> /dev/null || true

# --- Create or Update Conda Environment ---
ENV_FILE="environment.yml"
ENV_NAME_FROM_FILE=$(grep "name:" "${ENV_FILE}" | awk '{print $2}')

echo "Ensuring Conda environment '${ENV_NAME_FROM_FILE}' is created and up-to-date..."
# This single command is idempotent. It will create the environment if it doesn't exist,
# or update it with the packages from the file if it does.
# The --prune option removes packages from the env that are no longer in the file.
conda env update --file "${ENV_FILE}" --prune --name "${ENV_NAME_FROM_FILE}"

# --- Activate the Environment ---
echo "Activating the '${ENV_NAME_FROM_FILE}' environment..."
conda activate "${ENV_NAME_FROM_FILE}"

echo ""
echo "-------------------------------------------------------------------"
echo "Setup complete! The '${ENV_NAME_FROM_FILE}' environment is now active."
echo "NOTE: For the activation to affect your terminal, this script must be 'sourced'."
echo "Please run it like this: source ./setup_dev_env.sh"
echo "-------------------------------------------------------------------"
