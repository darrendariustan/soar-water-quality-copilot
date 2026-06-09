@echo off
echo Starting WaterForAll Environment...
docker-compose up --build -d
echo Environment started. 
echo Frontend is accessible at http://localhost:3000
echo Backend API is accessible at http://localhost:8000
