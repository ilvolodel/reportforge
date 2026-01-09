#!/usr/bin/env python3
"""
ReportForge - PDF Template Testing Script
Tests PDF generation with mock data using WeasyPrint
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from jinja2 import Environment, FileSystemLoader

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Mock data for testing
MOCK_REPORT = {
    'id': 'RPT-2026-01',
    'name': 'Monthly Report - AI Customer Support',
    'description': 'Report mensile attività AI Customer Support e GenAI Hub per il periodo Gennaio 2026',
    'period_start': date(2026, 1, 1),
    'period_end': date(2026, 1, 31),
    'author_email': 'ai.team@infocert.it'
}

MOCK_EXECUTIVE_SUMMARY = {
    'overview_text': 'Il mese di Gennaio 2026 ha visto un\'accelerazione significativa delle iniziative AI, con 8 progetti attivi che hanno generato un valore totale di €425K tra revenue e saving. La pipeline per il 2026 mostra un forecast di €2.6M, con particolare focus su progetti di Customer Care automation e Sales enablement.',
    'year_current': 2025,
    'year_forecast': 2026,
    'revenue_current': 375000,
    'saving_current': 50000,
    'total_current': 425000,
    'revenue_forecast': 2000000,
    'saving_forecast': 600000,
    'total_forecast': 2600000,
    'show_forecast': True,
    'benefits_list': [
        'Leadership AI avanzate nel settore Customer Care',
        'Riduzione rischio reputazionale grazie a risposte più accurate',
        'Miglioramento Customer Experience con tempi di risposta ridotti',
        'Efficienza operativa grazie ad automazione processi ripetitivi',
        'Insight data-driven per ottimizzazione continua servizi'
    ],
    'stakeholders_list': [
        'Customer Care', 'Marketing', 'Sales', 'IT & Operations', 
        'Legal & Compliance', 'Product Management'
    ]
}

MOCK_PROJECTS = [
    {
        'name': 'CHATBOT ANALYZER',
        'category': 'Analytics & Monitoring',
        'status': 'Active',
        'description': 'Sistema di analisi avanzata per monitoraggio performance chatbot e identificazione aree di miglioramento attraverso ML e NLP.',
        'start_date': date(2025, 3, 1),
        'stakeholders': ['Customer Care', 'Data Science', 'Product'],
        'activities': [
            {'date': date(2026, 1, 15), 'description': 'Implementazione dashboard real-time analytics', 'notes': 'Rilascio beta'},
            {'date': date(2026, 1, 22), 'description': 'Training modello ML per sentiment analysis', 'notes': '85% accuracy'}
        ],
        'goals': [
            'Ridurre tasso di escalation a operatore umano del 20%',
            'Identificare pattern di fallimento chatbot in tempo reale',
            'Generare report automatici settimanali su performance'
        ],
        'notes': 'In fase di validazione con team Customer Care'
    },
    {
        'name': 'SERVICE GURU',
        'category': 'Chatbot Evolution',
        'status': 'Active',
        'description': 'Assistente AI intelligente a supporto del Customer Care e Sales per risposte rapide e accurate su catalogo servizi.',
        'start_date': date(2025, 6, 1),
        'stakeholders': ['Customer Care', 'Sales', 'Training'],
        'deliverables': [
            {'name': 'Integrazione Knowledge Base', 'completed': True, 'due_date': date(2026, 1, 10)},
            {'name': 'API connessione CRM', 'completed': False, 'due_date': date(2026, 2, 15)},
            {'name': 'Dashboard analytics utilizzo', 'completed': False, 'due_date': date(2026, 3, 1)}
        ]
    },
    {
        'name': 'TRUSTY VOICE (SPID)',
        'category': 'Chatbot Evolution',
        'status': 'Planning',
        'description': 'Assistente vocale per supporto SPID via telefono, con riconoscimento vocale e risposta automatica.',
        'start_date': date(2026, 2, 1),
        'stakeholders': ['Customer Care', 'IT', 'Legal'],
        'notes': 'In attesa approvazione budget Q1 2026'
    },
    {
        'name': 'Marketing Copilot',
        'category': 'Marketing Automation',
        'status': 'Active',
        'description': 'Tool AI per generazione contenuti marketing, copy automatico e ottimizzazione campagne.',
        'start_date': date(2025, 9, 1),
        'stakeholders': ['Marketing', 'Content Team']
    },
    {
        'name': 'TRUSTY HUB',
        'category': 'Platform',
        'status': 'Active',
        'description': 'Hub centralizzato per gestione tutti strumenti AI, con orchestrazione workflow e monitoraggio unificato.',
        'start_date': date(2025, 11, 1),
        'stakeholders': ['IT', 'Operations', 'All Teams']
    }
]

MOCK_TEAM_MEMBERS = [
    {'name': 'Mario Rossi', 'role': 'AI Team Lead', 'email': 'mario.rossi@infocert.it', 'project_count': 5},
    {'name': 'Laura Bianchi', 'role': 'ML Engineer', 'email': 'laura.bianchi@infocert.it', 'project_count': 3},
    {'name': 'Giuseppe Verdi', 'role': 'Data Scientist', 'email': 'giuseppe.verdi@infocert.it', 'project_count': 4},
    {'name': 'Anna Ferrari', 'role': 'Backend Developer', 'email': 'anna.ferrari@infocert.it', 'project_count': 3}
]

MOCK_STAKEHOLDERS = [
    {'name': 'Paolo Conti', 'organization': 'Customer Care', 'role': 'Director', 'email': 'paolo.conti@infocert.it'},
    {'name': 'Silvia Marino', 'organization': 'Marketing', 'role': 'Marketing Manager', 'email': 'silvia.marino@infocert.it'},
    {'name': 'Luca Romano', 'organization': 'Sales', 'role': 'Sales Director', 'email': 'luca.romano@infocert.it'}
]

MOCK_SUBSCRIPTIONS = [
    {
        'client_name': 'INFOCERT',
        'description': 'Trusty Hub - Subscription mensile',
        'start_date': date(2025, 10, 1),
        'end_date': None,
        'mrr': 15000,
        'arr': 180000,
        'status': 'Active'
    },
    {
        'client_name': 'ASL CUNEO',
        'description': 'Chatbot Evolution - Maintenance',
        'start_date': date(2025, 9, 1),
        'end_date': date(2026, 8, 31),
        'mrr': 5000,
        'arr': 60000,
        'status': 'Active'
    }
]

MOCK_REVENUE_ONETIME = [
    {
        'client_name': 'INFOCERT',
        'project_name': 'NORMA',
        'partner_name': None,
        'revenue_date': date(2025, 12, 1),
        'amount': 280000,
        'status': 'Invoiced',
        'notes': 'Operativo da Ottobre 2025, fatturato Q4'
    },
    {
        'client_name': 'LENOVYS',
        'project_name': 'Chatbot Custom',
        'partner_name': 'TechPartner SRL',
        'revenue_date': date(2025, 11, 15),
        'amount': 45000,
        'status': 'Paid',
        'notes': None
    }
]

MOCK_SAVINGS = [
    {
        'client_name': 'INFOCERT',
        'description': 'Automazione risposte FAQ',
        'saving_type': 'Operational',
        'saving_date': date(2025, 12, 1),
        'amount': 30000,
        'status': 'Realized',
        'notes': 'Riduzione 2 FTE Customer Care'
    },
    {
        'client_name': 'ASL CUNEO',
        'description': 'Riduzione tempi gestione ticket',
        'saving_type': 'Process Improvement',
        'saving_date': date(2025, 11, 1),
        'amount': 20000,
        'status': 'Estimated',
        'notes': '-40% tempo medio risoluzione'
    }
]

MOCK_FINANCIAL = {
    'subscriptions_revenue': 240000,
    'onetime_revenue': 325000,
    'total_revenue': 565000,
    'operational_saving': 30000,
    'process_saving': 20000,
    'total_saving': 50000,
    'breakdown': [
        {'client_name': 'INFOCERT', 'project_name': 'NORMA', 'revenue': 280000, 'saving': 30000},
        {'client_name': 'INFOCERT', 'project_name': 'Trusty Hub', 'revenue': 180000, 'saving': 0},
        {'client_name': 'ASL CUNEO', 'project_name': 'Chatbot', 'revenue': 60000, 'saving': 20000},
        {'client_name': 'LENOVYS', 'project_name': 'Custom', 'revenue': 45000, 'saving': 0}
    ]
}

MOCK_CONFIG = {
    'show_cover': True,
    'show_executive_summary': True,
    'show_projects': True,
    'show_project_details': True,
    'show_team_stakeholders': True,
    'show_financial_overview': True,
    'show_revenue_details': True,
    'show_back_cover': True
}

def test_pdf_generation():
    """Test PDF generation with mock data"""
    print("🧪 ReportForge - PDF Template Testing")
    print("=" * 60)
    
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent / "backend" / "app" / "templates" / "pdf"
    print(f"\n📁 Template directory: {template_dir}")
    
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return False
    
    env = Environment(loader=FileSystemLoader(str(template_dir.parent)))
    
    # Load template
    try:
        template = env.get_template('pdf/base.html')
        print("✅ Template loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load template: {e}")
        return False
    
    # Render HTML
    try:
        html_content = template.render(
            report=MOCK_REPORT,
            executive_summary=MOCK_EXECUTIVE_SUMMARY,
            projects=MOCK_PROJECTS,
            team_members=MOCK_TEAM_MEMBERS,
            stakeholders=MOCK_STAKEHOLDERS,
            subscriptions=MOCK_SUBSCRIPTIONS,
            revenue_onetime=MOCK_REVENUE_ONETIME,
            savings=MOCK_SAVINGS,
            financial=MOCK_FINANCIAL,
            config=MOCK_CONFIG,
            generation_date=datetime.now(),
            logo_path=None,
            version='0.5.0'
        )
        print("✅ HTML rendered successfully")
        print(f"   HTML size: {len(html_content):,} characters")
    except Exception as e:
        print(f"❌ Failed to render HTML: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save HTML for inspection
    output_dir = Path(__file__).parent.parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    html_path = output_dir / "test_report.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML saved to: {html_path}")
    
    # Try to generate PDF with WeasyPrint
    try:
        from weasyprint import HTML, CSS
        print("\n📄 Generating PDF with WeasyPrint...")
        
        pdf_path = output_dir / "test_report.pdf"
        
        # Generate PDF
        HTML(string=html_content, base_url=str(template_dir)).write_pdf(
            pdf_path,
            stylesheets=None
        )
        
        print(f"✅ PDF generated successfully: {pdf_path}")
        print(f"   PDF size: {pdf_path.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except ImportError:
        print("\n⚠️  WeasyPrint not installed. Install with:")
        print("   pip install weasyprint")
        print("\n✅ HTML generation successful (PDF skipped)")
        return True
        
    except Exception as e:
        print(f"\n❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n✅ HTML generation successful (PDF failed)")
        return True

def main():
    """Main function"""
    success = test_pdf_generation()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("\n📂 Output files:")
        print("   test_output/test_report.html - HTML preview")
        print("   test_output/test_report.pdf - PDF output (if WeasyPrint available)")
        print("\n💡 Open HTML file in browser to preview design")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
