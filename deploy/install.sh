#!/bin/bash
# AKAVIN OS - Complete Installation Script
# Run: curl -sSL https://raw.githubusercontent.com/akavinprimepartners/visit/main/deploy/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AKAVIN OS Installation Script${NC}"
echo "================================="

# Check system requirements
echo -e "${YELLOW}📋 Checking system requirements...${NC}"

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${GREEN}✅ Linux detected${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}✅ macOS detected${NC}"
else
    echo -e "${RED}❌ Unsupported OS. Please use Linux or macOS.${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Git...${NC}"
    sudo apt-get update && sudo apt-get install git -y
else
    echo -e "${GREEN}✅ Git already installed${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Python...${NC}"
    sudo apt-get install python3 python3-pip -y
else
    echo -e "${GREEN}✅ Python already installed${NC}"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo -e "${GREEN}✅ Node.js already installed${NC}"
fi

# Clone repository
echo -e "${YELLOW}📥 Cloning AKAVIN OS repository...${NC}"
if [ -d "akavin-os" ]; then
    echo -e "${YELLOW}⚠️  Directory exists. Pulling latest changes...${NC}"
    cd akavin-os
    git pull
else
    git clone https://github.com/akavinprimepartners/visit.git akavin-os
    cd akavin-os
fi

# Setup environment
echo -e "${YELLOW}🔧 Setting up environment...${NC}"
cp docker/.env.example .env
cp backend/.env.production backend/.env

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/g" backend/.env

# Install dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip3 install -r backend/requirements.txt

echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
cd frontend && npm install && cd ..

# Download NLP models
echo -e "${YELLOW}🧠 Downloading AI models...${NC}"
python3 -m spacy download en_core_web_sm

# Setup database
echo -e "${YELLOW}🗄️ Setting up database...${NC}"
python3 -c "from backend.app.core.database import Database; import asyncio; asyncio.run(Database().connect())"

# Pull Ollama model
echo -e "${YELLOW}🦙 Pulling Ollama model...${NC}"
if command -v ollama &> /dev/null; then
    ollama pull llama2
else
    echo -e "${YELLOW}⚠️  Ollama not installed. Please install from https://ollama.ai${NC}"
fi

# Setup Nginx
echo -e "${YELLOW}🔧 Setting up Nginx...${NC}"
if command -v nginx &> /dev/null; then
    sudo cp nginx/nginx.conf /etc/nginx/sites-available/akavin
    sudo ln -sf /etc/nginx/sites-available/akavin /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
else
    echo -e "${YELLOW}⚠️  Nginx not installed. Skipping...${NC}"
fi

echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Update DNS records to point to this server"
echo "2. Run: docker-compose -f docker/docker-compose.prod.yml up -d"
echo "3. Access: https://www.visit.akavin.online"
echo ""
echo "For SSL certificate: sudo certbot --nginx -d www.visit.akavin.online"
