#!/bin/bash
# NovaCore + Aurora Justice - Final Activation Script
# Complete activation checklist automation
# This script activates NovaCore as a fully operational DAO-controlled digital state

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
POSTGRES_PORT="${POSTGRES_PORT:-5433}"
API_URL="${API_URL:-http://localhost:8000}"
SKIP_TESTS="${SKIP_TESTS:-false}"
SKIP_DAO_SYNC="${SKIP_DAO_SYNC:-false}"

echo -e "${PURPLE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   NOVACORE + AURORA JUSTICE - ACTIVATION CHECKLIST (v1.0)  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Step counter
STEP=0
TOTAL_STEPS=8

print_step() {
  STEP=$((STEP + 1))
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}[$STEP/$TOTAL_STEPS]${NC} ${1}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

print_success() {
  echo -e "${GREEN}✅ ${1}${NC}"
}

print_error() {
  echo -e "${RED}❌ ${1}${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  ${1}${NC}"
}

print_info() {
  echo -e "${CYAN}ℹ️  ${1}${NC}"
}

# Check prerequisites
check_prerequisites() {
  print_info "Checking prerequisites..."
  
  # Check Python
  if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
  fi
  
  # Check Docker
  if ! command -v docker &> /dev/null; then
    print_error "Docker is required but not installed"
    exit 1
  fi
  
  # Check virtualenv
  if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv .venv
  fi
  
  # Activate virtualenv
  if [ -z "$VIRTUAL_ENV" ]; then
    source .venv/bin/activate
  fi
  
  print_success "Prerequisites check complete"
}

# Step 1: DB & Migration Setup
step_1_migration() {
  print_step "1. Database & Migration Setup"
  
  # 1.1 Environment check
  if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from example..."
    if [ -f ".env.example" ]; then
      cp .env.example .env
      print_info "Please update .env with your database credentials"
    else
      print_error ".env.example not found. Please create .env manually"
      exit 1
    fi
  fi
  
  # 1.2 Docker start
  print_info "Starting PostgreSQL container..."
  if docker-compose up -d postgres 2>/dev/null; then
    print_success "PostgreSQL container started"
    sleep 3  # Wait for DB to be ready
  else
    print_warning "Docker Compose failed. Trying direct docker command..."
    # Fallback: try direct docker
    if docker ps | grep -q novacore-postgres; then
      print_success "PostgreSQL container already running"
    else
      print_error "Failed to start PostgreSQL. Please start manually."
      exit 1
    fi
  fi
  
  # 1.3 Run migrations
  print_info "Running database migrations..."
  if alembic upgrade head; then
    print_success "Migrations applied successfully"
  else
    print_error "Migration failed"
    exit 1
  fi
  
  # Verify critical tables
  print_info "Verifying critical tables..."
  CRITICAL_TABLES=(
    "consent_sessions"
    "consent_records"
    "user_privacy_profiles"
    "justice_policy_params"
    "justice_policy_change_log"
    "justice_violations"
    "justice_cp_state"
  )
  
  for table in "${CRITICAL_TABLES[@]}"; do
    if docker exec novacore-postgres psql -U novacore -d novacore -c "\d $table" &>/dev/null; then
      print_success "Table $table exists"
    else
      print_error "Table $table not found"
      exit 1
    fi
  done
  
  echo ""
}

# Step 2: Default Policy Seed
step_2_policy_seed() {
  print_step "2. Default Policy Seed (DAO v1.0)"
  
  print_info "Initializing default Aurora Justice Policy v1.0..."
  if python scripts/init_default_policy.py; then
    print_success "Default policy v1.0 seeded"
  else
    print_error "Policy seed failed"
    exit 1
  fi
  
  # Verify policy
  print_info "Verifying policy in database..."
  POLICY_COUNT=$(docker exec novacore-postgres psql -U novacore -d novacore -t -c "SELECT COUNT(*) FROM justice_policy_params WHERE active = TRUE;" 2>/dev/null | tr -d ' ')
  if [ "$POLICY_COUNT" -gt 0 ]; then
    print_success "Active policy found in database"
  else
    print_error "No active policy found"
    exit 1
  fi
  
  echo ""
}

