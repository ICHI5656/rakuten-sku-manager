#!/bin/bash
# NAS deployment script

echo "Loading Docker images..."
docker load -i backend.tar
docker load -i frontend.tar

echo "Stopping existing containers..."
docker-compose -f docker-compose-simple.yml down

echo "Starting new containers..."
docker-compose -f docker-compose-simple.yml up -d

echo "Checking container status..."
docker ps

echo "Deployment complete!"
echo "Access the application at:"
echo "- Frontend: http://$(hostname -I | awk '{print $1}'):3000"
echo "- Backend API: http://$(hostname -I | awk '{print $1}'):8000/docs"