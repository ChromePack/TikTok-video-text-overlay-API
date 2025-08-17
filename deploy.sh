#!/bin/bash

# TikTok Text Overlay API - VPS Deployment Script
# Usage: ./deploy.sh

set -e

VPS_IP="148.230.93.128"
VPS_USER="root"
APP_DIR="/var/www/tiktok-video-text-overlay-api"
REPO_URL="https://github.com/ChromePack/TikTok-video-text-overlay-API.git"

echo "🚀 Deploying TikTok Text Overlay API to VPS..."

# Function to run commands on VPS
run_on_vps() {
    ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "$1"
}

# Check if we can connect to VPS
echo "📡 Testing VPS connection..."
if ! run_on_vps "echo 'Connection successful'"; then
    echo "❌ Cannot connect to VPS. Please check your SSH keys and network."
    exit 1
fi

# Install Docker if not present
echo "🐳 Ensuring Docker is installed..."
run_on_vps "
    if ! command -v docker &> /dev/null; then
        echo 'Installing Docker...'
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo 'Installing Docker Compose...'
        curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
"

# Clone or update repository
echo "📂 Setting up repository..."
run_on_vps "
    if [ ! -d \"$APP_DIR\" ]; then
        echo 'Cloning repository...'
        git clone $REPO_URL $APP_DIR
    else
        echo 'Updating repository...'
        cd $APP_DIR
        git pull origin main
    fi
"

# Deploy with Docker Compose
echo "🔨 Building and deploying..."
run_on_vps "
    cd $APP_DIR
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Remove old images to save space
    docker image prune -f
    
    # Build and start
    docker-compose up --build -d
    
    echo 'Waiting for service to start...'
    sleep 10
    
    # Check if service is running
    if curl -f http://localhost:3003/health; then
        echo '✅ Service is healthy!'
    else
        echo '❌ Service health check failed'
        docker-compose logs
        exit 1
    fi
"

echo "🎉 Deployment completed successfully!"
echo "📍 Your API is now running at: http://$VPS_IP:3003"
echo "🔍 Health check: http://$VPS_IP:3003/health"
echo ""
echo "📊 To monitor logs: ssh $VPS_USER@$VPS_IP 'cd $APP_DIR && docker-compose logs -f'"
echo "🔄 To restart: ssh $VPS_USER@$VPS_IP 'cd $APP_DIR && docker-compose restart'"