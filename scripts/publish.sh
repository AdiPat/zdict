#!/bin/bash
# publish.sh - Robust script to publish zdict to PyPI
# This script includes comprehensive checks and fallbacks for safe publishing

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="zdict"
VERSION_FILE="zdict/__init__.py"
TEST_PYPI_URL="https://test.pypi.org/legacy/"
PROD_PYPI_URL="https://upload.pypi.org/legacy/"

# Functions
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        return 1
    fi
    return 0
}

get_version() {
    python -c "import re; content = open('$VERSION_FILE').read(); print(re.search(r'__version__\s*=\s*[\"']([^\"']+)[\"']', content).group(1))"
}

check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "Working directory has uncommitted changes"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    return 0
}

check_version_tag() {
    local version=$1
    if git rev-parse "v$version" >/dev/null 2>&1; then
        print_success "Git tag v$version exists"
    else
        print_warning "Git tag v$version does not exist"
        read -p "Create tag now? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            git tag -a "v$version" -m "Release version $version"
            print_success "Created tag v$version"
        fi
    fi
}

check_pypi_version() {
    local index_url=$1
    local version=$2
    
    # Check if package version already exists
    if pip index versions $PACKAGE_NAME --index-url "$index_url" 2>/dev/null | grep -q "$version"; then
        return 0  # Version exists
    else
        return 1  # Version does not exist
    fi
}

run_tests() {
    print_step "Running tests..."
    if python -m pytest tests/ -q; then
        print_success "All tests passed"
    else
        print_error "Tests failed. Fix issues before publishing."
        return 1
    fi
}

build_distributions() {
    print_step "Building distributions..."
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info
    
    # Build source distribution
    print_step "Building source distribution..."
    python -m build --sdist
    
    # Build wheel
    print_step "Building wheel distribution..."
    python -m build --wheel
    
    # List built distributions
    print_success "Built distributions:"
    ls -la dist/
}

check_distributions() {
    print_step "Checking distributions..."
    
    # Check with twine
    if twine check dist/*; then
        print_success "Distribution checks passed"
    else
        print_error "Distribution checks failed"
        return 1
    fi
}

upload_to_pypi() {
    local index_url=$1
    local repository_name=$2
    
    print_step "Uploading to $repository_name..."
    
    # Check for API token
    if [[ -z "${TWINE_PASSWORD:-}" ]]; then
        print_warning "No API token found in environment"
        echo "Please enter your PyPI API token (starts with 'pypi-'):"
        read -s TWINE_PASSWORD
        export TWINE_PASSWORD
        export TWINE_USERNAME="__token__"
    fi
    
    # Upload with twine
    if twine upload --repository-url "$index_url" dist/* --verbose; then
        print_success "Successfully uploaded to $repository_name"
        return 0
    else
        print_error "Upload to $repository_name failed"
        return 1
    fi
}

# Main script
main() {
    echo "🚀 zdict Publishing Script"
    echo "========================="
    echo
    
    # Check required commands
    print_step "Checking required tools..."
    check_command python || exit 1
    check_command pip || exit 1
    check_command git || exit 1
    check_command twine || { print_error "Please install twine: pip install twine"; exit 1; }
    check_command build || { print_error "Please install build: pip install build"; exit 1; }
    print_success "All required tools found"
    
    # Get current version
    print_step "Getting package version..."
    VERSION=$(get_version)
    print_success "Package version: $VERSION"
    
    # Check git status
    print_step "Checking git status..."
    check_git_status || exit 1
    
    # Check git tag
    check_version_tag "$VERSION"
    
    # Run tests
    run_tests || exit 1
    
    # Check if version already exists on PyPI
    print_step "Checking if version exists on PyPI..."
    if check_pypi_version "$PROD_PYPI_URL" "$VERSION"; then
        print_error "Version $VERSION already exists on PyPI!"
        echo "Please update the version in $VERSION_FILE before publishing."
        exit 1
    else
        print_success "Version $VERSION is not on PyPI (ready to publish)"
    fi
    
    # Build distributions
    build_distributions || exit 1
    
    # Check distributions
    check_distributions || exit 1
    
    # Ask about Test PyPI
    echo
    read -p "Upload to Test PyPI first? (recommended) (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if check_pypi_version "$TEST_PYPI_URL" "$VERSION"; then
            print_warning "Version $VERSION already exists on Test PyPI"
        else
            upload_to_pypi "$TEST_PYPI_URL" "Test PyPI" || {
                read -p "Test PyPI upload failed. Continue to PyPI anyway? (y/N) " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    exit 1
                fi
            }
            
            print_success "Package uploaded to Test PyPI"
            echo "Test with: pip install -i https://test.pypi.org/simple/ $PACKAGE_NAME==$VERSION"
            echo
            read -p "Press Enter to continue to PyPI upload..."
        fi
    fi
    
    # Final confirmation
    echo
    print_warning "Ready to upload to PyPI (Production)"
    echo "Package: $PACKAGE_NAME"
    echo "Version: $VERSION"
    echo
    read -p "Are you sure you want to publish to PyPI? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Publishing cancelled"
        exit 0
    fi
    
    # Upload to PyPI
    upload_to_pypi "$PROD_PYPI_URL" "PyPI" || exit 1
    
    # Success!
    echo
    print_success "🎉 Successfully published $PACKAGE_NAME $VERSION to PyPI!"
    echo
    echo "Next steps:"
    echo "1. Test installation: pip install $PACKAGE_NAME==$VERSION"
    echo "2. Create GitHub release: https://github.com/AdiPat/zdict/releases/new"
    echo "3. Announce the release"
    echo
    
    # Push tags if not already pushed
    read -p "Push git tag to remote? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        git push origin "v$VERSION"
        print_success "Pushed tag v$VERSION to remote"
    fi
}

# Run main function
main "$@"