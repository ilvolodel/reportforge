"""Report models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Date, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base


class Report(Base):
    """Monthly report model."""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    month = Column(Date, nullable=False)  # First day of report month (e.g., 2026-01-01)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("ReportProject", back_populates="report", cascade="all, delete-orphan")
    executive_summary = relationship("ReportExecutiveSummary", back_populates="report", uselist=False, cascade="all, delete-orphan")
    versions = relationship("ReportVersion", back_populates="report", cascade="all, delete-orphan")


class ReportProject(Base):
    """Many-to-many relationship between reports and projects."""
    
    __tablename__ = "report_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    sort_order = Column(Integer, default=0)  # For ordering projects in report
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    report = relationship("Report", back_populates="projects")
    project = relationship("Project", back_populates="report_projects")


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
    created_by_user = relationship("User", back_populates="report_versions")