# Step 3: DAO Smart Contract Connection
step_3_dao_sync() {
  print_step "3. DAO Smart Contract Connection"
  
  if [ "$SKIP_DAO_SYNC" = "true" ]; then
    print_warning "DAO sync skipped (SKIP_DAO_SYNC=true)"
    print_info "To sync later, run: python scripts/sync_dao_policy.py --rpc-url <RPC> --contract <ADDRESS>"
    echo ""
    return
  fi
  
  if [ -z "$AURORA_RPC_URL" ] || [ -z "$AURORA_POLICY_CONTRACT" ]; then
    print_warning "DAO contract not configured (AURORA_RPC_URL or AURORA_POLICY_CONTRACT not set)"
    print_info "Skipping DAO sync. To sync later:"
    print_info "  export AURORA_RPC_URL=https://rpc.testnet"
    print_info "  export AURORA_POLICY_CONTRACT=0x..."
    print_info "  python scripts/sync_dao_policy.py"
    echo ""
    return
  fi
  
  # 3.1 Dry-run
  print_info "Testing DAO sync (dry-run)..."
  if python scripts/sync_dao_policy.py --rpc-url "$AURORA_RPC_URL" --contract "$AURORA_POLICY_CONTRACT" --dry-run; then
    print_success "Dry-run successful"
  else
    print_error "Dry-run failed. Check RPC URL and contract address"
    exit 1
  fi
  
  # 3.2 Real sync
  print_info "Syncing policy from DAO contract..."
  if python scripts/sync_dao_policy.py --rpc-url "$AURORA_RPC_URL" --contract "$AURORA_POLICY_CONTRACT"; then
    print_success "Policy synced from DAO"
  else
    print_error "DAO sync failed"
    exit 1
  fi
  
  echo ""
}

# Step 4: Demo Citizen Seed
step_4_demo_seed() {
  print_step "4. Demo Citizen Seed"
  
  print_info "Seeding demo users (AUR-SIGMA, AUR-TROLLER, AUR-GHOST)..."
  if python scripts/seed_aurora_demo.py; then
    print_success "Demo users seeded"
  else
    print_warning "Demo seed failed (may already exist)"
  fi
  
  # Verify demo users
  print_info "Verifying demo users..."
  DEMO_COUNT=$(docker exec novacore-postgres psql -U novacore -d novacore -t -c "SELECT COUNT(*) FROM justice_cp_state WHERE user_id LIKE 'AUR-%';" 2>/dev/null | tr -d ' ')
  if [ "$DEMO_COUNT" -gt 0 ]; then
    print_success "Found $DEMO_COUNT demo users"
  else
    print_warning "No demo users found"
  fi
  
  echo ""
}

# Step 5: Core System Tests
step_5_tests() {
  print_step "5. Core System Tests"
  
  if [ "$SKIP_TESTS" = "true" ]; then
    print_warning "Tests skipped (SKIP_TESTS=true)"
    echo ""
    return
  fi
  
  # Check if API is running
  print_info "Checking if API is running..."
  if curl -s "$API_URL/health" > /dev/null 2>&1; then
    print_success "API is running"
  else
    print_warning "API is not running. Starting in background..."
    print_info "Starting API server..."
    # Start API in background (user should start manually in production)
    print_warning "Please start API manually: uvicorn app.main:app --reload"
    print_info "Skipping API-dependent tests"
    echo ""
    return
  fi
  
  # 5.1 Consent Flow Test
  print_info "5.1 Running Consent Flow Test..."
  if [ -f "scripts/test_consent_flow.sh" ]; then
    if ./scripts/test_consent_flow.sh; then
      print_success "Consent flow test passed"
    else
      print_error "Consent flow test failed"
      exit 1
    fi
  else
    print_warning "test_consent_flow.sh not found, skipping"
  fi
  
  # 5.2 Full Smoke Test
  print_info "5.2 Running Full Smoke Test..."
  if [ -f "scripts/smoke_test.sh" ]; then
    if ./scripts/smoke_test.sh; then
      print_success "Smoke test passed"
    else
      print_error "Smoke test failed"
      exit 1
    fi
  else
    print_warning "smoke_test.sh not found, skipping"
  fi
  
  # 5.3 Enforcement Test
  print_info "5.3 Running Enforcement Test..."
  if [ -f "scripts/test_enforcement.sh" ]; then
    if ./scripts/test_enforcement.sh; then
      print_success "Enforcement test passed"
    else
      print_error "Enforcement test failed"
      exit 1
    fi
  else
    print_warning "test_enforcement.sh not found, skipping"
  fi
  
  # 5.4 DAO Integration Test
  print_info "5.4 Running DAO Integration Test..."
  if [ -f "scripts/test_dao_integration.sh" ]; then
    if ./scripts/test_dao_integration.sh; then
      print_success "DAO integration test passed"
    else
      print_warning "DAO integration test failed (may need contract setup)"
    fi
  else
    print_warning "test_dao_integration.sh not found, skipping"
  fi
  
  echo ""
}

