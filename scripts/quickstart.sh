#!/bin/bash

# CoinScribe Quickstart Script
# This script helps new developers get up and running quickly

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print banner
echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║                                           ║"
echo "║      CoinScribe Quickstart Setup          ║"
echo "║                                           ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Check prerequisites
print_header "Checking Prerequisites"

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js is installed: $NODE_VERSION"
    
    # Check if version is >= 18 (handle various version formats)
    MAJOR_VERSION=$(node --version | sed 's/v//' | cut -d'.' -f1 | sed 's/[^0-9].*//')
    if [ -n "$MAJOR_VERSION" ] && [ "$MAJOR_VERSION" -ge 0 ] 2>/dev/null; then
        if [ "$MAJOR_VERSION" -lt 18 ]; then
            print_error "Node.js version must be >= 18.0.0"
            print_info "Please upgrade Node.js: https://nodejs.org/"
            exit 1
        fi
    else
        print_warning "Could not parse Node.js version, skipping version check"
    fi
else
    print_error "Node.js is not installed"
    print_info "Please install Node.js (>= 18.0.0): https://nodejs.org/"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm is installed: v$NPM_VERSION"
else
    print_error "npm is not installed"
    print_info "npm should come with Node.js"
    exit 1
fi

# Check Git
if command_exists git; then
    GIT_VERSION=$(git --version)
    print_success "Git is installed: $GIT_VERSION"
else
    print_warning "Git is not installed (optional for development)"
fi

# Install dependencies
print_header "Installing Dependencies"

print_info "Running npm install..."
if npm install; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Run quality checks
print_header "Running Quality Checks"

# Linting
print_info "Running ESLint..."
if npm run lint; then
    print_success "Linting passed"
else
    print_error "Linting failed"
    print_warning "Try running: npm run lint:fix"
    exit 1
fi

# Type checking
print_info "Running TypeScript type check..."
if npm run type-check; then
    print_success "Type checking passed"
else
    print_error "Type checking failed"
    exit 1
fi

# Build
print_header "Building Application"

print_info "Running production build..."
if npm run build; then
    print_success "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Security audit
print_header "Security Audit"

print_info "Running npm audit for production dependencies..."
if npm audit --production --audit-level=moderate; then
    print_success "No production vulnerabilities found"
else
    print_warning "Some vulnerabilities detected in dev dependencies"
    print_info "Run 'npm audit' for details"
fi

# Success message
print_header "Setup Complete!"

echo ""
print_success "CoinScribe is ready to use!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Start development server:"
echo "     ${GREEN}npm run dev${NC}"
echo ""
echo "  2. Open your browser:"
echo "     ${GREEN}http://localhost:5173${NC}"
echo ""
echo "  3. Build for production:"
echo "     ${GREEN}npm run build${NC}"
echo ""
echo "  4. Preview production build:"
echo "     ${GREEN}npm run preview${NC}"
echo ""
echo "Documentation:"
echo "  - README.md         - Quick start guide"
echo "  - BUILD_GUIDE.md    - Detailed build instructions"
echo "  - DEPLOYMENT.md     - Deployment guide"
echo "  - .github/CICD.md   - CI/CD documentation"
echo ""
print_info "Happy coding! 🚀"
echo ""
