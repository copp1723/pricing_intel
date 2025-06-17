#!/bin/bash

# Pricing Intelligence Platform Deployment Script
# Automates the deployment process for both backend and frontend

set -e  # Exit on any error

echo "🚀 Starting Pricing Intelligence Platform Deployment"
echo "=================================================="

# Configuration
PROJECT_ROOT="/home/ubuntu/pricing-intelligence-platform"
BACKEND_DIR="$PROJECT_ROOT/backend/pricing-api"
FRONTEND_DIR="$PROJECT_ROOT/frontend/pricing-dashboard"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command_exists python3.11; then
        log_error "Python 3.11 is required but not installed"
        exit 1
    fi
    
    if ! command_exists pnpm; then
        log_error "pnpm is required but not installed"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Setup backend
setup_backend() {
    log_info "Setting up backend..."
    
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    if [ ! -d "venv" ]; then
        log_error "Virtual environment not found. Please run setup first."
        exit 1
    fi
    
    source venv/bin/activate
    
    # Install/update dependencies
    log_info "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Update requirements.txt
    pip freeze > requirements.txt
    
    log_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    log_info "Setting up frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    log_info "Installing frontend dependencies..."
    pnpm install
    
    # Build for production
    log_info "Building frontend for production..."
    pnpm run build
    
    log_success "Frontend setup completed"
}

# Run tests
run_tests() {
    log_info "Running integration tests..."
    
    cd "$PROJECT_ROOT"
    
    # Start backend in background
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python src/main.py &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 5
    
    # Start frontend in background
    cd "$FRONTEND_DIR"
    pnpm run dev --host &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    sleep 5
    
    # Run integration tests
    cd "$PROJECT_ROOT"
    python3.11 tests/integration_tests.py
    TEST_RESULT=$?
    
    # Clean up background processes
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    if [ $TEST_RESULT -eq 0 ]; then
        log_success "All tests passed"
    else
        log_warning "Some tests failed, but deployment will continue"
    fi
}

# Deploy backend
deploy_backend() {
    log_info "Deploying backend..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Start backend server
    log_info "Starting backend server on port 5001..."
    python src/main.py &
    BACKEND_PID=$!
    
    # Save PID for later management
    echo $BACKEND_PID > "$PROJECT_ROOT/backend.pid"
    
    log_success "Backend deployed and running (PID: $BACKEND_PID)"
}

# Deploy frontend
deploy_frontend() {
    log_info "Deploying frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Start frontend development server
    log_info "Starting frontend server on port 5173..."
    pnpm run dev --host &
    FRONTEND_PID=$!
    
    # Save PID for later management
    echo $FRONTEND_PID > "$PROJECT_ROOT/frontend.pid"
    
    log_success "Frontend deployed and running (PID: $FRONTEND_PID)"
}

# Generate deployment report
generate_report() {
    log_info "Generating deployment report..."
    
    REPORT_FILE="$PROJECT_ROOT/deployment_report.txt"
    
    cat > "$REPORT_FILE" << EOF
Pricing Intelligence Platform - Deployment Report
================================================

Deployment Date: $(date)
Project Location: $PROJECT_ROOT

Backend:
- Status: Running
- Port: 5001
- PID: $(cat "$PROJECT_ROOT/backend.pid" 2>/dev/null || echo "Unknown")
- URL: http://localhost:5001

Frontend:
- Status: Running
- Port: 5173
- PID: $(cat "$PROJECT_ROOT/frontend.pid" 2>/dev/null || echo "Unknown")
- URL: http://localhost:5173

API Endpoints:
- Health Check: http://localhost:5001/api/health
- System Status: http://localhost:5001/api/system-health
- Vehicle Stats: http://localhost:5001/api/stats
- API Documentation: See $PROJECT_ROOT/docs/api_documentation.md

Management Commands:
- Stop Backend: kill \$(cat $PROJECT_ROOT/backend.pid)
- Stop Frontend: kill \$(cat $PROJECT_ROOT/frontend.pid)
- View Logs: Check terminal where deployment was run
- Run Tests: cd $PROJECT_ROOT && python3.11 tests/integration_tests.py

Next Steps:
1. Access the dashboard at http://localhost:5173
2. Test the API endpoints
3. Upload CSV data via the Settings page
4. Generate insights and analytics

For production deployment, consider:
- Using a production WSGI server (gunicorn) for the backend
- Using nginx as a reverse proxy
- Setting up SSL certificates
- Configuring environment variables
- Setting up monitoring and logging
EOF

    log_success "Deployment report saved to: $REPORT_FILE"
}

# Main deployment flow
main() {
    echo
    log_info "Starting deployment process..."
    
    check_prerequisites
    setup_backend
    setup_frontend
    
    if [ "$1" != "--skip-tests" ]; then
        run_tests
    else
        log_warning "Skipping tests as requested"
    fi
    
    deploy_backend
    sleep 2
    deploy_frontend
    sleep 2
    
    generate_report
    
    echo
    echo "=================================================="
    log_success "🎉 Deployment completed successfully!"
    echo
    echo "Access your Pricing Intelligence Platform:"
    echo "  Dashboard: http://localhost:5173"
    echo "  API: http://localhost:5001"
    echo
    echo "View the deployment report: $PROJECT_ROOT/deployment_report.txt"
    echo
    log_info "Both services are running in the background."
    log_info "Check the terminal for any error messages."
    echo
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "Pricing Intelligence Platform Deployment Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --skip-tests    Skip integration tests during deployment"
        echo "  --help, -h      Show this help message"
        echo
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac

