#!/bin/bash
# Test script for deployed API

API_URL="${1:-http://localhost:8001}"

echo "Testing API at: $API_URL"
echo "================================"

# Test health check
echo -e "\n1. Testing health check endpoint..."
curl -X GET "$API_URL/" | jq .

# Test spell check
echo -e "\n2. Testing spell check endpoint..."
curl -X POST "$API_URL/check" \
  -H "Content-Type: application/json" \
  -d '{"text": "សួស្តី"}' | jq .

echo -e "\n================================"
echo "Testing complete!"
