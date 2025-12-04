#!/bin/bash
# NovaCore Citizen Portal - Quick Validation Script

set -e

echo "🔍 NovaCore Citizen Portal - Validation Check"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Next.js dev server is running
echo "1️⃣ Checking if Next.js dev server is running..."
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Portal is running on http://localhost:3001${NC}"
else
    echo -e "${RED}❌ Portal is not running. Start with: cd apps/citizen-portal && npm run dev${NC}"
    exit 1
fi

# Check if backend is running
echo ""
echo "2️⃣ Checking if backend API is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API is running on http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API is not running. Some features may not work.${NC}"
    echo "   Start with: uvicorn app.main:app --reload"
fi

# Check if seed users exist (optional)
echo ""
echo "3️⃣ Checking seed users..."
if curl -s -X POST "http://localhost:8000/api/v1/dev/token?user_id=AUR-SIGMA" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Seed users available (AUR-SIGMA, AUR-TROLLER, AUR-GHOST)${NC}"
else
    echo -e "${YELLOW}⚠️  Seed users may not exist. Run: python scripts/seed_aurora_demo.py${NC}"
fi

# Test protected endpoints (if token available)
echo ""
echo "4️⃣ Testing protected endpoints (requires token)..."
echo "   Manual test: Use CitizenSwitcher in dev mode to get a token"
echo "   Then test:"
echo "   - GET /api/v1/identity/me"
echo "   - GET /api/v1/nova-score/me"
echo "   - GET /api/v1/justice/cp/me"

echo ""
echo "✅ Validation checklist complete!"
echo ""
echo "📋 Manual Tests to Run:"
echo "   1. Visit http://localhost:3001"
echo "   2. Click 'Become a Citizen' → Test onboarding flow"
echo "   3. Use CitizenSwitcher (bottom-right) to switch users"
echo "   4. Test protected pages: /dashboard, /identity, /justice, /academy"
echo "   5. Test logout → should redirect to landing"
echo ""

