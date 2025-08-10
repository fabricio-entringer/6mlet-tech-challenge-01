#!/bin/bash

# Docker Setup Validation Script
# Tests the Docker containerization setup for the 6MLET Tech Challenge 01

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print colored output
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Function to run a test
run_test() {
    ((TESTS_RUN++))
    print_test "$1"
}

# Function to check if Docker is available
test_docker_available() {
    run_test "Checking if Docker is available"
    
    if docker info >/dev/null 2>&1; then
        print_pass "Docker is running"
    else
        print_fail "Docker is not running or not installed"
    fi
}

# Function to check if docker-compose is available
test_compose_available() {
    run_test "Checking if docker-compose is available"
    
    if command -v docker-compose >/dev/null 2>&1; then
        print_pass "docker-compose is available"
    else
        print_fail "docker-compose is not installed"
    fi
}

# Function to test Dockerfile syntax
test_dockerfile_syntax() {
    run_test "Validating Dockerfile syntax"
    
    if docker build --dry-run -f Dockerfile .. >/dev/null 2>&1; then
        print_pass "Dockerfile syntax is valid"
    else
        print_fail "Dockerfile has syntax errors"
    fi
}

# Function to test docker-compose file syntax
test_compose_syntax() {
    run_test "Validating docker-compose.yml syntax"
    
    if docker-compose config >/dev/null 2>&1; then
        print_pass "docker-compose.yml syntax is valid"
    else
        print_fail "docker-compose.yml has syntax errors"
    fi
}

# Function to test environment files
test_env_files() {
    run_test "Checking environment files"
    
    if [ -f .env.example ]; then
        print_pass ".env.example exists"
    else
        print_fail ".env.example is missing"
    fi
}

# Function to test Docker build process
test_docker_build() {
    run_test "Testing Docker build"
    
    if docker build -t 6mlet-test -f Dockerfile .. >/dev/null 2>&1; then
        print_pass "Docker build successful"
        docker rmi 6mlet-test >/dev/null 2>&1 || true
    else
        print_fail "Docker build failed"
    fi
}

# Function to test required files in build context
test_build_context() {
    run_test "Checking required files in build context"
    
    local required_files=(
        "../requirements.txt"
        "../run.py"
        "../app"
        "../data"
    )
    
    for file in "${required_files[@]}"; do
        if [ -e "$file" ]; then
            print_pass "Required file/directory exists: $file"
        else
            print_fail "Required file/directory missing: $file"
        fi
    done
}

# Function to test dockerignore file
test_dockerignore() {
    run_test "Checking .dockerignore file"
    
    if [ -f .dockerignore ]; then
        print_pass ".dockerignore exists"
        
        # Check if it contains important exclusions
        if grep -q "__pycache__" .dockerignore; then
            print_pass ".dockerignore excludes __pycache__"
        else
            print_fail ".dockerignore should exclude __pycache__"
        fi
        
        if grep -q ".git" .dockerignore; then
            print_pass ".dockerignore excludes .git"
        else
            print_fail ".dockerignore should exclude .git"
        fi
    else
        print_fail ".dockerignore is missing"
    fi
}

# Function to test network and volume configuration
test_docker_compose_config() {
    run_test "Testing docker-compose configuration"
    
    # Check if volumes are defined
    if docker-compose config | grep -q "volumes:"; then
        print_pass "Docker volumes are configured"
    else
        print_fail "Docker volumes are not configured"
    fi
    
    # Check if networks are defined
    if docker-compose config | grep -q "networks:"; then
        print_pass "Docker networks are configured"
    else
        print_fail "Docker networks are not configured"
    fi
    
    # Check if health checks are defined
    if docker-compose config | grep -q "healthcheck:"; then
        print_pass "Health checks are configured"
    else
        print_fail "Health checks are not configured"
    fi
}

# Function to test port configuration
test_port_config() {
    run_test "Testing port configuration"
    
    # Check port mapping
    if docker-compose config | grep -q "8000:8000"; then
        print_pass "Port mapping is configured"
    else
        print_fail "Port mapping is incorrect"
    fi
}

# Function to test file permissions and security
test_security_config() {
    run_test "Testing security configuration"
    
    # Check if Dockerfile creates non-root user
    if grep -q "groupadd.*appuser" Dockerfile && grep -q "useradd.*appuser" Dockerfile; then
        print_pass "Non-root user is configured"
    else
        print_fail "Non-root user is not configured"
    fi
    
    # Check if USER directive is used
    if grep -q "USER appuser" Dockerfile; then
        print_pass "USER directive is used for security"
    else
        print_fail "USER directive is missing"
    fi
}

# Function to show test summary
show_summary() {
    echo ""
    echo "================================="
    echo "    Docker Setup Test Summary    "
    echo "================================="
    echo "Tests Run:    $TESTS_RUN"
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed! Docker setup is ready.${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Copy .env.example to .env and customize as needed"
        echo "2. Run './docker-manage.sh setup' to start Docker environment"
        echo "3. Test the API at http://localhost:8000/health"
    else
        echo -e "${RED}Some tests failed. Please fix the issues before proceeding.${NC}"
        exit 1
    fi
}

# Main function
main() {
    echo "======================================"
    echo "  Docker Setup Validation Test Suite  "
    echo "======================================"
    echo ""
    
    # Change to infra directory
    cd "$(dirname "$0")"
    
    # Run all tests
    test_docker_available
    test_compose_available
    test_dockerfile_syntax
    test_compose_syntax
    test_env_files
    test_dockerignore
    test_build_context
    test_docker_compose_config
    test_port_config
    test_security_config
    test_docker_build
    
    # Show summary
    show_summary
}

# Run main function
main "$@"
