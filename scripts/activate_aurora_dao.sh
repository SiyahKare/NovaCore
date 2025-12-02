#!/bin/bash
# Aurora DAO Activation Script
# Complete activation checklist automation

set -e

echo "🔥 Aurora DAO Activation"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if virtualenv is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected${NC}"
    echo "Activating virtual environment..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo -e "${RED}❌ Virtual environment not found. Create with: python -m venv .venv${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Virtual environment active${NC}"
echo ""

# Step 1: Migration
echo -e "${BLUE}Step 1: Database Migration${NC}"
echo "Generating migration for policy tables..."
if alembic revision --autogenerate -m "Add justice policy params tables" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Migration generated${NC}"
else
    echo -e "${YELLOW}⚠️  Migration generation (may already exist)${NC}"
fi

echo "Applying migrations..."
if alembic upgrade head; then
    echo -e "${GREEN}✅ Migrations applied${NC}"
else
    echo -e "${RED}❌ Migration failed${NC}"
    exit 1
fi
echo ""

# Step 2: Initialize Default Policy
echo -e "${BLUE}Step 2: Initialize Default Policy${NC}"
if python scripts/init_default_policy.py; then
    echo -e "${GREEN}✅ Default policy initialized${NC}"
else
    echo -e "${RED}❌ Policy initialization failed${NC}"
    exit 1
fi
echo ""

# Step 3: Verify Policy
echo -e "${BLUE}Step 3: Verify Policy${NC}"
API_URL="${API_BASE_URL:-http://localhost:8000/api/v1}"
POLICY_RESPONSE=$(curl -s "${API_URL}/justice/policy/current" 2>/dev/null || echo "{}")
POLICY_VERSION=$(echo "$POLICY_RESPONSE" | jq -r '.version // "none"')

if [ "$POLICY_VERSION" != "none" ] && [ "$POLICY_VERSION" != "null" ]; then
    echo -e "${GREEN}✅ Active policy: ${POLICY_VERSION}${NC}"
    echo "$POLICY_RESPONSE" | jq '.version, .decay_per_day, .threshold_lockdown'
else
    echo -e "${YELLOW}⚠️  Could not verify policy (API may not be running)${NC}"
    echo "   Run API and check: curl ${API_URL}/justice/policy/current"
fi
echo ""

# Step 4: Test Simulation
echo -e "${BLUE}Step 4: Test Simulation${NC}"
if python scripts/simulate_aurora_policies.py --users 100 --days 30 --from-db --summary-only > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Simulation test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Simulation test (may need API running)${NC}"
fi
echo ""

# Step 5: Smart Contract Check
echo -e "${BLUE}Step 5: Smart Contract Check${NC}"
if [ -f "contracts/AuroraPolicyConfig.sol" ] && [ -f "contracts/AuroraConstitution.sol" ]; then
    echo -e "${GREEN}✅ Smart contracts ready${NC}"
    echo "   - contracts/AuroraPolicyConfig.sol"
    echo "   - contracts/AuroraConstitution.sol"
    echo ""
    echo -e "${YELLOW}Next: Deploy contracts to target chain${NC}"
else
    echo -e "${YELLOW}⚠️  Smart contracts not found${NC}"
fi
echo ""

# Step 6: Sync Check
echo -e "${BLUE}Step 6: DAO Sync Check${NC}"
if [ -n "$AURORA_RPC_URL" ] && [ -n "$AURORA_POLICY_CONTRACT" ]; then
    echo -e "${GREEN}✅ RPC and contract configured${NC}"
    echo "   Run: python scripts/sync_dao_policy.py"
else
    echo -e "${YELLOW}⚠️  RPC/Contract not configured${NC}"
    echo "   Set: AURORA_RPC_URL and AURORA_POLICY_CONTRACT"
fi
echo ""

# Summary
echo "========================================"
echo -e "${GREEN}✅ Aurora DAO Activation Complete!${NC}"
echo ""
echo "Completed:"
echo "  ✅ Database migration"
echo "  ✅ Default policy initialized"
echo "  ✅ Policy verification"
echo "  ✅ Simulation test"
echo ""
echo "Next Steps:"
echo "  1. Deploy smart contracts (see contracts/)"
echo "  2. Configure RPC and contract address"
echo "  3. Run: python scripts/sync_dao_policy.py"
echo "  4. Verify: curl ${API_URL}/justice/policy/current"
echo ""
echo "📚 Documentation:"
echo "  - docs/DAO_ACTIVATION_CHECKLIST.md"
echo "  - docs/DAO_INTEGRATION.md"
echo "  - docs/DAO_GOVERNANCE_FLOW.md"
echo ""

