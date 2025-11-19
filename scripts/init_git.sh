#!/bin/bash
# Initialize Git repository and create initial commit

set -e

echo "========================================="
echo "Initializing Git Repository"
echo "========================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed"
    exit 1
fi

# Initialize repository if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git branch -M main
else
    echo "Git repository already initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Logs
*.log
logs/

# Configuration (sensitive)
config/secrets.json
config/line_credentials.json
*.key
*.pem

# Snapshots and media
snapshots/
*.jpg
*.png
*.mp4
*.avi
*.wav
*.mp3

# OS
.DS_Store
Thumbs.db

# Raspberry Pi specific
*.img
*.img.gz
*.img.xz

# Temporary files
tmp/
temp/
*.tmp
EOF
fi

# Stage all files
echo "Staging files..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "chore: initial project setup

- Project structure created
- CI/CD workflows configured
- Architecture diagram added
- Documentation initialized
- Branching strategy defined
- All 9 milestones planned

Project: Raspberry Pi Smart Monitoring Kit
Client: Yoshinori Ueda
Budget: \$450
Timeline: 3-4 weeks"

echo ""
echo "========================================="
echo "Git repository initialized successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Create GitHub repository"
echo "2. Add remote: git remote add origin <repository-url>"
echo "3. Push to GitHub: git push -u origin main"
echo "4. Start Milestone 1: git checkout -b milestone-1-rtsp-setup"
echo ""
echo "Current branch: $(git branch --show-current)"
echo "Total commits: $(git rev-list --count HEAD)"

