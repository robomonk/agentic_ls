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
 
# --- Install Terraform and Google Cloud SDK (if not present) ---
echo "Checking for required command-line tools..."

# Check and install Terraform
if ! command -v terraform &> /dev/null; then
    echo "Terraform not found. Installing..."
    # Note: This may require sudo privileges to write to /usr/local/bin
    ARG_TERRAFORM_VERSION=1.8.5
    wget https://releases.hashicorp.com/terraform/${ARG_TERRAFORM_VERSION}/terraform_${ARG_TERRAFORM_VERSION}_linux_amd64.zip -O /tmp/terraform.zip && \
    unzip /tmp/terraform.zip -d /tmp && \
    sudo mv /tmp/terraform /usr/local/bin/ && \
    rm /tmp/terraform.zip
    echo "Terraform installed successfully."
else
    echo "Terraform is already installed."
fi

# Check and install Google Cloud SDK
if ! command -v gcloud &> /dev/null; then
    echo "Google Cloud SDK not found. Installing..."
    # Note: This requires sudo privileges for apt-get
    sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates gnupg
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    sudo apt-get update && sudo apt-get install -y google-cloud-sdk
    echo "Google Cloud SDK installed successfully."
    echo "Please run 'gcloud auth application-default login' to configure local credentials."
else
    echo "Google Cloud SDK is already installed."
fi


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