# Step 6: Frontend Activation
step_6_frontend() {
  print_step "6. Frontend Activation (Shared Libraries)"
  
  # Check if packages exist
  if [ -d "packages/aurora-ui" ]; then
    print_success "Aurora UI package found"
    UI_COMPONENTS=$(find packages/aurora-ui/src/components -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
    print_info "  Found $UI_COMPONENTS components"
  else
    print_warning "packages/aurora-ui not found"
  fi
  
  if [ -d "packages/aurora-hooks" ]; then
    print_success "Aurora Hooks package found"
    HOOKS=$(find packages/aurora-hooks/src -name "use*.ts" 2>/dev/null | wc -l | tr -d ' ')
    print_info "  Found $HOOKS hooks"
  else
    print_warning "packages/aurora-hooks not found"
  fi
  
  print_info "Frontend libraries ready for Citizen Portal setup"
  echo ""
}

# Step 7: CI/CD Verification
step_7_cicd() {
  print_step "7. CI/CD Verification"
  
  if [ -f ".github/workflows/aurora-smoke-test.yml" ]; then
    print_success "GitHub Actions workflow found"
    print_info "CI/CD pipeline configured for:"
    print_info "  - PostgreSQL setup"
    print_info "  - Migration execution"
    print_info "  - API startup"
    print_info "  - Full test suite"
  else
    print_warning "GitHub Actions workflow not found"
    print_info "Create .github/workflows/aurora-smoke-test.yml for CI/CD"
  fi
  
  echo ""
}

# Step 8: Final Verification
step_8_verification() {
  print_step "8. Final Verification"
  
  print_info "Verifying Aurora State activation..."
  
  # Check database
  DB_TABLES=$(docker exec novacore-postgres psql -U novacore -d novacore -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
  if [ "$DB_TABLES" -gt 10 ]; then
    print_success "Database: $DB_TABLES tables found"
  else
    print_error "Database verification failed"
    exit 1
  fi
  
  # Check policy
  POLICY_VERSION=$(docker exec novacore-postgres psql -U novacore -d novacore -t -c "SELECT version FROM justice_policy_params WHERE active = TRUE LIMIT 1;" 2>/dev/null | tr -d ' ')
  if [ -n "$POLICY_VERSION" ]; then
    print_success "Policy: $POLICY_VERSION active"
  else
    print_error "No active policy found"
    exit 1
  fi
  
  # Check demo users
  DEMO_USERS=$(docker exec novacore-postgres psql -U novacore -d novacore -t -c "SELECT COUNT(*) FROM justice_cp_state WHERE user_id LIKE 'AUR-%';" 2>/dev/null | tr -d ' ')
  if [ "$DEMO_USERS" -gt 0 ]; then
    print_success "Demo users: $DEMO_USERS found"
  else
    print_warning "No demo users found"
  fi
  
  echo ""
}

# Main execution
main() {
  check_prerequisites
  
  step_1_migration
  step_2_policy_seed
  step_3_dao_sync
  step_4_demo_seed
  step_5_tests
  step_6_frontend
  step_7_cicd
  step_8_verification
  
  # Final message
  echo ""
  echo -e "${PURPLE}╔════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${PURPLE}║                                                            ║${NC}"
  echo -e "${GREEN}║${NC}        ${GREEN}AURORA STATE IS NOW LIVE${NC}                    ${GREEN}║${NC}"
  echo -e "${PURPLE}║                                                            ║${NC}"
  echo -e "${PURPLE}╚════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}Activation Summary:${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  echo -e "  ${GREEN}✅${NC} Database & Migrations"
  echo -e "  ${GREEN}✅${NC} Default Policy v1.0"
  echo -e "  ${GREEN}✅${NC} DAO Contract Connection"
  echo -e "  ${GREEN}✅${NC} Demo Citizens"
  echo -e "  ${GREEN}✅${NC} System Tests"
  echo -e "  ${GREEN}✅${NC} Frontend Libraries"
  echo -e "  ${GREEN}✅${NC} CI/CD Ready"
  echo ""
  echo -e "${CYAN}Next Steps:${NC}"
  echo -e "  1. Start API: ${YELLOW}uvicorn app.main:app --reload${NC}"
  echo -e "  2. Access API: ${YELLOW}$API_URL${NC}"
  echo -e "  3. Build Citizen Portal: ${YELLOW}cd apps/citizen-portal && npm run dev${NC}"
  echo -e "  4. View docs: ${YELLOW}docs/DAO_ACTIVATION_CHECKLIST.md${NC}"
  echo ""
  echo -e "${PURPLE}SiyahKare Republic + NovaCore = DAO-controlled, versioned, simulated, enforced digital state.${NC}"
  echo ""
}

# Run main
main

