#!/bin/bash
# Update Chrome Extension with Production URL
# Usage: ./update_extension_url.sh https://your-app.onrender.com

RENDER_URL="${1}"

if [ -z "$RENDER_URL" ]; then
    echo "❌ Error: Please provide your Render URL"
    echo "Usage: ./update_extension_url.sh https://your-app.onrender.com"
    exit 1
fi

echo "🔧 Updating Chrome Extension manifest..."

# Backup original
cp chrome_extension/manifest.json chrome_extension/manifest.json.backup

# Update the host_permissions
sed -i "s|http://localhost:8001/\*|${RENDER_URL}/\*|g" chrome_extension/manifest.json

echo "✅ Updated manifest.json"
echo "   Old: http://localhost:8001/*"
echo "   New: ${RENDER_URL}/*"

# Create new extension package
echo ""
echo "📦 Creating new extension package..."
cd chrome_extension
zip -r ../khmer-spell-checker-extension-production.zip . -x "*.bak" -x ".*" -x "*.backup"
cd ..

echo ""
echo "✅ Extension package created!"
echo "   File: khmer-spell-checker-extension-production.zip"
echo ""
echo "📝 Next steps:"
echo "   1. Upload to Chrome Web Store"
echo "   2. Or test locally by loading unpacked extension"
