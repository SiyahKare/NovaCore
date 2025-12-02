#!/bin/bash
# Quick Consent Flow Test (without auth)
# Tests the complete consent signing flow

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
TEST_USER_ID="AUR-TEST-$(date +%s)"

# Check if API is running
if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo "❌ API is not running at $BASE_URL"
    echo "   Please start the API with: uvicorn app.main:app --reload"
    exit 1
fi

echo "🔷 Testing Consent Flow"
echo "======================"
echo ""

# Create session
echo "1. Creating consent session..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/consent/session" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$TEST_USER_ID\",
    \"client_fingerprint\": \"dev-macbook-01\"
  }")

SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))" 2>/dev/null)

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "None" ]; then
    echo "❌ Failed to create session"
    echo "Response: $SESSION_RESPONSE"
    exit 1
fi

echo "✅ Session created: $SESSION_ID"
echo ""

# Accept clauses
echo "2. Accepting clauses..."
for clause in "1.1" "1.2" "2.1" "2.2" "3.1" "3.2" "4.1" "4.2"; do
    curl -s -X POST "$BASE_URL/consent/clauses" \
      -H "Content-Type: application/json" \
      -d "{
        \"session_id\": \"$SESSION_ID\",
        \"clause_id\": \"$clause\",
        \"status\": \"ACCEPTED\",
        \"comprehension_passed\": true
      }" > /dev/null
    echo "  ✓ Clause $clause"
done
echo ""

# Accept redline
echo "3. Accepting redline..."
curl -s -X POST "$BASE_URL/consent/redline" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"redline_status\": \"ACCEPTED\",
    \"user_note_hash\": null
  }" > /dev/null
echo "✅ Redline accepted"
echo ""

# Sign consent
echo "4. Signing consent..."
SIGN_RESPONSE=$(curl -s -X POST "$BASE_URL/consent/sign" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"user_id\": \"$TEST_USER_ID\",
    \"contract_version\": \"Aurora-DataEthics-v1.0\",
    \"clauses_accepted\": [\"1.1\",\"1.2\",\"2.1\",\"2.2\",\"3.1\",\"3.2\",\"4.1\",\"4.2\"],
    \"redline_status\": \"ACCEPTED\",
    \"signature_text\": \"Baron Test\",
    \"client_fingerprint\": \"dev-macbook-01\"
  }")

RECORD_ID=$(echo "$SIGN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('record_id', ''))" 2>/dev/null)

if [ -z "$RECORD_ID" ] || [ "$RECORD_ID" = "None" ]; then
    echo "❌ Failed to sign consent"
    echo "Response: $SIGN_RESPONSE"
    exit 1
fi

echo "✅ Consent signed: $RECORD_ID"
echo ""
echo "📋 Test Summary:"
echo "  User ID: $TEST_USER_ID"
echo "  Session ID: $SESSION_ID"
echo "  Record ID: $RECORD_ID"
echo ""
echo "✅ Consent flow test complete!"
