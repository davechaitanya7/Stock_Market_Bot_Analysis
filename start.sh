#!/bin/bash

echo "Starting Stock Trading Bot..."
echo ""

# Start backend in background
echo "Starting backend server on port 8000..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "Backend PID: $BACKEND_PID"
echo ""
echo "Starting frontend dev server on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "==================================="
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo "==================================="
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait
