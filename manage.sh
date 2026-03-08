#!/bin/bash

# Define paths
APP_DIR="/home/joopstark/dev/project/carpool-app"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

start() {
    echo "Starting Backend Server..."
    cd "$BACKEND_DIR" || exit
    source venv/bin/activate
    # Run backend in background
    python run.py > backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > wrapper_backend.pid
    echo "Backend started (PID $BACKEND_PID). Logs in $BACKEND_DIR/backend.log"

    echo "Starting Frontend Server..."
    cd "$FRONTEND_DIR" || exit
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    # Run frontend in background
    npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > wrapper_frontend.pid
    echo "Frontend started (PID $FRONTEND_PID). Logs in $FRONTEND_DIR/frontend.log"
    
    echo "======================================"
    echo "Servers are running! "
    echo "Use './manage.sh stop' to gracefully shut them down."
    echo "Use './manage.sh status' to view their running status."
    echo "======================================"
}

stop() {
    echo "Stopping Backend Server..."
    if [ -f "$BACKEND_DIR/wrapper_backend.pid" ]; then
        kill -9 $(cat "$BACKEND_DIR/wrapper_backend.pid") 2>/dev/null
        rm "$BACKEND_DIR/wrapper_backend.pid"
        echo "Backend stopped."
    else
        echo "No backend PID file found. Attempting pkill..."
        pkill -f "python run.py" 2>/dev/null
    fi

    echo "Stopping Frontend Server..."
    if [ -f "$FRONTEND_DIR/wrapper_frontend.pid" ]; then
        # Vite spawns child processes, kill directly and strictly
        kill -9 $(cat "$FRONTEND_DIR/wrapper_frontend.pid") 2>/dev/null
        rm "$FRONTEND_DIR/wrapper_frontend.pid"
        pkill -f "vite" 2>/dev/null
        echo "Frontend stopped."
    else
        echo "No frontend PID file found. Attempting pkill..."
        pkill -f "npm run dev" 2>/dev/null
        pkill -f "vite" 2>/dev/null
    fi
    echo "All stopped."
}

status() {
    if pgrep -f "python run.py" > /dev/null; then
        echo "Backend is RUNNING."
    else
        echo "Backend is STOPPED."
    fi
    
    if pgrep -f "vite" > /dev/null; then
        echo "Frontend is RUNNING."
    else
        echo "Frontend is STOPPED."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac
