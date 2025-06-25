# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# Install system dependencies required for downloading tools and for Conda
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# --- Install Terraform ---
ARG TERRAFORM_VERSION=1.8.5
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# --- Install Google Cloud SDK ---
RUN apt-get update && apt-get install -y apt-transport-https gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# --- Install Miniconda ---
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p $CONDA_DIR && \
    rm miniconda.sh && \
    $CONDA_DIR/bin/conda init bash

# Copy the Conda environment file
COPY agentic_genomics/environment.yml .

# Create the Conda environment
RUN conda env create -f environment.yml

# Make sure all subsequent commands run in the new environment
SHELL ["conda", "run", "-n", "adk-nextflow-dev", "/bin/bash", "-c"]

# Copy the rest of the application code
COPY agentic_genomics/ ./agentic_genomics/

# Expose a port if you're running a web server (e.g., FastAPI/Uvicorn)
EXPOSE 8080

# Define the command to run your application
# This would typically be a web server that hosts the ADK agent.
# For example:
# CMD ["uvicorn", "agentic_genomics.main:app", "--host", "0.0.0.0", "--port", "8080"]