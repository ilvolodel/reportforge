"""Report schemas for API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


# Template Schemas
class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    config: Dict[str, Any] = Field(default_factory=dict)


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ReportTemplate(ReportTemplateBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Project Snapshot Schemas
class ReportProjectSnapshotBase(BaseModel):
    project_id: Optional[int] = None
    sort_order: int = 0
    name: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    financial_data: Dict[str, Any] = Field(default_factory=dict)
    team_data: List[Dict[str, Any]] = Field(default_factory=list)
    stakeholder_data: List[Dict[str, Any]] = Field(default_factory=list)
    client_data: List[Dict[str, Any]] = Field(default_factory=list)
    activities_data: List[Dict[str, Any]] = Field(default_factory=list)
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ReportProjectSnapshotCreate(ReportProjectSnapshotBase):
    pass


class ReportProjectSnapshotUpdate(BaseModel):
    sort_order: Optional[int] = None
    name: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    financial_data: Optional[Dict[str, Any]] = None
    team_data: Optional[List[Dict[str, Any]]] = None
    stakeholder_data: Optional[List[Dict[str, Any]]] = None
    client_data: Optional[List[Dict[str, Any]]] = None
    activities_data: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ReportProjectSnapshot(ReportProjectSnapshotBase):
    id: int
    report_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Executive Summary Schemas
class ReportExecutiveSummaryBase(BaseModel):
    actual_revenue_total: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    actual_saving_total: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    actual_projects_count: int = 0
    forecast_revenue_total: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    forecast_saving_total: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    forecast_projects_count: int = 0
    notes: Optional[str] = None


class ReportExecutiveSummaryUpdate(BaseModel):
    actual_revenue_total: Optional[Decimal] = None
    actual_saving_total: Optional[Decimal] = None
    actual_projects_count: Optional[int] = None
    forecast_revenue_total: Optional[Decimal] = None
    forecast_saving_total: Optional[Decimal] = None
    forecast_projects_count: Optional[int] = None
    notes: Optional[str] = None


class ReportExecutiveSummary(ReportExecutiveSummaryBase):
    id: int
    report_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Report Schemas
class ReportBase(BaseModel):
    name: str
    period_start: date
    period_end: date
    status: str = "draft"
    template_config: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class ReportCreate(ReportBase):
    template_id: Optional[int] = None  # Use template config
    project_ids: Optional[List[int]] = None  # Projects to include


class ReportUpdate(BaseModel):
    name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    status: Optional[str] = None
    template_config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class Report(ReportBase):
    id: int
    pdf_path: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include related data
    project_snapshots: List[ReportProjectSnapshot] = []
    executive_summary: Optional[ReportExecutiveSummary] = None

    class Config:
        from_attributes = True


class ReportList(BaseModel):
    """Simplified report for list view."""
    id: int
    name: str
    period_start: date
    period_end: date
    status: str
    pdf_path: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    projects_count: int = 0

    class Config:
        from_attributes = True


class ReportCopy(BaseModel):
    """Request to copy an existing report."""
    name: str
    period_start: date
    period_end: date


class GeneratePDFRequest(BaseModel):
    """Request to generate PDF for a report."""
    finalize: bool = False  # Set status to "final" after generation
