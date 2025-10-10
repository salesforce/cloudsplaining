#!/usr/bin/env python3
"""
Demo script to showcase the enhanced UI features for Cloudsplaining IAM Principals page.

This script demonstrates the new features:
1. Expand/Collapse all functionality
2. Sortable summary table
3. Filtering by risk type and principal type
4. Search functionality
"""

import os
import subprocess
import webbrowser
from pathlib import Path

def main():
    print("Cloudsplaining Enhanced UI Demo")
    print("=" * 50)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    print("Generating sample report with enhanced UI...")
    
    # Generate a report using the example data
    example_file = current_dir / "examples" / "files" / "example.json"
    output_dir = current_dir / "examples" / "output-demo"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Run the scan command
    cmd = [
        "python", "-m", "cloudsplaining.bin.cli", "scan",
        "--input-file", str(example_file),
        "--output", str(output_dir) + "/"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=current_dir)
        if result.returncode == 0:
            print("Report generated successfully!")
            
            # Find the generated HTML report
            html_report = output_dir / "iam-report-example.html"
            
            if html_report.exists():
                print(f"Report saved to: {html_report}")
                print("\nEnhanced UI Features:")
                print("  - Summary table with sorting capabilities")
                print("  - Filter by risk type (Data Exfiltration, Privilege Escalation, etc.)")
                print("  - Filter by principal type (Roles, Users, Groups)")
                print("  - Search by principal name or ARN")
                print("  - Expand/Collapse all controls")
                print("  - Risk indicators with color-coded badges")
                print("  - Pagination for large datasets")
                print("  - 'View Details' button to jump to specific principals")
                
                print(f"\nOpening report in browser...")
                webbrowser.open(f"file://{html_report.absolute()}")
                
                print("\nHow to test the new features:")
                print("1. Navigate to the 'Principals' tab in the report")
                print("2. Use the dropdown filters to filter by risk type or principal type")
                print("3. Try the search box to find specific principals")
                print("4. Click 'Expand All' or 'Collapse All' buttons")
                print("5. Sort the summary table by clicking column headers")
                print("6. Use 'View Details' buttons to jump to specific principals")
                
            else:
                print("HTML report not found!")
        else:
            print(f"Error generating report: {result.stderr}")
            
    except Exception as e:
        print(f"Error running demo: {e}")

if __name__ == "__main__":
    main()