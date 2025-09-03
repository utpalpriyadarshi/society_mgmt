# models/reports.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
import sqlite3
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from models.ledger import LedgerManager
from models.society import SocietyManager
from models.resident import ResidentManager

class ReportGenerator:
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
        self.ledger_manager = LedgerManager(db_path)
        self.society_manager = SocietyManager(db_path)
        self.resident_manager = ResidentManager(db_path)
        self.setup_report_directory()
    
    def setup_report_directory(self):
        """Create reports directory if it doesn't exist"""
        if not os.path.exists("reports"):
            os.makedirs("reports")
    
    def generate_ledger_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF ledger report with proper header and footer
        Optionally filter by date range
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"ledger_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,  # Reduced font size
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        normal_centered = ParagraphStyle(
            'NormalCentered',
            parent=styles['Normal'],
            alignment=1  # Center alignment
        )
        
        # Add report title
        story.append(Paragraph("LEDGER REPORT", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Add date range information if provided
        if start_date and end_date:
            date_range_text = f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            story.append(Paragraph(date_range_text, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Get ledger data
        if start_date and end_date:
            transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        else:
            transactions = self.ledger_manager.get_all_transactions()
        
        # Create table data
        table_data = [
            ['Txn ID', 'Date', 'Flat No', 'Type', 'Category', 'Description', 'Debit', 'Credit', 'Balance']
        ]
        
        total_debit = 0
        total_credit = 0
        
        for transaction in transactions:
            table_data.append([
                transaction.transaction_id,
                transaction.date,
                transaction.flat_no or '',
                transaction.transaction_type,
                transaction.category,
                transaction.description[:30] + "..." if len(transaction.description) > 30 else transaction.description,
                f"{transaction.debit:.2f}",
                f"{transaction.credit:.2f}",
                f"{transaction.balance:.2f}"
            ])
            total_debit += transaction.debit
            total_credit += transaction.credit
        
        # Add totals row
        table_data.append([
            '', '', '', '', '', 'TOTALS',
            f"{total_debit:.2f}",
            f"{total_credit:.2f}",
            ''
        ])
        
        # Create table with improved styling
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (5, -1), (-1, -1), 'Helvetica-Bold'),  # Bold for totals
            ('FONTNAME', (0, -1), (4, -1), 'Helvetica'),  # Normal for empty cells in totals row
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (6, 0), (8, -1), 'RIGHT'),  # Right align amount columns
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path
    
    
    
    def get_income_expense_data(self, start_date=None, end_date=None):
        """
        Get income and expense data for a given period
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Set default dates if not provided
        if not start_date:
            start_date = date.today() - relativedelta(months=12)
        if not end_date:
            end_date = date.today()
        
        # Get income (payments) by category
        cursor.execute('''
            SELECT category, SUM(credit) as total_income
            FROM ledger
            WHERE transaction_type = 'Payment'
            AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_income DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        income_data = cursor.fetchall()
        
        # Get expenses by category
        cursor.execute('''
            SELECT category, SUM(debit) as total_expense
            FROM ledger
            WHERE transaction_type = 'Expense'
            AND date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_expense DESC
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        expense_data = cursor.fetchall()
        
        conn.close()
        
        # Calculate totals
        total_income = sum(amount for _, amount in income_data)
        total_expense = sum(amount for _, amount in expense_data)
        net_amount = total_income - total_expense
        
        return {
            'income_data': income_data,
            'expense_data': expense_data,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': net_amount,
            'start_date': start_date,
            'end_date': end_date
        }

    def generate_income_expense_chart(self, income_expense_data):
        """
        Generate a bar chart for income vs expense and save as PNG
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create chart data
            categories = []
            income_values = []
            expense_values = []
            
            # Combine all categories from both income and expense
            all_categories = set()
            income_dict = dict(income_expense_data['income_data'])
            expense_dict = dict(income_expense_data['expense_data'])
            
            all_categories.update(income_dict.keys())
            all_categories.update(expense_dict.keys())
            
            # Sort categories by total value (income + expense)
            category_totals = {}
            for category in all_categories:
                total = income_dict.get(category, 0) + expense_dict.get(category, 0)
                category_totals[category] = total
            
            sorted_categories = sorted(category_totals.keys(), key=lambda x: category_totals[x], reverse=True)
            
            for category in sorted_categories:
                categories.append(category)
                income_values.append(income_dict.get(category, 0))
                expense_values.append(expense_dict.get(category, 0))
            
            # Create the chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x = np.arange(len(categories))
            width = 0.35
            
            rects1 = ax.bar(x - width/2, income_values, width, label='Income', color='green')
            rects2 = ax.bar(x + width/2, expense_values, width, label='Expense', color='red')
            
            # Add labels and title
            ax.set_xlabel('Categories')
            ax.set_ylabel('Amount (Rs)')
            ax.set_title('Income vs Expense by Category')
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            ax.legend()
            
            # Add value labels on bars
            def autolabel(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.0f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8)
            
            autolabel(rects1)
            autolabel(rects2)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join("reports", "income_expense_chart.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None

    def generate_income_expense_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF report of income vs expense with chart
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"income_expense_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Get income/expense data
        data = self.get_income_expense_data(start_date, end_date)
        
        # Generate chart
        chart_path = self.generate_income_expense_chart(data)
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add report title
        story.append(Paragraph("INCOME VS EXPENSE REPORT", title_style))
        
        # Add date range information
        date_range_text = f"Period: {data['start_date'].strftime('%Y-%m-%d')} to {data['end_date'].strftime('%Y-%m-%d')}"
        story.append(Paragraph(date_range_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add chart if generated
        if chart_path and os.path.exists(chart_path):
            try:
                chart_img = Image(chart_path, width=400, height=240)
                chart_img.hAlign = 'CENTER'
                story.append(chart_img)
                story.append(Spacer(1, 0.2*inch))
            except:
                pass  # If chart fails to load, continue without it
        
        # Create income table
        story.append(Paragraph("INCOME (Payments Received)", styles['Heading2']))
        income_table_data = [['Category', 'Amount (Rs)']]
        for category, amount in data['income_data']:
            income_table_data.append([category, f"{amount:.2f}"])
        income_table_data.append(['TOTAL INCOME', f"{data['total_income']:.2f}"])
        
        income_table = Table(income_table_data, repeatRows=1)
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        
        story.append(income_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Create expense table
        story.append(Paragraph("EXPENSES", styles['Heading2']))
        expense_table_data = [['Category', 'Amount (Rs)']]
        for category, amount in data['expense_data']:
            expense_table_data.append([category, f"{amount:.2f}"])
        expense_table_data.append(['TOTAL EXPENSES', f"{data['total_expense']:.2f}"])
        
        expense_table = Table(expense_table_data, repeatRows=1)
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        
        story.append(expense_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add net amount
        net_text = f"NET AMOUNT: Rs {data['net_amount']:.2f}"
        status_text = "Status: Surplus" if data['net_amount'] >= 0 else "Status: Deficit"
        story.append(Paragraph(net_text, styles['Normal']))
        story.append(Paragraph(status_text, styles['Normal']))
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        # Clean up chart file
        if chart_path and os.path.exists(chart_path):
            try:
                os.remove(chart_path)
            except:
                pass
        
        return file_path

    def add_header_footer(self, canvas, doc, society_info, generated_by):
        """
        Add header and footer to each page with watermark
        """
        canvas.saveState()
        
        # Add watermarks at three horizontal locations for better visibility
        canvas.setFont('Helvetica-Bold', 50)
        canvas.setFillColor(colors.gray)
        canvas.setFillAlpha(0.15)
        
        # Top watermark
        canvas.drawCentredString(A4[0]/2, A4[1] - 100, "NextGen Advisors")
        
        # Middle watermark
        canvas.drawCentredString(A4[0]/2, A4[1]/2, "NextGen Advisors")
        
        # Bottom watermark
        canvas.drawCentredString(A4[0]/2, 100, "NextGen Advisors")
        
        canvas.setFillAlpha(1.0)  # Reset alpha
        
        canvas.setFillAlpha(1.0)  # Reset alpha
        
        # Header
        canvas.setFont('Helvetica-Bold', 14)
        
        if society_info:
            # Society name in black
            canvas.setFillColor(colors.black)
            canvas.drawCentredString(A4[0]/2, A4[1] - 50, society_info.name or "Society Management System")
            
            # Society address and contact in black
            canvas.setFont('Helvetica', 10)
            address_text = society_info.address or ""
            phone_text = f"Phone: {society_info.phone or 'N/A'}"
            email_text = f"Email: {society_info.email or 'N/A'}"
            
            canvas.drawCentredString(A4[0]/2, A4[1] - 70, address_text)
            canvas.drawCentredString(A4[0]/2, A4[1] - 85, f"{phone_text} | {email_text}")
        else:
            # Default society info in black
            canvas.setFillColor(colors.black)
            canvas.drawCentredString(A4[0]/2, A4[1] - 50, "Society Management System")
            canvas.drawCentredString(A4[0]/2, A4[1] - 70, "123 Main Street, City, State 12345")
            canvas.drawCentredString(A4[0]/2, A4[1] - 85, "Phone: N/A | Email: N/A")
        
        # Footer with bold text and page number in center
        canvas.setFont('Helvetica-Bold', 8)
        generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        canvas.drawString(50, 30, f"Generated by: {generated_by}")
        canvas.drawCentredString(A4[0]/2, 30, f"Page {canvas.getPageNumber()}")
        canvas.drawRightString(A4[0] - 50, 30, f"Generated on: {generated_date}")
        
        canvas.restoreState()

    def get_outstanding_dues(self, start_date=None, end_date=None):
        """
        Calculate outstanding dues for all residents
        If start_date and end_date are not provided, calculate for the last 12 months
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # If no dates provided, use last 12 months
        if not start_date:
            end_date = date.today()
            start_date = end_date - relativedelta(months=12)
        if not end_date:
            end_date = date.today()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active residents
        cursor.execute('''
            SELECT flat_no, name, date_joining
            FROM residents
            WHERE status = 'Active'
        ''')
        
        residents = cursor.fetchall()
        outstanding_dues = []
        
        # Fixed monthly charges
        monthly_charges = 500.0
        
        for resident in residents:
            flat_no, name, date_joining_str = resident
            
            try:
                # Parse the date joining
                resident_joined = datetime.strptime(date_joining_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                # Skip residents with invalid joining dates
                continue
            
            # Calculate the actual period for which dues are applicable
            # Resident only owes dues from their joining date onwards
            period_start = max(resident_joined, start_date)
            period_end = end_date
            
            # If period start is after period end, resident didn't owe anything in this period
            if period_start > period_end:
                continue
            
            # Calculate number of months in the period
            months_due = (period_end.year - period_start.year) * 12 + (period_end.month - period_start.month) + 1
            
            # Total expected amount
            expected_amount = months_due * monthly_charges
            
            # Get all maintenance payments for this resident during the period
            cursor.execute('''
                SELECT SUM(credit) 
                FROM ledger 
                WHERE flat_no = ? 
                AND category = 'Maintenance' 
                AND transaction_type = 'Payment'
                AND date BETWEEN ? AND ?
            ''', (flat_no, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            payment_result = cursor.fetchone()
            amount_paid = payment_result[0] if payment_result[0] is not None else 0.0
            
            # Calculate outstanding amount
            amount_due = expected_amount - amount_paid
            
            # Only include if there's actually an outstanding amount
            if amount_due > 0:
                outstanding_dues.append({
                    'flat_no': flat_no,
                    'name': name,
                    'months_due': months_due,
                    'expected_amount': expected_amount,
                    'amount_paid': amount_paid,
                    'amount_due': amount_due
                })
        
        conn.close()
        # Sort by amount due descending
        outstanding_dues.sort(key=lambda x: x['amount_due'], reverse=True)
        return outstanding_dues

    def generate_outstanding_dues_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF report of residents with outstanding maintenance dues
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"outstanding_dues_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add report title
        story.append(Paragraph("OUTSTANDING DUES REPORT", title_style))
        
        # Add date range information
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        if not start_date:
            end_date_obj = date.today()
            start_date_obj = end_date_obj - relativedelta(months=12)
        else:
            start_date_obj = start_date
            end_date_obj = end_date if end_date else date.today()
        
        date_range_text = f"Period: {start_date_obj.strftime('%Y-%m-%d')} to {end_date_obj.strftime('%Y-%m-%d')}"
        story.append(Paragraph(date_range_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get outstanding dues data
        outstanding_dues_data = self.get_outstanding_dues(start_date_obj, end_date_obj)
        
        # Create table data
        table_data = [
            ['Flat No', 'Resident Name', 'Months', 'Expected (Rs)', 'Paid (Rs)', 'Due (Rs)']
        ]
        
        total_expected = 0
        total_paid = 0
        total_due = 0
        
        for data in outstanding_dues_data:
            table_data.append([
                data['flat_no'],
                data['name'],
                str(data['months_due']),
                f"{data['expected_amount']:.2f}",
                f"{data['amount_paid']:.2f}",
                f"{data['amount_due']:.2f}"
            ])
            total_expected += data['expected_amount']
            total_paid += data['amount_paid']
            total_due += data['amount_due']
        
        # Add totals row
        table_data.append([
            '', '', '', 
            f"{total_expected:.2f}",
            f"{total_paid:.2f}",
            f"{total_due:.2f}"
        ])
        
        # Create table with improved styling
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),  # Bold for totals
            ('FONTNAME', (0, -1), (2, -1), 'Helvetica'),  # Normal for empty cells in totals row
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (3, 0), (5, -1), 'RIGHT'),  # Right align amount columns
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path
    
    def generate_payments_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF report of payments received within a date range
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"payments_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add report title
        story.append(Paragraph("PAYMENTS REPORT", title_style))
        
        # Add date range information
        if start_date and end_date:
            date_range_text = f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            # Get all payments if no date range specified
            date_range_text = "All Payments"
        story.append(Paragraph(date_range_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get payment transactions
        if start_date and end_date:
            all_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        else:
            all_transactions = self.ledger_manager.get_all_transactions()
        
        # Filter only payment transactions
        payment_transactions = [txn for txn in all_transactions if txn.transaction_type == 'Payment']
        
        # Create table data
        table_data = [
            ['Txn ID', 'Date', 'Flat No', 'Category', 'Description', 'Amount (Rs)', 'Payment Mode']
        ]
        
        total_payments = 0
        
        for transaction in payment_transactions:
            table_data.append([
                transaction.transaction_id,
                transaction.date,
                transaction.flat_no or '',
                transaction.category,
                transaction.description[:30] + "..." if len(transaction.description) > 30 else transaction.description,
                f"{transaction.credit:.2f}",
                transaction.payment_mode
            ])
            total_payments += transaction.credit
        
        # Add totals row
        table_data.append([
            '', '', '', '', 'TOTAL', f"{total_payments:.2f}", ''
        ])
        
        # Create table with improved styling
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (4, -1), (5, -1), 'Helvetica-Bold'),  # Bold for totals
            ('FONTNAME', (0, -1), (3, -1), 'Helvetica'),  # Normal for empty cells in totals row
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (5, 0), (5, -1), 'RIGHT'),  # Right align amount column
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path
    
    def generate_expenses_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF report of expenses within a date range
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"expenses_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add report title
        story.append(Paragraph("EXPENSES REPORT", title_style))
        
        # Add date range information
        if start_date and end_date:
            date_range_text = f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            # Get all expenses if no date range specified
            date_range_text = "All Expenses"
        story.append(Paragraph(date_range_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get expense transactions
        if start_date and end_date:
            all_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        else:
            all_transactions = self.ledger_manager.get_all_transactions()
        
        # Filter only expense transactions
        expense_transactions = [txn for txn in all_transactions if txn.transaction_type == 'Expense']
        
        # Create table data
        table_data = [
            ['Txn ID', 'Date', 'Category', 'Description', 'Amount (Rs)', 'Payment Mode', 'Entered By']
        ]
        
        total_expenses = 0
        
        for transaction in expense_transactions:
            table_data.append([
                transaction.transaction_id,
                transaction.date,
                transaction.category,
                transaction.description[:30] + "..." if len(transaction.description) > 30 else transaction.description,
                f"{transaction.debit:.2f}",
                transaction.payment_mode,
                transaction.entered_by
            ])
            total_expenses += transaction.debit
        
        # Add totals row
        table_data.append([
            '', '', '', 'TOTAL', f"{total_expenses:.2f}", '', ''
        ])
        
        # Create table with improved styling
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (3, -1), (4, -1), 'Helvetica-Bold'),  # Bold for totals
            ('FONTNAME', (0, -1), (2, -1), 'Helvetica'),  # Normal for empty cells in totals row
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),  # Right align amount column
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path
    
    def generate_resident_list_report(self, generated_by, file_name=None):
        """
        Generate a PDF report of all residents
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"resident_list_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add report title
        story.append(Paragraph("RESIDENT LIST REPORT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Get resident data
        residents = self.resident_manager.get_all_residents()
        
        # Create table data
        table_data = [
            ['Flat No', 'Name', 'Type', 'Mobile', 'Email', 'Joining Date', 'Status']
        ]
        
        for resident in residents:
            table_data.append([
                resident.flat_no,
                resident.name,
                resident.resident_type,
                resident.mobile_no,
                resident.email,
                resident.date_joining,
                resident.status
            ])
        
        # Create table with improved styling
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path
    
    def generate_payment_summary_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF summary report of payments within a date range
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"payment_summary_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15
        )
        
        # Add report title
        story.append(Paragraph("PAYMENT SUMMARY REPORT", title_style))
        
        # Add date range information
        if start_date and end_date:
            date_range_text = f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            # Get all payments if no date range specified
            date_range_text = "All Payments"
        story.append(Paragraph(date_range_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get payment transactions
        if start_date and end_date:
            all_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        else:
            all_transactions = self.ledger_manager.get_all_transactions()
        
        # Filter only payment transactions
        payment_transactions = [txn for txn in all_transactions if txn.transaction_type == 'Payment']
        
        # Group payments by category
        category_totals = {}
        total_payments = 0
        
        for transaction in payment_transactions:
            category = transaction.category
            amount = transaction.credit
            
            if category not in category_totals:
                category_totals[category] = 0
            
            category_totals[category] += amount
            total_payments += amount
        
        # Add summary section
        story.append(Paragraph("Payment Summary by Category", heading_style))
        
        # Create summary table data
        summary_table_data = [
            ['Category', 'Total Amount (Rs)']
        ]
        
        # Add category rows
        for category, total in category_totals.items():
            summary_table_data.append([category, f"{total:.2f}"])
        
        # Add totals row
        summary_table_data.append(['TOTAL', f"{total_payments:.2f}"])
        
        # Create summary table with improved styling
        summary_table = Table(summary_table_data, repeatRows=1)
        summary_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right align amount column
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add detailed transactions section
        story.append(Paragraph("Detailed Payment Transactions", heading_style))
        
        # Create detailed transactions table data
        detailed_table_data = [
            ['Txn ID', 'Date', 'Flat No', 'Category', 'Description', 'Amount (Rs)', 'Payment Mode']
        ]
        
        # Sort transactions by date
        payment_transactions.sort(key=lambda x: x.date)
        
        # Add transaction rows
        for transaction in payment_transactions:
            detailed_table_data.append([
                transaction.transaction_id,
                transaction.date,
                transaction.flat_no or '',
                transaction.category,
                transaction.description[:30] + "..." if len(transaction.description) > 30 else transaction.description,
                f"{transaction.credit:.2f}",
                transaction.payment_mode
            ])
        
        # Add totals row
        detailed_table_data.append([
            '', '', '', '', 'TOTAL', f"{total_payments:.2f}", ''
        ])
        
        # Create detailed transactions table with improved styling
        detailed_table = Table(detailed_table_data, repeatRows=1)
        detailed_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (4, -1), (5, -1), 'Helvetica-Bold'),  # Bold for totals
            ('FONTNAME', (0, -1), (3, -1), 'Helvetica'),  # Normal for empty cells in totals row
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (5, 0), (5, -1), 'RIGHT'),  # Right align amount column
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(detailed_table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path
    
    def generate_expense_summary_report(self, generated_by, file_name=None, start_date=None, end_date=None):
        """
        Generate a PDF summary report of expenses within a date range
        """
        # Use default file name if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"expense_summary_report_{timestamp}.pdf"
        
        file_path = os.path.join("reports", file_name)
        
        # Get society info
        society_info = self.society_manager.get_society_info()
        
        # Create PDF document with custom page setup
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=A4,
            topMargin=100,
            bottomMargin=50,
            leftMargin=50,
            rightMargin=50
        )
        
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15
        )
        
        # Add report title
        story.append(Paragraph("EXPENSE SUMMARY REPORT", title_style))
        
        # Add date range information
        if start_date and end_date:
            date_range_text = f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            # Get all expenses if no date range specified
            date_range_text = "All Expenses"
        story.append(Paragraph(date_range_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get expense transactions
        if start_date and end_date:
            all_transactions = self.ledger_manager.get_transactions_by_date_range(start_date, end_date)
        else:
            all_transactions = self.ledger_manager.get_all_transactions()
        
        # Filter only expense transactions
        expense_transactions = [txn for txn in all_transactions if txn.transaction_type == 'Expense']
        
        # Group expenses by category
        category_totals = {}
        total_expenses = 0
        
        for transaction in expense_transactions:
            category = transaction.category
            amount = transaction.debit
            
            if category not in category_totals:
                category_totals[category] = 0
            
            category_totals[category] += amount
            total_expenses += amount
        
        # Add summary section
        story.append(Paragraph("Expense Summary by Category", heading_style))
        
        # Create summary table data
        summary_table_data = [
            ['Category', 'Total Amount (Rs)']
        ]
        
        # Add category rows
        for category, total in category_totals.items():
            summary_table_data.append([category, f"{total:.2f}"])
        
        # Add totals row
        summary_table_data.append(['TOTAL', f"{total_expenses:.2f}"])
        
        # Create summary table with improved styling
        summary_table = Table(summary_table_data, repeatRows=1)
        summary_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right align amount column
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add detailed transactions section
        story.append(Paragraph("Detailed Expense Transactions", heading_style))
        
        # Create detailed transactions table data
        detailed_table_data = [
            ['Txn ID', 'Date', 'Category', 'Description', 'Amount (Rs)', 'Payment Mode', 'Entered By']
        ]
        
        # Sort transactions by date
        expense_transactions.sort(key=lambda x: x.date)
        
        # Add transaction rows
        for transaction in expense_transactions:
            detailed_table_data.append([
                transaction.transaction_id,
                transaction.date,
                transaction.category,
                transaction.description[:30] + "..." if len(transaction.description) > 30 else transaction.description,
                f"{transaction.debit:.2f}",
                transaction.payment_mode,
                transaction.entered_by
            ])
        
        # Add totals row
        detailed_table_data.append([
            '', '', '', 'TOTAL', f"{total_expenses:.2f}", '', ''
        ])
        
        # Create detailed transactions table with improved styling
        detailed_table = Table(detailed_table_data, repeatRows=1)
        detailed_table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            
            # Totals row styling
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (3, -1), (4, -1), 'Helvetica-Bold'),  # Bold for totals
            ('FONTNAME', (0, -1), (2, -1), 'Helvetica'),  # Normal for empty cells in totals row
            
            # Grid styling
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),  # Right align amount column
            
            # Alternate row coloring for better readability
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.Color(0.9, 0.85, 0.8)]),
        ]))
        
        story.append(detailed_table)
        
        # Build PDF with custom header and footer
        doc.build(story, onFirstPage=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by), 
                  onLaterPages=lambda canvas, doc: self.add_header_footer(canvas, doc, society_info, generated_by))
        
        return file_path

def generate_ledger_pdf(generated_by):
    """
    Convenience function to generate ledger report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_ledger_report(generated_by)

def generate_outstanding_dues_pdf(generated_by, start_date=None, end_date=None):
    """
    Convenience function to generate outstanding dues report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_outstanding_dues_report(generated_by, start_date=start_date, end_date=end_date)

def generate_payments_pdf(generated_by, start_date=None, end_date=None):
    """
    Convenience function to generate payments report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_payments_report(generated_by, start_date=start_date, end_date=end_date)

def generate_expenses_pdf(generated_by, start_date=None, end_date=None):
    """
    Convenience function to generate expenses report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_expenses_report(generated_by, start_date=start_date, end_date=end_date)

def generate_resident_list_pdf(generated_by):
    """
    Convenience function to generate resident list report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_resident_list_report(generated_by)

def generate_payment_summary_pdf(generated_by, start_date=None, end_date=None):
    """
    Convenience function to generate payment summary report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_payment_summary_report(generated_by, start_date=start_date, end_date=end_date)

def generate_expense_summary_pdf(generated_by, start_date=None, end_date=None):
    """
    Convenience function to generate expense summary report
    """
    report_generator = ReportGenerator()
    return report_generator.generate_expense_summary_report(generated_by, start_date=start_date, end_date=end_date)