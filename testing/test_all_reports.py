"""
Script to test all report types
"""
import sys
import os
from datetime import date
from dateutil.relativedelta import relativedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.reports import ReportGenerator

def test_all_reports():
    """Test all report types"""
    print("Testing all report types...")
    
    try:
        report_generator = ReportGenerator()
        
        # Test dates
        end_date = date.today()
        start_date = end_date - relativedelta(months=12)
        
        # 1. Test Ledger Report
        print("\n1. Testing Ledger Report...")
        ledger_path = report_generator.generate_ledger_report("System Admin")
        print(f"   SUCCESS: Ledger report generated: {ledger_path}")
        
        # 2. Test Outstanding Dues Report
        print("\n2. Testing Outstanding Dues Report...")
        outstanding_path = report_generator.generate_outstanding_dues_report(
            "System Admin", 
            start_date=start_date, 
            end_date=end_date
        )
        print(f"   SUCCESS: Outstanding dues report generated: {outstanding_path}")
        
        # 3. Test Income vs Expense Report
        print("\n3. Testing Income vs Expense Report...")
        income_expense_path = report_generator.generate_income_expense_report(
            "System Admin",
            start_date=start_date,
            end_date=end_date
        )
        print(f"   SUCCESS: Income vs expense report generated: {income_expense_path}")
        
        print("\nSUCCESS: All reports generated successfully!")
        print(f"\nGenerated reports:")
        print(f"  - Ledger Report: {ledger_path}")
        print(f"  - Outstanding Dues Report: {outstanding_path}")
        print(f"  - Income vs Expense Report: {income_expense_path}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing reports: {e}")
        return False

if __name__ == "__main__":
    success = test_all_reports()
    if success:
        print("\nSUCCESS: All tests passed!")
        sys.exit(0)
    else:
        print("\nERROR: Tests failed!")
        sys.exit(1)