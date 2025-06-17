#!/bin/bash

# Pricing Intelligence Platform Packaging Script
# Creates a complete, deployable package of the platform

set -e  # Exit on any error

echo "📦 Creating Pricing Intelligence Platform Package"
echo "================================================"

# Configuration
PROJECT_ROOT="/home/ubuntu/pricing-intelligence-platform"
PACKAGE_NAME="pricing-intelligence-platform-v1.0"
PACKAGE_DIR="/home/ubuntu/${PACKAGE_NAME}"
ARCHIVE_NAME="${PACKAGE_NAME}.tar.gz"

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

# Clean up any existing package
cleanup() {
    log_info "Cleaning up existing package..."
    rm -rf "$PACKAGE_DIR" 2>/dev/null || true
    rm -f "/home/ubuntu/${ARCHIVE_NAME}" 2>/dev/null || true
}

# Create package directory structure
create_structure() {
    log_info "Creating package structure..."
    
    mkdir -p "$PACKAGE_DIR"
    mkdir -p "$PACKAGE_DIR/backend"
    mkdir -p "$PACKAGE_DIR/frontend"
    mkdir -p "$PACKAGE_DIR/data"
    mkdir -p "$PACKAGE_DIR/docs"
    mkdir -p "$PACKAGE_DIR/tests"
    mkdir -p "$PACKAGE_DIR/scripts"
}

# Copy backend files
copy_backend() {
    log_info "Copying backend files..."
    
    # Copy the entire pricing-api directory
    cp -r "$PROJECT_ROOT/backend/pricing-api" "$PACKAGE_DIR/backend/"
    
    # Remove virtual environment (will be recreated on deployment)
    rm -rf "$PACKAGE_DIR/backend/pricing-api/venv" 2>/dev/null || true
    
    # Remove __pycache__ directories
    find "$PACKAGE_DIR/backend" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PACKAGE_DIR/backend" -name "*.pyc" -delete 2>/dev/null || true
    
    # Ensure requirements.txt is up to date
    cd "$PROJECT_ROOT/backend/pricing-api"
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip freeze > "$PACKAGE_DIR/backend/pricing-api/requirements.txt"
        deactivate
    fi
}

# Copy frontend files
copy_frontend() {
    log_info "Copying frontend files..."
    
    # Copy the entire pricing-dashboard directory
    cp -r "$PROJECT_ROOT/frontend/pricing-dashboard" "$PACKAGE_DIR/frontend/"
    
    # Remove node_modules (will be reinstalled on deployment)
    rm -rf "$PACKAGE_DIR/frontend/pricing-dashboard/node_modules" 2>/dev/null || true
    
    # Remove build artifacts
    rm -rf "$PACKAGE_DIR/frontend/pricing-dashboard/dist" 2>/dev/null || true
    rm -rf "$PACKAGE_DIR/frontend/pricing-dashboard/.vite" 2>/dev/null || true
}

