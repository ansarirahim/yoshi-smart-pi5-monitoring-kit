#!/bin/bash
# Deployment script for Raspberry Pi 5
# Target: 192.168.1.39
# User: yoshi
# Author: A.R. Ansari

set -e

# Configuration
RPI_HOST="192.168.1.39"
RPI_USER="yoshi"
RPI_PASSWORD="ansari"
PROJECT_NAME="raspberry-pi-smart-monitoring"
REMOTE_DIR="/home/yoshi/${PROJECT_NAME}"
LOCAL_DIR="."

echo "========================================="
echo "Deploying to Raspberry Pi 5"
echo "========================================="
echo "Target: ${RPI_USER}@${RPI_HOST}"
echo "Remote Directory: ${REMOTE_DIR}"
echo ""

# Check if sshpass is available
if ! command -v sshpass &> /dev/null; then
    echo "Warning: sshpass not found. You'll need to enter password manually."
    SSH_CMD="ssh"
    SCP_CMD="scp"
else
    SSH_CMD="sshpass -p ${RPI_PASSWORD} ssh"
    SCP_CMD="sshpass -p ${RPI_PASSWORD} scp"
fi

# Test SSH connection
echo "Testing SSH connection..."
${SSH_CMD} ${RPI_USER}@${RPI_HOST} "echo 'Connection successful!'" || {
    echo "Error: Cannot connect to ${RPI_HOST}"
    exit 1
}

# Create remote directory
echo "Creating remote directory..."
${SSH_CMD} ${RPI_USER}@${RPI_HOST} "mkdir -p ${REMOTE_DIR}"

# Transfer files using rsync or scp
echo "Transferring files..."
if command -v rsync &> /dev/null; then
    echo "Using rsync for transfer..."
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='venv' \
        --exclude='htmlcov' \
        --exclude='coverage.xml' \
        --exclude='logs/*' \
        --exclude='snapshots/*' \
        --exclude='M*_SUBMISSION.txt' \
        --exclude='CODE_REVIEW_REPORT.md' \
        --exclude='*_GIT_DIFF_REVIEW.txt' \
        -e "ssh" \
        ${LOCAL_DIR}/ ${RPI_USER}@${RPI_HOST}:${REMOTE_DIR}/
else
    echo "Using scp for transfer..."
    ${SCP_CMD} -r \
        src config docs examples scripts tests \
        main.py requirements.txt setup.py pytest.ini VERSION \
        README.md MILESTONES.md \
        ${RPI_USER}@${RPI_HOST}:${REMOTE_DIR}/
fi

echo ""
echo "========================================="
echo "Transfer Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. SSH into RPI5: ssh ${RPI_USER}@${RPI_HOST}"
echo "2. Navigate to project: cd ${REMOTE_DIR}"
echo "3. Install dependencies: pip3 install -r requirements.txt"
echo "4. Configure secrets: cp config/secrets.example.json config/secrets.json"
echo "5. Edit config: nano config/config.yaml"
echo "6. Run tests: pytest tests/"
echo "7. Start application: python3 main.py"
echo ""
echo "For automatic startup, run: ./scripts/install.sh"
echo ""

