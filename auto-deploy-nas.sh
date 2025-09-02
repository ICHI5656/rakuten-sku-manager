#!/bin/bash
# Automated NAS deployment script

NAS_IP="192.168.24.240"
NAS_USER="quest"
NAS_PATH="/home/quest/rakuten-sku"
EXPORT_DIR="export"

echo "======================================"
echo "Rakuten SKU Manager - Auto Deploy"
echo "======================================"
echo ""

# Step 1: Create remote directory
echo "Creating directory on NAS..."
sshpass -p "Ichio_22520113" ssh -o StrictHostKeyChecking=no $NAS_USER@$NAS_IP "mkdir -p $NAS_PATH"

# Step 2: Copy files
echo "Transferring files to NAS..."
sshpass -p "Ichio_22520113" scp -o StrictHostKeyChecking=no $EXPORT_DIR/backend.tar $NAS_USER@$NAS_IP:$NAS_PATH/
sshpass -p "Ichio_22520113" scp -o StrictHostKeyChecking=no $EXPORT_DIR/frontend-fixed.tar $NAS_USER@$NAS_IP:$NAS_PATH/frontend.tar
sshpass -p "Ichio_22520113" scp -o StrictHostKeyChecking=no docker-compose-nas-simple.yml $NAS_USER@$NAS_IP:$NAS_PATH/docker-compose.yml

# Step 3: Load images and start containers
echo "Loading Docker images on NAS..."
sshpass -p "Ichio_22520113" ssh -o StrictHostKeyChecking=no $NAS_USER@$NAS_IP "cd $NAS_PATH && sudo docker load -i backend.tar && sudo docker load -i frontend.tar"

echo "Starting containers..."
sshpass -p "Ichio_22520113" ssh -o StrictHostKeyChecking=no $NAS_USER@$NAS_IP "cd $NAS_PATH && sudo docker-compose down && sudo docker-compose up -d"

# Step 4: Check status
echo ""
echo "Checking deployment status..."
sshpass -p "Ichio_22520113" ssh -o StrictHostKeyChecking=no $NAS_USER@$NAS_IP "sudo docker ps | grep rakuten"

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo "Access URLs:"
echo "- Application: http://$NAS_IP:3000"
echo "- API Docs: http://$NAS_IP:8000/docs"