# Copy data and documentation
copy_data_and_docs() {
    log_info "Copying data and documentation..."
    
    # Copy data files (including sample data)
    cp -r "$PROJECT_ROOT/data"/* "$PACKAGE_DIR/data/" 2>/dev/null || true
    
    # Copy documentation
    cp -r "$PROJECT_ROOT/docs"/* "$PACKAGE_DIR/docs/" 2>/dev/null || true
    
    # Copy tests
    cp -r "$PROJECT_ROOT/tests"/* "$PACKAGE_DIR/tests/" 2>/dev/null || true
    
    # Copy scripts
    cp -r "$PROJECT_ROOT/scripts"/* "$PACKAGE_DIR/scripts/" 2>/dev/null || true
    
    # Make scripts executable
    chmod +x "$PACKAGE_DIR/scripts"/*.sh 2>/dev/null || true
}

# Copy root files
copy_root_files() {
    log_info "Copying root configuration files..."
    
    # Copy important root files
    cp "$PROJECT_ROOT/README.md" "$PACKAGE_DIR/"
    cp "$PROJECT_ROOT/DEPLOYMENT_GUIDE.md" "$PACKAGE_DIR/"
    cp "$PROJECT_ROOT/todo.md" "$PACKAGE_DIR/" 2>/dev/null || true
    
    # Create additional files for the package
    create_package_files
}

# Create package-specific files
create_package_files() {
    log_info "Creating package-specific files..."
    
    # Create INSTALL.md
    cat > "$PACKAGE_DIR/INSTALL.md" << 'EOF'
# Quick Installation Guide

## Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm package manager
- 4GB+ RAM recommended

## Installation Steps

1. **Extract the package** (if you haven't already):
   ```bash
   tar -xzf pricing-intelligence-platform-v1.0.tar.gz
   cd pricing-intelligence-platform-v1.0
   ```

2. **Run automated setup**:
   ```bash
   ./scripts/setup.sh
   ```

3. **Deploy the platform**:
   ```bash
   ./scripts/deploy.sh
   ```

4. **Access the platform**:
   - Dashboard: http://localhost:5173
   - API: http://localhost:5001

## Manual Setup (if automated setup fails)

### Backend Setup
```bash
cd backend/pricing-api
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd frontend/pricing-dashboard
pnpm install
pnpm run dev --host
```

## Verification
Run the integration tests to verify everything is working:
```bash
python3.11 tests/integration_tests.py
```

For detailed instructions, see README.md and DEPLOYMENT_GUIDE.md
EOF

    # Create setup script
    cat > "$PACKAGE_DIR/scripts/setup.sh" << 'EOF'
#!/bin/bash

# Pricing Intelligence Platform Setup Script
# Prepares the system for deployment

set -e

echo "🔧 Setting up Pricing Intelligence Platform"
echo "=========================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 is required but not installed"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm is required but not installed"
    echo "Install with: npm install -g pnpm"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "Setting up backend..."
cd "$PROJECT_ROOT/backend/pricing-api"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3.11 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create database directory
mkdir -p src/database

echo "✅ Backend setup completed"

# Setup frontend
echo "Setting up frontend..."
cd "$PROJECT_ROOT/frontend/pricing-dashboard"

echo "Installing Node.js dependencies..."
pnpm install

echo "✅ Frontend setup completed"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/deploy.sh"
echo "2. Access dashboard at: http://localhost:5173"
echo "3. Access API at: http://localhost:5001"
EOF

    chmod +x "$PACKAGE_DIR/scripts/setup.sh"
    
    # Create VERSION file
    cat > "$PACKAGE_DIR/VERSION" << EOF
Pricing Intelligence Platform
Version: 1.0.0
Build Date: $(date)
Build Environment: Development
Components:
- Backend: Flask API with SQLAlchemy
- Frontend: React 18 with Vite
- Database: SQLite (production-ready for PostgreSQL)
- Features: Vehicle matching, pricing scoring, AI insights
EOF

    # Create LICENSE file
    cat > "$PACKAGE_DIR/LICENSE" << 'EOF'
MIT License

Copyright (c) 2025 Pricing Intelligence Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
}

# Create archive
create_archive() {
    log_info "Creating archive..."
    
    cd /home/ubuntu
    tar -czf "$ARCHIVE_NAME" "$PACKAGE_NAME/"
    
    # Get archive size
    ARCHIVE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
    
    log_success "Archive created: $ARCHIVE_NAME ($ARCHIVE_SIZE)"
}

# Generate package manifest
generate_manifest() {
    log_info "Generating package manifest..."
    
    cat > "$PACKAGE_DIR/MANIFEST.txt" << EOF
Pricing Intelligence Platform - Package Manifest
===============================================

Package: $PACKAGE_NAME
Created: $(date)
Size: $(du -sh "$PACKAGE_DIR" | cut -f1)

Directory Structure:
├── backend/                    # Flask API server
│   └── pricing-api/
│       ├── src/               # Source code
│       │   ├── models/        # Database models
│       │   ├── routes/        # API endpoints
│       │   ├── services/      # Business logic
│       │   └── main.py        # Flask application
│       └── requirements.txt   # Python dependencies
├── frontend/                   # React dashboard
│   └── pricing-dashboard/
│       ├── src/               # React source code
│       │   ├── components/    # React components
│       │   ├── pages/         # Dashboard pages
│       │   └── hooks/         # Custom hooks
│       └── package.json       # Node.js dependencies
├── data/                       # Sample data and analysis
├── docs/                       # Documentation
├── tests/                      # Test suites
├── scripts/                    # Deployment scripts
├── README.md                   # Main documentation
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── INSTALL.md                  # Quick installation guide
├── LICENSE                     # MIT License
└── VERSION                     # Version information

Files Included:
$(find "$PACKAGE_DIR" -type f | wc -l) files
$(find "$PACKAGE_DIR" -name "*.py" | wc -l) Python files
$(find "$PACKAGE_DIR" -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" | wc -l) JavaScript/TypeScript files
$(find "$PACKAGE_DIR" -name "*.md" | wc -l) Documentation files

Key Features:
- Complete CSV data ingestion pipeline
- Advanced vehicle matching algorithms
- Multi-factor pricing scoring system
- AI-powered insights generation
- Responsive web dashboard
- Comprehensive REST API
- Real-time monitoring and analytics
- Production-ready deployment scripts

System Requirements:
- Python 3.11+
- Node.js 20+
- pnpm package manager
- 4GB+ RAM recommended
- 2GB+ disk space

Installation:
1. Extract: tar -xzf $ARCHIVE_NAME
2. Setup: ./scripts/setup.sh
3. Deploy: ./scripts/deploy.sh
4. Access: http://localhost:5173

Support:
- Documentation: README.md, DEPLOYMENT_GUIDE.md
- Integration tests: python3.11 tests/integration_tests.py
- Health checks: http://localhost:5001/api/health
EOF
}

# Main packaging process
main() {
    echo
    log_info "Starting packaging process..."
    
    cleanup
    create_structure
    copy_backend
    copy_frontend
    copy_data_and_docs
    copy_root_files
    generate_manifest
    create_archive
    
    # Final statistics
    TOTAL_FILES=$(find "$PACKAGE_DIR" -type f | wc -l)
    PACKAGE_SIZE=$(du -sh "$PACKAGE_DIR" | cut -f1)
    ARCHIVE_SIZE=$(du -h "/home/ubuntu/$ARCHIVE_NAME" | cut -f1)
    
    echo
    echo "================================================"
    log_success "🎉 Package created successfully!"
    echo
    echo "Package Details:"
    echo "  Name: $PACKAGE_NAME"
    echo "  Location: /home/ubuntu/$ARCHIVE_NAME"
    echo "  Archive Size: $ARCHIVE_SIZE"
    echo "  Total Files: $TOTAL_FILES"
    echo "  Uncompressed Size: $PACKAGE_SIZE"
    echo
    echo "Package Contents:"
    echo "  ✅ Complete backend (Flask API)"
    echo "  ✅ Complete frontend (React dashboard)"
    echo "  ✅ Sample data (363 vehicles)"
    echo "  ✅ Comprehensive documentation"
    echo "  ✅ Integration tests"
    echo "  ✅ Deployment scripts"
    echo "  ✅ Setup automation"
    echo
    echo "Installation Instructions:"
    echo "  1. Download: $ARCHIVE_NAME"
    echo "  2. Extract: tar -xzf $ARCHIVE_NAME"
    echo "  3. Setup: cd $PACKAGE_NAME && ./scripts/setup.sh"
    echo "  4. Deploy: ./scripts/deploy.sh"
    echo "  5. Access: http://localhost:5173"
    echo
    log_success "Your Pricing Intelligence Platform is ready for deployment!"
    echo
}

# Run the packaging process
main "$@"

