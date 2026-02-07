#!/bin/bash
# RepoLens Setup Script

set -e

echo "🔍 RepoLens Setup Script"
echo "========================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if python3-venv is available
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "❌ python3-venv is not available."
    echo ""
    echo "Please install it with:"
    echo "  sudo apt install python3.12-venv"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv "$SCRIPT_DIR/venv"

# Activate and install
echo "📥 Installing dependencies..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -e "$SCRIPT_DIR"

# Create bin directory and wrapper script
echo "🔧 Setting up global command..."
mkdir -p "$SCRIPT_DIR/bin"

cat > "$SCRIPT_DIR/bin/repolens" << 'EOF'
#!/usr/bin/env bash
# RepoLens launcher - automatically activates venv and runs repolens

# Resolve symlink to get actual script location
if [ -L "${BASH_SOURCE[0]}" ]; then
    # If it's a symlink, resolve it
    SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
else
    # Otherwise use the source directly
    SCRIPT_PATH="${BASH_SOURCE[0]}"
fi

# Get the directory where this script is located (resolved path)
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Run the actual repolens command with all passed arguments
exec repolens "$@"
EOF

chmod +x "$SCRIPT_DIR/bin/repolens"

# Create symlink in ~/.local/bin
mkdir -p ~/.local/bin
ln -sf "$SCRIPT_DIR/bin/repolens" ~/.local/bin/repolens

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  ~/.local/bin is not in your PATH."
    echo "   Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "   Then run: source ~/.bashrc"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run RepoLens, simply type:"
echo "  repolens"
echo ""
echo "No need to activate any virtual environment - it's handled automatically!"
echo ""
