#!/bin/bash
# Citizen Portal Setup Script
# Installs dependencies and builds shared libraries

set -e

echo "🚀 Setting up Citizen Portal..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Build shared libraries
echo -e "${YELLOW}1. Building shared libraries...${NC}"
cd ../../packages/aurora-ui
if [ ! -d "node_modules" ]; then
  echo "  Installing aurora-ui dependencies..."
  npm install
fi
echo "  Building aurora-ui..."
npm run build
echo -e "${GREEN}✅ aurora-ui built${NC}"

cd ../aurora-hooks
if [ ! -d "node_modules" ]; then
  echo "  Installing aurora-hooks dependencies..."
  npm install
fi
echo "  Building aurora-hooks..."
npm run build
echo -e "${GREEN}✅ aurora-hooks built${NC}"

# 2. Install portal dependencies
echo ""
echo -e "${YELLOW}2. Installing portal dependencies...${NC}"
cd ../../apps/citizen-portal
if [ ! -d "node_modules" ]; then
  npm install
  echo -e "${GREEN}✅ Dependencies installed${NC}"
else
  echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# 3. Setup env
echo ""
echo -e "${YELLOW}3. Setting up environment...${NC}"
if [ ! -f ".env.local" ]; then
  cp .env.local.example .env.local
  echo -e "${GREEN}✅ .env.local created${NC}"
else
  echo -e "${GREEN}✅ .env.local exists${NC}"
fi

# 4. Check port
echo ""
echo -e "${YELLOW}4. Checking ports...${NC}"
if lsof -ti:3000 > /dev/null 2>&1; then
  echo -e "${YELLOW}⚠️  Port 3000 is in use${NC}"
  echo "   Kill with: lsof -ti:3000 | xargs kill -9"
  echo "   Or use: PORT=3001 npm run dev"
else
  echo -e "${GREEN}✅ Port 3000 is free${NC}"
fi

if lsof -ti:8000 > /dev/null 2>&1; then
  echo -e "${GREEN}✅ API running on port 8000${NC}"
else
  echo -e "${YELLOW}⚠️  API not running on port 8000${NC}"
  echo "   Start with: uvicorn app.main:app --reload"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start API: uvicorn app.main:app --reload"
echo "  2. Start Portal: npm run dev"
echo "  3. Visit: http://localhost:3000"

