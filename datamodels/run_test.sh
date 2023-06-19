#!/bin/bash

# Initialize counters
success_count=0
failure_count=0

# Function to run a test and update counters
run_test() {
    local test_name=$1
    local command=$2

    echo "Running test: $test_name"
    eval "$command"
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "Test $test_name passed!"
        ((success_count++))
    else
        echo "Test $test_name failed with exit code $exit_code"
        ((failure_count++))
    fi
    echo
}
