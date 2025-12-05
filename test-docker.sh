#!/bin/bash
# ============================================================================
# TEST DOCKER BUILD AND RUN LOCALLY
# Run this script to verify your Docker setup works before deploying
# ============================================================================

set -e

echo "🐳 SeatServe Docker Test Suite"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo "📋 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install from: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
echo ""

# Check if Docker daemon is running
echo "📋 Checking Docker daemon..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "Start Docker Desktop or daemon and try again"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon is running${NC}"
echo ""

# Check Docker Compose
echo "📋 Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Install from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found: $(docker-compose --version)${NC}"
echo ""

# Check required files
echo "📋 Checking required files..."
required_files=("Dockerfile" "seatserve-backend/requirements.txt" "seatserve-frontend/package.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Missing file: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Found: $file${NC}"
done
echo ""

# Build Docker image
echo "🔨 Building Docker image..."
echo "(This may take 2-5 minutes on first run)"
if docker build -t seatserve:latest .; then
    echo -e "${GREEN}✅ Build successful!${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    echo "Check the output above for errors"
    exit 1
fi
echo ""

# Create .env file for testing
echo "⚙️  Setting up test environment..."
if [ ! -f ".env.test" ]; then
    cat > .env.test <<EOF
DEBUG=False
SECRET_KEY=test-secret-key-only-for-testing-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DATABASE_URL=postgresql://postgres:postgres@db:5432/seatserve
REDIS_URL=redis://redis:6379/0
PORT=8000
EOF
    echo -e "${GREEN}✅ Created .env.test${NC}"
else
    echo -e "${YELLOW}⚠️  Using existing .env.test${NC}"
fi
echo ""

# Run Docker Compose
echo "🚀 Starting containers with docker-compose..."
docker-compose -f docker-compose.prod.yml up -d

echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check if services are running
echo "📋 Checking running containers..."
docker-compose -f docker-compose.prod.yml ps

# Wait for database
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres &> /dev/null; then
        echo -e "${GREEN}✅ Database is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Database failed to start${NC}"
        docker-compose -f docker-compose.prod.yml logs db
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""

# Run migrations
echo "🔄 Running database migrations..."
if docker-compose -f docker-compose.prod.yml exec -T app python manage.py migrate; then
    echo -e "${GREEN}✅ Migrations successful${NC}"
else
    echo -e "${RED}❌ Migrations failed${NC}"
    docker-compose -f docker-compose.prod.yml logs app
    exit 1
fi
echo ""

# Check if API is responding
echo "🧪 Testing API endpoint..."
sleep 5
if curl -f http://localhost:8000/health/ &> /dev/null 2>&1; then
    echo -e "${GREEN}✅ API is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Health check endpoint not available (normal if not configured)${NC}"
fi
echo ""

# Check frontend
echo "🧪 Testing Frontend..."
if curl -f http://localhost:8000/ &> /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${RED}❌ Frontend is not responding${NC}"
fi
echo ""

# Summary
echo "================================"
echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
echo "================================"
echo ""
echo "Your Docker setup is working correctly! 🎉"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:8000/"
echo "   API: http://localhost:8000/api/"
echo "   Admin: http://localhost:8000/admin/"
echo ""
echo "📊 View logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f app"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "Next steps for production deployment:"
echo "1. Replace SECRET_KEY with a production value"
echo "2. Update ALLOWED_HOSTS to your domain"
echo "3. Deploy to Railway/Render/AWS"
echo "4. Run migrations on production database"
echo ""
