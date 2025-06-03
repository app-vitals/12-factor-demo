#!/usr/bin/env python3
"""
Analyze existing Factor 3 test results with different model combinations
Usage: python analyze_results.py <results_file.json>
"""

import sys
import json
from factor3_test import load_and_analyze_results

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_results.py <results_file.json>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        load_and_analyze_results(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filename}'")
        sys.exit(1)

if __name__ == "__main__":
    main()