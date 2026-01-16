#!/bin/bash
# Test Render Deployment
# Usage: ./test_render.sh https://your-app.onrender.com

API_URL="${1}"

if [ -z "$API_URL" ]; then
    echo "❌ Error: Please provide your Render URL"
    echo "Usage: ./test_render.sh https://your-app.onrender.com"
    exit 1
fi

echo "🧪 Testing Render Deployment"
echo "API URL: $API_URL"
echo "================================"

# Test 1: Health Check
echo -e "\n1️⃣  Testing health check endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Health check passed!"
    echo "Response: $BODY"
else
    echo "❌ Health check failed (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
    exit 1
fi

# Test 2: Spell Check Endpoint
echo -e "\n2️⃣  Testing spell check endpoint..."
SPELL_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/check" \
  -H "Content-Type: application/json" \
  -d '{"text": "សួស្តី"}')
HTTP_CODE=$(echo "$SPELL_RESPONSE" | tail -n1)
BODY=$(echo "$SPELL_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Spell check endpoint working!"
    echo "Response: $BODY" | head -c 200
    echo "..."
else
    echo "❌ Spell check failed (HTTP $HTTP_CODE)"
    echo "Response: $BODY"
fi

echo -e "\n================================"
echo "✅ Testing complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Update chrome_extension/manifest.json"
echo "   2. Change host_permissions to: $API_URL/*"
echo "   3. Re-package and publish extension"
