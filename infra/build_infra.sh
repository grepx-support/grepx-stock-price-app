#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Starting infrastructure services..."
docker-compose -f docker-compose.yaml up -d

echo ""
echo "Infrastructure started:"
echo "  Redis:     localhost:6379"
echo "  MongoDB:   localhost:27017 (admin/password123)"
echo "  RabbitMQ:  localhost:5672 (admin/password123)"
echo "  RabbitMQ UI: http://localhost:15672"
echo ""
echo "Stop with: docker-compose down"