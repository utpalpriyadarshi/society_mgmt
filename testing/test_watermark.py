#!/usr/bin/env python3
"""
Test script to generate a ledger report with enhanced watermark
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from models.reports import ReportGenerator

def test_watermark_report():
    """Generate a test ledger report with enhanced watermark"""
    try:
        report_generator = ReportGenerator()
        file_path = report_generator.generate_ledger_report(
            generated_by="Test User",
            file_name="test_ledger_watermark.pdf"
        )
        print(f"Ledger report with enhanced watermark generated successfully: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating report: {e}")
        return None

if __name__ == "__main__":
    test_watermark_report()