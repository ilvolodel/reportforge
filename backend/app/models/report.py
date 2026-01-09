"""Report models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Date, func, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base
import enum


class ReportStatus(str, enum.Enum):
    """Report status enum."""
    DRAFT = "draft"
    FINAL = "final"


class Report(Base):
    """Monthly report model with versioning and configuration."""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # "Report Dicembre 2025"
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String(50), default=ReportStatus.DRAFT)
    
    # Template configuration (what sections to include)
    template_config = Column(JSONB, default={})
    
    # Generated PDF
    pdf_path = Column(String(500))
    pdf_generated_at = Column(DateTime(timezone=True))
    
    # Metadata
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project_snapshots = relationship("ReportProjectSnapshot", back_populates="report", cascade="all, delete-orphan")
    executive_summary = relationship("ReportExecutiveSummary", back_populates="report", uselist=False, cascade="all, delete-orphan")
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class ReportProjectSnapshot(Base):
    """Snapshot of project data at report generation time."""
    
    __tablename__ = "report_project_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"))  # Keep snapshot even if project deleted
    sort_order = Column(Integer, default=0)
    
    # Snapshot data (editable in report)
    name = Column(String(255))
    project_type = Column(String(50))
    status = Column(String(50))
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Financial snapshot
    financial_data = Column(JSONB, default={})  # Revenue, saving, costs breakdown
    
    # Team & stakeholders snapshot
    team_data = Column(JSONB, default=[])  # List of team members
    stakeholder_data = Column(JSONB, default=[])  # List of stakeholders
    client_data = Column(JSONB, default=[])  # List of clients
    
    # Activities snapshot
    activities_data = Column(JSONB, default=[])  # List of activities with status
    
    # Notes & custom fields
    notes = Column(Text)
    custom_fields = Column(JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="project_snapshots")
    project = relationship("Project")


class ReportExecutiveSummary(Base):
    """Executive summary with calculated totals."""
    
    __tablename__ = "report_executive_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # ACTUAL (current year)
    actual_revenue_total = Column(Numeric(15, 2), default=0)
    actual_saving_total = Column(Numeric(15, 2), default=0)
    actual_projects_count = Column(Integer, default=0)
    
    # FORECAST (next year)
    forecast_revenue_total = Column(Numeric(15, 2), default=0)
    forecast_saving_total = Column(Numeric(15, 2), default=0)
    forecast_projects_count = Column(Integer, default=0)
    
    # Additional metadata
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="executive_summary")


class ReportVersion(Base):
    """Version history for reports (complete snapshot)."""
    
    __tablename__ = "report_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    data_snapshot = Column(JSONB, nullable=False)  # Full JSON snapshot
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    
    # Relationships
    report = relationship("Report", back_populates="versions")
    created_by_user = relationship("User")


class ReportTemplate(Base):
    """Saved report template configurations (reusable)."""
    
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # "Report Standard", "Report Executive"
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    
    # Configuration: which sections to include
    config = Column(JSONB, default={
        # Global sections
        "include_executive_summary": True,
        "include_pipeline": True,
        "include_team_overview": True,
        
        # Per-project details
        "include_project_description": True,
        "include_project_team": True,
        "include_project_activities": True,
        "include_project_timeline": False,
        "include_project_kpis": False,
        "include_project_risks": True,
        "include_project_notes": True,
        
        # Charts
        "include_revenue_trend": True,
        "include_client_breakdown": True,
        "include_cost_breakdown": False,
        "include_project_status_chart": False
    })
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
