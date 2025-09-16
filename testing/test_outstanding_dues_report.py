"""
Test script for outstanding dues report
"""
import sys
import os
from datetime import date
from dateutil.relativedelta import relativedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.reports import ReportGenerator

def test_outstanding_dues_report():
    """Test that the outstanding dues report can be generated without errors"""
    try:
        report_generator = ReportGenerator()
        # Test with a date range
        end_date = date.today()
        start_date = end_date - relativedelta(months=12)
        
        file_path = report_generator.generate_outstanding_dues_report(
            "Test User",
            start_date=start_date,
            end_date=end_date
        )
        print(f"SUCCESS: Outstanding dues report generated successfully: {file_path}")
        return True
    except Exception as e:
        print(f"ERROR: Error generating outstanding dues report: {e}")
        return False

if __name__ == "__main__":
    print("Testing outstanding dues report generation...")
    success = test_outstanding_dues_report()
    if success:
        print("SUCCESS: All tests passed!")
        sys.exit(0)
    else:
        print("ERROR: Tests failed!")
        sys.exit(1)