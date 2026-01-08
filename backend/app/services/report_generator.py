"""
Report Generator Service - Modular architecture for multiple output formats

This service provides a flexible architecture that supports:
1. PDF generation (primary, using WeasyPrint)
2. PPTX generation (future, using python-pptx)
3. Easy addition of new formats

Design Pattern: Strategy Pattern for different export formats
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportExporter(ABC):
    """Abstract base class for report exporters"""
    
    @abstractmethod
    def export(self, report_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Export report to specific format
        
        Args:
            report_data: Dictionary containing all report data
            output_path: Path where to save the output file
            
        Returns:
            Path to the generated file
        """
        pass
    
    @abstractmethod
    def get_format(self) -> str:
        """Return the format name (e.g., 'pdf', 'pptx')"""
        pass
    
    @abstractmethod
    def get_mime_type(self) -> str:
        """Return the MIME type for HTTP responses"""
        pass


class PDFExporter(ReportExporter):
    """PDF export using WeasyPrint + Jinja2 templates"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        logger.info(f"PDFExporter initialized with template_dir: {template_dir}")
    
    def export(self, report_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate PDF report using WeasyPrint
        
        Template structure:
        - templates/pdf/base.html (main layout)
        - templates/pdf/sections/cover.html
        - templates/pdf/sections/executive_summary.html
        - templates/pdf/sections/projects.html
        - templates/pdf/sections/sales.html
        - templates/pdf/styles/infocert.css
        """
        from jinja2 import Environment, FileSystemLoader
        from weasyprint import HTML, CSS
        
        logger.info(f"Generating PDF report: {output_path}")
        
        # Setup Jinja2 environment
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template('pdf/report.html')
        
        # Render HTML with data
        html_content = template.render(**report_data)
        
        # Generate PDF
        css_path = self.template_dir / 'pdf' / 'styles' / 'infocert.css'
        html = HTML(string=html_content)
        
        if css_path.exists():
            css = CSS(filename=str(css_path))
            html.write_pdf(output_path, stylesheets=[css])
        else:
            html.write_pdf(output_path)
        
        logger.info(f"PDF generated successfully: {output_path}")
        return output_path
    
    def get_format(self) -> str:
        return "pdf"
    
    def get_mime_type(self) -> str:
        return "application/pdf"


class PPTXExporter(ReportExporter):
    """PPTX export using python-pptx (future implementation)"""
    
    def __init__(self, template_path: Optional[Path] = None):
        self.template_path = template_path
        logger.info(f"PPTXExporter initialized with template: {template_path}")
    
    def export(self, report_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate PPTX report using python-pptx
        
        Future implementation will:
        1. Load template PPTX if provided
        2. Create presentation from scratch otherwise
        3. Populate slides with report_data
        4. Save to output_path
        """
        from pptx import Presentation
        
        logger.info(f"Generating PPTX report: {output_path}")
        
        # TODO: Implement PPTX generation
        # This is a placeholder for future implementation
        
        if self.template_path and self.template_path.exists():
            # Load template and modify
            prs = Presentation(str(self.template_path))
            logger.info(f"Loaded template: {self.template_path}")
        else:
            # Create from scratch
            prs = Presentation()
            logger.info("Creating PPTX from scratch")
        
        # TODO: Add slides and populate with data
        # - Cover slide
        # - Executive summary
        # - Projects
        # - Sales details
        
        prs.save(str(output_path))
        logger.info(f"PPTX generated successfully: {output_path}")
        
        return output_path
    
    def get_format(self) -> str:
        return "pptx"
    
    def get_mime_type(self) -> str:
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"


class ReportGenerator:
    """
    Main report generator service
    
    Supports multiple export formats through Strategy Pattern.
    Easy to add new formats by creating new ReportExporter subclasses.
    """
    
    def __init__(self, template_dir: Path, output_dir: Path):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Register available exporters
        self.exporters: Dict[str, ReportExporter] = {
            'pdf': PDFExporter(template_dir),
            # PPTX exporter ready but not active yet
            # 'pptx': PPTXExporter(template_dir / 'template.pptx')
        }
        
        logger.info(f"ReportGenerator initialized with formats: {list(self.exporters.keys())}")
    
    def generate(
        self,
        report_id: int,
        report_data: Dict[str, Any],
        format: str = 'pdf',
        filename: Optional[str] = None
    ) -> Path:
        """
        Generate report in specified format
        
        Args:
            report_id: Database report ID
            report_data: Report data dictionary (from database queries)
            format: Output format ('pdf' or 'pptx')
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to generated report file
            
        Raises:
            ValueError: If format is not supported
        """
        if format not in self.exporters:
            available = ', '.join(self.exporters.keys())
            raise ValueError(f"Unsupported format '{format}'. Available: {available}")
        
        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            month = report_data.get('month', 'Unknown')
            year = report_data.get('year', datetime.now().year)
            filename = f"Report_{month}_{year}_{timestamp}"
        
        # Add extension
        extension = self.exporters[format].get_format()
        output_path = self.output_dir / f"{filename}.{extension}"
        
        # Generate report
        logger.info(f"Generating {format.upper()} report: {filename}")
        exporter = self.exporters[format]
        result_path = exporter.export(report_data, output_path)
        
        logger.info(f"Report generated successfully: {result_path}")
        return result_path
    
    def register_exporter(self, format: str, exporter: ReportExporter):
        """
        Register a new exporter format
        
        This allows easy extension with new formats without modifying core code
        """
        self.exporters[format] = exporter
        logger.info(f"Registered new exporter: {format}")
    
    def get_available_formats(self) -> list[str]:
        """Return list of available export formats"""
        return list(self.exporters.keys())


# Convenience function for easy usage
def generate_report(
    report_id: int,
    report_data: Dict[str, Any],
    format: str = 'pdf',
    template_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Quick function to generate a report
    
    Usage:
        from services.report_generator import generate_report
        
        report_data = {...}  # From database
        pdf_path = generate_report(123, report_data, format='pdf')
        
        # Future: PPTX support
        # pptx_path = generate_report(123, report_data, format='pptx')
    """
    if not template_dir:
        template_dir = Path(__file__).parent.parent / 'templates'
    
    if not output_dir:
        output_dir = Path(__file__).parent.parent.parent / 'reports'
    
    generator = ReportGenerator(template_dir, output_dir)
    return generator.generate(report_id, report_data, format)
