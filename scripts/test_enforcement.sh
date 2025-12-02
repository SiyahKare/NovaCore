#!/bin/bash
# Aurora Enforcement Test
# Tests that LOCKDOWN users are actually blocked from actions

set -e

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_PREFIX="${API_PREFIX:-}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_USER_ID="AUR-ENFORCE-TEST-$(date +%s)"

echo -e "${BLUE}⚖️  Aurora Enforcement Test${NC}"
echo -e "${BLUE}============================${NC}"
echo ""

# Helper functions
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local headers="$4"
    
    if [ -n "$data" ]; then
        curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$API_PREFIX$endpoint" \
            -H "Content-Type: application/json" \
            $headers \
            -d "$data"
    else
        curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$API_PREFIX$endpoint" \
            $headers
    fi
}

extract_json() {
    local json="$1"
    local field="$2"
    echo "$json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('$field', ''))" 2>/dev/null || echo ""
}

print_test() {
    local test_name="$1"
    local status="$2"
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $test_name${NC}"
    else
        echo -e "${RED}❌ $test_name${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}📋 Step 1: Create test user with consent${NC}"

# Create consent session
SESSION_RESPONSE=$(api_call "POST" "/consent/session" "{
    \"user_id\": \"$TEST_USER_ID\",
    \"client_fingerprint\": \"enforce-test-01\"
}" "")
SESSION_ID=$(echo "$SESSION_RESPONSE" | head -n 1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('session_id', ''))" 2>/dev/null)

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "None" ]; then
    print_test "Session creation" "FAIL"
fi

# Accept all clauses
for clause in "1.1" "1.2" "2.1" "2.2" "3.1" "3.2" "4.1" "4.2"; do
    api_call "POST" "/consent/clauses" "{
        \"session_id\": \"$SESSION_ID\",
        \"clause_id\": \"$clause\",
        \"status\": \"ACCEPTED\",
        \"comprehension_passed\": true
    }" "" > /dev/null
done

# Accept redline
api_call "POST" "/consent/redline" "{
    \"session_id\": \"$SESSION_ID\",
    \"redline_status\": \"ACCEPTED\",
    \"user_note_hash\": null
}" "" > /dev/null

# Sign consent
SIGN_RESPONSE=$(api_call "POST" "/consent/sign" "{
    \"session_id\": \"$SESSION_ID\",
    \"user_id\": \"$TEST_USER_ID\",
    \"contract_version\": \"Aurora-DataEthics-v1.0\",
    \"clauses_accepted\": [\"1.1\",\"1.2\",\"2.1\",\"2.2\",\"3.1\",\"3.2\",\"4.1\",\"4.2\"],
    \"redline_status\": \"ACCEPTED\",
    \"signature_text\": \"Enforce Test\",
    \"client_fingerprint\": \"enforce-test-01\"
}" "")

echo -e "${GREEN}✓ User created and consent signed${NC}"
echo ""

echo -e "${YELLOW}📋 Step 2: Escalate user to LOCKDOWN regime${NC}"

# Add severe violations to push CP to 80+
VIOLATIONS=(
    '{"user_id":"'$TEST_USER_ID'","category":"TRUST","code":"TRUST_MULTIPLE_ACCOUNTS","severity":5,"source":"enforce-test","context":{"reason":"test"}}'
    '{"user_id":"'$TEST_USER_ID'","category":"SYS","code":"SYS_EXPLOIT","severity":5,"source":"enforce-test","context":{"reason":"test"}}'
    '{"user_id":"'$TEST_USER_ID'","category":"COM","code":"COM_TOXIC","severity":4,"source":"enforce-test","context":{"reason":"test"}}'
)

for violation in "${VIOLATIONS[@]}"; do
    VIOLATION_RESPONSE=$(api_call "POST" "/justice/violations" "$violation" "-H \"Authorization: Bearer test-token\"")
    CP_DELTA=$(echo "$VIOLATION_RESPONSE" | head -n 1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('cp_delta', 0))" 2>/dev/null)
    echo -e "  ${BLUE}→ Violation added: +$CP_DELTA CP${NC}"
done

# Check CP state
CP_RESPONSE=$(api_call "GET" "/justice/cp/me" "" "-H \"Authorization: Bearer test-token\"")
CP_VALUE=$(echo "$CP_RESPONSE" | head -n 1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('cp_value', 0))" 2>/dev/null)
REGIME=$(echo "$CP_RESPONSE" | head -n 1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('regime', ''))" 2>/dev/null)

echo -e "${GREEN}✓ CP: $CP_VALUE, Regime: $REGIME${NC}"

if [ "$REGIME" != "LOCKDOWN" ] && [ "$CP_VALUE" -lt 80 ]; then
    echo -e "${YELLOW}⚠️  CP not high enough for LOCKDOWN, adding more violations...${NC}"
    # Add more violations
    for i in {1..3}; do
        api_call "POST" "/justice/violations" '{"user_id":"'$TEST_USER_ID'","category":"SYS","code":"SYS_EXPLOIT","severity":5,"source":"enforce-test"}' "-H \"Authorization: Bearer test-token\"" > /dev/null
    done
    # Re-check
    CP_RESPONSE=$(api_call "GET" "/justice/cp/me" "" "-H \"Authorization: Bearer test-token\"")
    CP_VALUE=$(echo "$CP_RESPONSE" | head -n 1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('cp_value', 0))" 2>/dev/null)
    REGIME=$(echo "$CP_RESPONSE" | head -n 1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('regime', ''))" 2>/dev/null)
fi

if [ "$REGIME" != "LOCKDOWN" ]; then
    echo -e "${RED}❌ Failed to escalate to LOCKDOWN (CP: $CP_VALUE, Regime: $REGIME)${NC}"
    exit 1
fi

echo ""

echo -e "${YELLOW}📋 Step 3: Test enforcement on wallet transfer${NC}"

# Try to transfer funds (should be blocked)
TRANSFER_RESPONSE=$(api_call "POST" "/api/v1/wallet/transfer" "{
    \"to_user_id\": 999,
    \"amount\": \"10.0\",
    \"token\": \"NCR\",
    \"memo\": \"enforcement test\"
}" "-H \"Authorization: Bearer test-token\"")

HTTP_CODE=$(echo "$TRANSFER_RESPONSE" | tail -n 1)
RESPONSE_BODY=$(echo "$TRANSFER_RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "403" ]; then
    print_test "Wallet transfer blocked for LOCKDOWN user" "PASS"
    if echo "$RESPONSE_BODY" | grep -q "LOCKDOWN\|rejim\|regime" 2>/dev/null; then
        echo -e "${GREEN}✓ Error message contains regime information${NC}"
    fi
else
    echo -e "${RED}❌ Expected 403, got $HTTP_CODE${NC}"
    echo "Response: $RESPONSE_BODY"
    print_test "Enforcement check" "FAIL"
fi

echo ""

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}✅ Enforcement Test Complete!${NC}"
echo ""
echo -e "${BLUE}Test User: $TEST_USER_ID${NC}"
echo -e "${BLUE}Final CP: $CP_VALUE${NC}"
echo -e "${BLUE}Final Regime: $REGIME${NC}"

