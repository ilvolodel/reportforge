#!/usr/bin/env python3
"""
Test script for PDF API integration
Tests the PDF generation with mock database data
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.pdf_service import PDFGenerationService
from datetime import datetime, date


class MockDB:
    """Mock database session for testing"""
    
    class MockQuery:
        def __init__(self, results):
            self.results = results
        
        def filter(self, *args):
            return self
        
        def first(self):
            return self.results[0] if self.results else None
        
        def all(self):
            return self.results
    
    def __init__(self):
        self.data = {}
    
    def query(self, model):
        model_name = model.__name__
        return MockDB.MockQuery(self.data.get(model_name, []))


class MockReport:
    def __init__(self):
        self.id = 1
        self.name = "Monthly Report - January 2026"
        self.description = "Test report for AI Customer Support activities"
        self.period_start = date(2026, 1, 1)
        self.period_end = date(2026, 1, 31)
        self.template_id = None
        self.executive_summary = None


class MockProject:
    def __init__(self, name, status):
        self.id = 1
        self.name = name
        self.status = status
        self.description = "Test project description"
        self.start_date = date(2025, 10, 1)
        self.clients = []
        self.activities = []
        self.costs = []
        self.stakeholders = []


class MockSnapshot:
    def __init__(self, name, status):
        self.id = 1
        self.report_id = 1
        self.project_id = 1
        self.snapshot_data = {
            'name': name,
            'status': status,
            'description': 'Test project for chatbot analytics',
            'category': 'Analytics & Monitoring',
            'start_date': date(2025, 3, 1),
            'stakeholders': ['Customer Care', 'Data Science'],
            'goals': [
                'Reduce escalation rate by 20%',
                'Real-time failure pattern identification'
            ]
        }


class MockSubscription:
    def __init__(self):
        self.name = "Trusty Hub Subscription"
        self.description = "Monthly subscription for AI platform"
        self.start_date = date(2025, 10, 1)
        self.end_date = None
        self.monthly_amount = 15000
        self.status = "Active"


class MockRevenue:
    def __init__(self):
        self.id = 1
        self.project_id = 1
        self.amount = 280000
        self.invoice_date = date(2025, 12, 1)
        self.payment_date = None
        self.status = "Invoiced"
        self.description = "NORMA project implementation"


class MockTeamMember:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.email = f"{name.lower().replace(' ', '.')}@infocert.it"
        self.projects = []


class MockStakeholder:
    def __init__(self, name, org, role):
        self.name = name
        self.organization = org
        self.role = role
        self.email = f"{name.lower().replace(' ', '.')}@infocert.it"


def test_pdf_service():
    """Test PDF service with mock data"""
    print("🧪 Testing PDF API Integration")
    print("=" * 60)
    
    # Setup mock database
    db = MockDB()
    
    # Add mock report
    from app.models.report import Report
    db.data['Report'] = [MockReport()]
    
    # Add mock snapshots
    from app.models.report import ReportProjectSnapshot, ReportTemplate
    db.data['ReportProjectSnapshot'] = [
        MockSnapshot('CHATBOT ANALYZER', 'Active'),
        MockSnapshot('SERVICE GURU', 'Active')
    ]
    db.data['ReportTemplate'] = []
    
    # Add mock projects
    from app.models.project import Project, Client, TeamMember, Stakeholder
    db.data['Project'] = [MockProject('CHATBOT ANALYZER', 'Active')]
    
    # Add mock subscriptions
    from app.models.subscription import Subscription, RevenueOneTime
    db.data['Subscription'] = [MockSubscription()]
    db.data['RevenueOneTime'] = [MockRevenue()]
    
    # Add mock team and stakeholders
    db.data['TeamMember'] = [
        MockTeamMember('Mario Rossi', 'AI Team Lead'),
        MockTeamMember('Laura Bianchi', 'ML Engineer')
    ]
    db.data['Stakeholder'] = [
        MockStakeholder('Paolo Conti', 'Customer Care', 'Director'),
        MockStakeholder('Silvia Marino', 'Marketing', 'Manager')
    ]
    
    # Test PDF service
    try:
        print("\n📋 Step 1: Initialize PDF service")
        pdf_service = PDFGenerationService()
        print("✅ PDF service initialized")
        
        print("\n📋 Step 2: Fetch report data")
        data = pdf_service.fetch_report_data(db, 1)
        print("✅ Data fetched successfully")
        print(f"   - Report: {data['report']['name']}")
        print(f"   - Projects: {len(data['projects'])}")
        print(f"   - Team members: {len(data['team_members'])}")
        print(f"   - Subscriptions: {len(data['subscriptions'])}")
        print(f"   - Revenue items: {len(data['revenue_onetime'])}")
        
        print("\n📋 Step 3: Generate HTML preview")
        html_content = pdf_service.generate_html_preview(db, 1)
        print("✅ HTML generated successfully")
        print(f"   HTML size: {len(html_content):,} characters")
        
        # Save HTML for inspection
        output_dir = Path(__file__).parent.parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        
        html_path = output_dir / "test_api_integration.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   Saved to: {html_path}")
        
        print("\n📋 Step 4: Generate PDF")
        pdf_path = pdf_service.generate_pdf(db, 1)
        print(f"✅ PDF generated: {pdf_path}")
        print(f"   PDF size: {pdf_path.stat().st_size / 1024:.1f} KB")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("\n📂 Output files:")
        print(f"   {html_path}")
        print(f"   {pdf_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_service()
    sys.exit(0 if success else 1)
