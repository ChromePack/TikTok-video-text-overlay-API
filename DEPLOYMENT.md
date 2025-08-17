# TikTok Text Overlay API - Production Deployment Guide

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

1. **Set up SSH key in GitHub Secrets:**
   ```bash
   # Generate SSH key pair if you don't have one
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   
   # Copy public key to VPS
   ssh-copy-id root@148.230.93.128
   
   # Copy private key content to GitHub Secret named 'VPS_SSH_KEY'
   cat ~/.ssh/id_rsa
   ```

2. **Push to main branch:**
   - Any push to `main` branch will automatically deploy to VPS
   - Monitor deployment in GitHub Actions tab

### Option 2: Manual Deployment

1. **Make deploy script executable:**
   ```bash
   chmod +x deploy.sh
   ```

2. **Run deployment:**
   ```bash
   ./deploy.sh
   ```

## 🛠️ Initial VPS Setup

Run this once on your VPS to prepare it:

```bash
# Connect to VPS
ssh root@148.230.93.128

# Update system
apt update && apt upgrade -y

# Install basic tools
apt install -y curl wget git

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /var/www/tiktok-video-text-overlay-api
```

## 📊 Management Commands

### Check Service Status
```bash
ssh root@148.230.93.128 'cd /var/www/tiktok-video-text-overlay-api && docker-compose ps'
```

### View Logs
```bash
ssh root@148.230.93.128 'cd /var/www/tiktok-video-text-overlay-api && docker-compose logs -f'
```

### Restart Service
```bash
ssh root@148.230.93.128 'cd /var/www/tiktok-video-text-overlay-api && docker-compose restart'
```

### Update and Redeploy
```bash
ssh root@148.230.93.128 'cd /var/www/tiktok-video-text-overlay-api && git pull && docker-compose up --build -d'
```

## 🔍 Health Monitoring

- **Health Check URL:** `http://148.230.93.128:3003/health`
- **API Root:** `http://148.230.93.128:3003/`
- **Service Status:** `docker-compose ps`

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs

# Check system resources
htop
df -h
```

### Port Issues
```bash
# Check what's using port 3003
netstat -tulpn | grep 3003

# Kill process if needed
sudo kill -9 $(lsof -t -i:3003)
```

### Container Issues
```bash
# Remove all containers and rebuild
docker-compose down
docker system prune -f
docker-compose up --build -d
```

## 🔧 Configuration

### Environment Variables
Edit `docker-compose.yml` to modify:
- `PORT`: Service port (default: 3003)
- `HOST`: Bind address (default: 0.0.0.0)

### Resource Limits
Add to `docker-compose.yml` under service:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

## 🔐 Security Notes

- API runs on port 3003 - ensure firewall allows this
- Consider using nginx as reverse proxy for SSL
- Regular security updates: `apt update && apt upgrade -y`

## 🆚 Why This is Better Than PM2

- ✅ **Containerization**: Isolated environment, consistent across dev/prod
- ✅ **Auto-restart**: Docker handles crashes better than PM2
- ✅ **Resource management**: Built-in memory/CPU limits
- ✅ **Health checks**: Automatic health monitoring
- ✅ **Easy scaling**: Can easily scale to multiple instances
- ✅ **Version control**: Rollbacks via Docker images
- ✅ **CI/CD**: Automated deployment pipeline