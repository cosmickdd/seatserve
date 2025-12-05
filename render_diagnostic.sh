#!/bin/bash
# Render Deployment Diagnostic Script
# This script runs after deployment to verify everything is working

set -e

echo ""
echo "████████████████████████████████████████████████████████████████████"
echo "█ SeatServe Production Diagnostic Script for Render"
echo "████████████████████████████████████████████████████████████████████"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_success() {
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} $1"
  else
    echo -e "${RED}✗${NC} $1"
  fi
}

check_file() {
  if [ -f "$1" ]; then
    echo -e "${GREEN}✓${NC} File exists: $1"
    return 0
  else
    echo -e "${RED}✗${NC} File missing: $1"
    return 1
  fi
}

check_dir() {
  if [ -d "$1" ]; then
    file_count=$(find "$1" -type f | wc -l)
    echo -e "${GREEN}✓${NC} Directory exists: $1 ($file_count files)"
    return 0
  else
    echo -e "${RED}✗${NC} Directory missing: $1"
    return 1
  fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DEBUG: $DEBUG"
echo "PORT: $PORT"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Static File Directories"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "/app/staticfiles"
check_dir "/app/static"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Critical Files Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file "/app/staticfiles/index.html"
check_file "/app/manage.py"
check_file "/app/config/wsgi.py"
check_file "/app/staticfiles/assets/index-CvI8qVw6.css" || echo -e "${YELLOW}!${NC} Main CSS file not found (may have different hash)"
check_file "/app/staticfiles/assets/index-d5Gq7B8F.js" || echo -e "${YELLOW}!${NC} Main JS file not found (may have different hash)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. File Statistics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "/app/staticfiles" ]; then
  total_files=$(find /app/staticfiles -type f | wc -l)
  total_size=$(du -sh /app/staticfiles | cut -f1)
  echo "Total static files: $total_files"
  echo "Total static size: $total_size"
  
  echo ""
  echo "File breakdown:"
  find /app/staticfiles -type f -name "*.html" | wc -l | xargs echo "  HTML files:"
  find /app/staticfiles -type f -name "*.css" | wc -l | xargs echo "  CSS files:"
  find /app/staticfiles -type f -name "*.js" | wc -l | xargs echo "  JS files:"
  find /app/staticfiles -type f -name "*.woff*" -o -name "*.ttf" | wc -l | xargs echo "  Font files:"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Sample Files in /app/staticfiles/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "/app/staticfiles" ]; then
  find /app/staticfiles -maxdepth 2 -type f | head -20
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Test Django Management Commands"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing: python manage.py check"
cd /app
python manage.py check 2>&1 | tail -5
check_success "Django checks passed"

echo ""
echo "████████████████████████████████████████████████████████████████████"
echo "█ Diagnostic Complete"
echo "████████████████████████████████████████████████████████████████████"
echo ""
echo "If deployment is still not working, check:"
echo "  1. /diagnostic/ endpoint for detailed JSON report"
echo "  2. /diagnostic/summary/ for quick text summary"
echo "  3. Application logs for runtime errors"
echo ""
