"""
PDF Generation Service for ReportForge

Fetches report data from database and generates PDF using WeasyPrint + Jinja2 templates
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.models.report import Report, ReportProjectSnapshot, ReportTemplate
from app.models.project import Project, Client, TeamMember, Stakeholder
from app.models.subscription import Subscription, RevenueOneTime

logger = logging.getLogger(__name__)


class PDFGenerationService:
    """Service for generating PDF reports from database data"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize PDF generation service
        
        Args:
            template_dir: Path to templates directory (defaults to app/templates)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"
        
        self.template_dir = template_dir
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        logger.info(f"PDFGenerationService initialized with template_dir: {template_dir}")
    
    def fetch_report_data(self, db: Session, report_id: int) -> Dict[str, Any]:
        """
        Fetch all data needed for report generation from database
        
        Args:
            db: Database session
            report_id: Report ID
            
        Returns:
            Dictionary with all report data formatted for templates
            
        Raises:
            ValueError: If report not found
        """
        # Get report
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report with id {report_id} not found")
        
        logger.info(f"Fetching data for report {report_id}: {report.name}")
        
        # Get report template config from report itself or use defaults
        config = report.template_config if report.template_config else {}
        
        # Default config if none provided
        if not config:
            config = {
                'show_cover': True,
                'show_executive_summary': True,
                'show_projects': True,
                'show_project_details': True,
                'show_team_stakeholders': True,
                'show_financial_overview': True,
                'show_revenue_details': True,
                'show_back_cover': True
            }
        
        # Get project snapshots
        snapshots = db.query(ReportProjectSnapshot).filter(
            ReportProjectSnapshot.report_id == report_id
        ).all()
        
        projects = []
        for snapshot in snapshots:
            # Build project data from snapshot fields
            project_data = {
                'name': snapshot.name,
                'status': snapshot.status,
                'category': snapshot.project_type,
                'description': snapshot.description,
                'start_date': snapshot.start_date,
                'end_date': snapshot.end_date,
                'financial_data': snapshot.financial_data or {},
                'team_data': snapshot.team_data or [],
                'stakeholder_data': snapshot.stakeholder_data or [],
                'client_data': snapshot.client_data or [],
                'activities': snapshot.activities_data or [],
                'deliverables': [],
                'goals': [],
                'stakeholders': [s.get('organization', s.get('name', '')) for s in (snapshot.stakeholder_data or [])]
            }
            
            # Get custom fields if available
            if snapshot.custom_fields:
                project_data.update(snapshot.custom_fields)
            
            projects.append(project_data)
        
        # Get subscriptions
        subscriptions = []
        if config.get('show_revenue_details', True):
            subs = db.query(Subscription).all()
            for sub in subs:
                # Get project for client name
                project = None
                client_name = 'Unknown'
                if sub.project_id:
                    project = db.query(Project).filter(Project.id == sub.project_id).first()
                    if project:
                        client_name = project.name
                        if hasattr(project, 'clients') and project.clients:
                            client_name = project.clients[0].name
                
                subscriptions.append({
                    'client_name': client_name,
                    'description': sub.description or '',
                    'start_date': sub.start_date,
                    'end_date': sub.end_date,
                    'mrr': float(sub.annual_value / 12) if sub.annual_value else 0,
                    'arr': float(sub.annual_value) if sub.annual_value else 0,
                    'status': 'Active' if not sub.end_date else 'Ended'
                })
        
        # Get one-time revenue
        revenue_onetime = []
        if config.get('show_revenue_details', True):
            revenues = db.query(RevenueOneTime).all()
            for rev in revenues:
                # Get project for client name
                project = None
                client_name = 'Unknown'
                project_name = 'Unknown'
                if rev.project_id:
                    project = db.query(Project).filter(Project.id == rev.project_id).first()
                    if project:
                        project_name = project.name
                        if hasattr(project, 'clients') and project.clients:
                            client_name = project.clients[0].name
                
                revenue_onetime.append({
                    'client_name': client_name,
                    'project_name': project_name,
                    'partner_name': None,
                    'revenue_date': rev.date,
                    'amount': float(rev.amount) if rev.amount else 0,
                    'status': 'Forecast' if rev.is_forecast else 'Actual',
                    'notes': rev.description
                })
        
        # Calculate financial summary
        total_subscriptions = sum(s['arr'] for s in subscriptions)
        total_revenue_onetime = sum(r['amount'] for r in revenue_onetime)
        
        # Get team members (from report metadata or all active)
        team_members = []
        if config.get('show_team_stakeholders', True):
            members = db.query(TeamMember).all()
            for member in members[:10]:  # Limit to top 10
                # Count projects
                project_count = 0
                if hasattr(member, 'projects'):
                    project_count = len(member.projects)
                
                team_members.append({
                    'name': member.name,
                    'role': member.role,
                    'email': member.email,
                    'project_count': project_count
                })
        
        # Get stakeholders
        stakeholders_list = []
        if config.get('show_team_stakeholders', True):
            stakeholders_db = db.query(Stakeholder).all()
            for sh in stakeholders_db[:10]:  # Limit to top 10
                stakeholders_list.append({
                    'name': sh.name,
                    'organization': sh.organization,
                    'role': sh.role,
                    'email': sh.email
                })
        
        # Executive summary from report metadata or calculate
        executive_summary = report.executive_summary or {}
        if not executive_summary:
            executive_summary = {
                'overview_text': report.description or '',
                'year_current': report.period_start.year if report.period_start else datetime.now().year,
                'year_forecast': (report.period_start.year + 1) if report.period_start else datetime.now().year + 1,
                'revenue_current': total_subscriptions + total_revenue_onetime,
                'saving_current': 0,
                'total_current': total_subscriptions + total_revenue_onetime,
                'show_forecast': False
            }
        
        # Financial overview
        financial = {
            'subscriptions_revenue': total_subscriptions,
            'onetime_revenue': total_revenue_onetime,
            'total_revenue': total_subscriptions + total_revenue_onetime,
            'operational_saving': 0,
            'process_saving': 0,
            'total_saving': 0,
            'breakdown': []
        }
        
        # Build data structure for template
        data = {
            'report': {
                'id': report.id,
                'name': report.name,
                'description': report.description,
                'period_start': report.period_start,
                'period_end': report.period_end,
                'author_email': report.created_by if hasattr(report, 'created_by') else None
            },
            'config': config,
            'executive_summary': executive_summary,
            'projects': projects,
            'team_members': team_members,
            'stakeholders': stakeholders_list,
            'subscriptions': subscriptions,
            'revenue_onetime': revenue_onetime,
            'savings': [],  # TODO: Add savings data when model exists
            'financial': financial,
            'generation_date': datetime.now(),
            'logo_path': None,  # TODO: Add logo handling
            'version': '0.5.0'
        }
        
        return data
    
    def generate_pdf(
        self,
        db: Session,
        report_id: int,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate PDF report from database data
        
        Args:
            db: Database session
            report_id: Report ID
            output_path: Optional custom output path
            
        Returns:
            Path to generated PDF file
            
        Raises:
            ValueError: If report not found or generation fails
        """
        logger.info(f"Starting PDF generation for report {report_id}")
        
        # Fetch data
        data = self.fetch_report_data(db, report_id)
        
        # Generate output path if not provided
        if output_path is None:
            reports_dir = Path(__file__).parent.parent.parent / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{report_id}_{timestamp}.pdf"
            output_path = reports_dir / filename
        
        # Render HTML template
        try:
            template = self.jinja_env.get_template('pdf/base.html')
            html_content = template.render(**data)
            logger.info("HTML template rendered successfully")
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            raise ValueError(f"Template rendering failed: {e}")
        
        # Generate PDF with WeasyPrint
        try:
            html = HTML(string=html_content, base_url=str(self.template_dir))
            html.write_pdf(output_path)
            logger.info(f"PDF generated successfully: {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise ValueError(f"PDF generation failed: {e}")
        
        return output_path
    
    def generate_html_preview(
        self,
        db: Session,
        report_id: int
    ) -> str:
        """
        Generate HTML preview of report (without PDF conversion)
        
        Args:
            db: Database session
            report_id: Report ID
            
        Returns:
            HTML string
        """
        logger.info(f"Generating HTML preview for report {report_id}")
        
        data = self.fetch_report_data(db, report_id)
        template = self.jinja_env.get_template('pdf/base.html')
        html_content = template.render(**data)
        
        return html_content
