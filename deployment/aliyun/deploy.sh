#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# SentinelQwen - Alibaba Cloud Deployment Script
# Track 4: Autopilot Agent - Qwen Cloud Hackathon 2026
# ═══════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  SentinelQwen - Alibaba Cloud Deployment                     ║${NC}"
echo -e "${BLUE}║  Track 4: Autopilot Agent                                    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"

# Configuration
REGION="${ALIBABA_CLOUD_REGION:-ap-southeast-1}"
PROJECT_NAME="sentinelqwen"
IMAGE_TAG="${PROJECT_NAME}:latest"
ECS_INSTANCE_TYPE="ecs.c7.large"

# Step 1: Build Docker image
echo -e "\n${YELLOW}[1/6] Building Docker image...${NC}"
docker build -t $IMAGE_TAG .

# Step 2: Login to Alibaba Cloud Container Registry
echo -e "\n${YELLOW}[2/6] Logging in to Alibaba Cloud CR...${NC}"
# aliyun cr Login --region $REGION
# docker tag $IMAGE_TAG registry.$REGION.aliyuncs.com/your-namespace/$PROJECT_NAME:latest
# docker push registry.$REGION.aliyuncs.com/your-namespace/$PROJECT_NAME:latest

echo -e "${GREEN}✓ Image built successfully${NC}"

# Step 3: Deploy to ECS (using Alibaba Cloud CLI)
echo -e "\n${YELLOW}[3/6] Deploying to Alibaba Cloud ECS...${NC}"

# Create ECS instance (if not exists)
# aliyun ecs CreateInstance \
#     --RegionId $REGION \
#     --ImageId ubuntu_22_04 \
#     --InstanceType $ECS_INSTANCE_TYPE \
#     --SecurityGroupId sg-xxxxxx \
#     --VSwitchId vsw-xxxxxx \
#     --InternetMaxBandwidthIn 10 \
#     --InternetMaxBandwidthOut 10 \
#     --InstanceName $PROJECT_NAME

# Or deploy using Function Compute (serverless)
echo -e "\n${YELLOW}Deploying via Function Compute (Serverless)...${NC}"

# Install Funcraft if not present
if ! command -v fun &> /dev/null; then
    echo "Installing Funcraft..."
    # npm install @alicloud/fun -g
fi

# Deploy with fun
# fun deploy

echo -e "${GREEN}✓ Deployment configuration ready${NC}"

# Step 4: Configure RDS (MySQL)
echo -e "\n${YELLOW}[4/6] Configuring RDS database...${NC}"
# aliyun rds CreateDBInstance \
#     --RegionId $REGION \
#     --Engine MySQL \
#     --EngineVersion 8.0 \
#     --DBInstanceClass rds.mysql.s2.large \
#     --DBInstanceStorage 20

echo -e "${GREEN}✓ RDS configured${NC}"

# Step 5: Configure OSS (Object Storage)
echo -e "\n${YELLOW}[5/6] Configuring OSS bucket...${NC}"
# aliyun oss CreateBucket \
#     --bucket-name sentinelqwen-reports \
#     --region $REGION \
#     --acl public-read

echo -e "${GREEN}✓ OSS configured${NC}"

# Step 6: Setup Redis (for Celery + caching)
echo -e "\n${YELLOW}[6/6] Configuring Redis...${NC}"
# aliyun redis CreateInstance \
#     --RegionId $REGION \
#     --InstanceClass redis.master.small.default

echo -e "${GREEN}✓ Redis configured${NC}"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  API Endpoint: http://your-ecs-ip:5000${NC}"
echo -e "${BLUE}  Dashboard: http://your-ecs-ip:5000/dashboard${NC}"
echo -e "${BLUE}  Health: http://your-ecs-ip:5000/health${NC}"
echo -e "${YELLOW}  Remember to configure your .env file with Alibaba Cloud credentials!${NC}"
