#!/bin/bash
# Add a new presentation template to the claude-skills repo
# Usage: ./add-template.sh path/to/template.pptx [slides|posters] [template-name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$1" ]; then
    echo "Usage: $0 <pptx-file> [slides|posters] [template-name]"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Downloads/my-talk.pptx slides conference-talk"
    echo "  $0 ~/Downloads/poster.pptx posters neurips-2024"
    exit 1
fi

PPTX_FILE="$1"
OUTPUT_TYPE="${2:-slides}"
TEMPLATE_NAME="${3:-}"

if [ ! -f "$PPTX_FILE" ]; then
    echo "Error: File not found: $PPTX_FILE"
    exit 1
fi

# Check for python-pptx
if ! python3 -c "import pptx" 2>/dev/null; then
    echo "Installing python-pptx..."
    pip install python-pptx
fi

# Build command
CMD="python3 \"$SCRIPT_DIR/analyze_template.py\" \"$PPTX_FILE\" --output \"$OUTPUT_TYPE\""
if [ -n "$TEMPLATE_NAME" ]; then
    CMD="$CMD --name \"$TEMPLATE_NAME\""
fi

echo "Adding template..."
eval $CMD

echo ""
echo "✓ Template added! Run ./install.sh to update symlinks."
