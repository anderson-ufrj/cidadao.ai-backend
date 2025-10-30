#!/bin/bash
# Generate base64-encoded Google Cloud credentials for Railway deployment
# Usage: ./scripts/deployment/generate_google_credentials_base64.sh

set -e

CREDENTIALS_FILE="config/credentials/google-cloud-key.json"
OUTPUT_FILE="/tmp/google_credentials_base64.txt"

echo "🔐 Generating base64 credentials for Railway deployment..."
echo ""

# Check if credentials file exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Error: Credentials file not found at: $CREDENTIALS_FILE"
    echo ""
    echo "Please ensure the Google Cloud service account JSON is at:"
    echo "  $CREDENTIALS_FILE"
    exit 1
fi

echo "✅ Found credentials file: $CREDENTIALS_FILE"
echo ""

# Validate JSON structure
if ! jq empty "$CREDENTIALS_FILE" 2>/dev/null; then
    echo "❌ Error: Invalid JSON in credentials file"
    exit 1
fi

echo "✅ Credentials file is valid JSON"
echo ""

# Extract project info
PROJECT_ID=$(jq -r '.project_id' "$CREDENTIALS_FILE")
CLIENT_EMAIL=$(jq -r '.client_email' "$CREDENTIALS_FILE")

echo "📋 Credentials Info:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Account: $CLIENT_EMAIL"
echo ""

# Generate base64 (single line, no wrapping)
echo "🔄 Generating base64 encoding..."
base64 -w 0 "$CREDENTIALS_FILE" > "$OUTPUT_FILE"

# Get base64 length
BASE64_LENGTH=$(wc -c < "$OUTPUT_FILE")

echo "✅ Base64 generated successfully!"
echo ""
echo "📊 Statistics:"
echo "  Original file size: $(wc -c < "$CREDENTIALS_FILE") bytes"
echo "  Base64 length: $BASE64_LENGTH characters"
echo ""

# Show preview
echo "🔍 Preview (first 100 characters):"
head -c 100 "$OUTPUT_FILE"
echo "..."
echo ""

# Show last 50 characters
echo "🔍 Preview (last 50 characters):"
echo -n "..."
tail -c 50 "$OUTPUT_FILE"
echo ""
echo ""

echo "📁 Full base64 saved to: $OUTPUT_FILE"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 NEXT STEPS - Configure Railway:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Copy the base64 value:"
echo "   cat $OUTPUT_FILE | pbcopy    # macOS"
echo "   cat $OUTPUT_FILE | xclip -selection clipboard    # Linux"
echo "   cat $OUTPUT_FILE    # Manual copy"
echo ""
echo "2. Go to Railway Dashboard:"
echo "   https://railway.app/project/cidadao-ai/settings"
echo ""
echo "3. Update environment variable:"
echo "   Variable Name: GOOGLE_CREDENTIALS_BASE64"
echo "   Variable Value: [paste the base64 content]"
echo ""
echo "4. Verify the value is set correctly:"
echo "   - It should be a single long line"
echo "   - Length: $BASE64_LENGTH characters"
echo "   - Starts with: $(head -c 20 "$OUTPUT_FILE")"
echo ""
echo "5. Railway will auto-redeploy (~2-3 minutes)"
echo ""
echo "6. Test the voice endpoint:"
echo "   curl https://cidadao-api-production.up.railway.app/api/v1/voice/health | jq '.configuration'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Script completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
