"""Reports API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.report import Report, ReportProjectSnapshot, ReportExecutiveSummary, ReportTemplate, ReportStatus
from ..models.project import Project
from ..schemas import report as schemas

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ============================================================================
# TEMPLATES
# ============================================================================

@router.get("/templates", response_model=List[schemas.ReportTemplate])
def list_templates(db: Session = Depends(get_db)):
    """List all report templates."""
    templates = db.query(ReportTemplate).order_by(ReportTemplate.is_default.desc(), ReportTemplate.name).all()
    return templates


@router.post("/templates", response_model=schemas.ReportTemplate, status_code=status.HTTP_201_CREATED)
def create_template(template: schemas.ReportTemplateCreate, db: Session = Depends(get_db)):
    """Create a new report template."""
    db_template = ReportTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/templates/{template_id}", response_model=schemas.ReportTemplate)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific template."""
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=schemas.ReportTemplate)
def update_template(template_id: int, template: schemas.ReportTemplateUpdate, db: Session = Depends(get_db)):
    """Update a template."""
    db_template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a template."""
    db_template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return


# ============================================================================
# REPORTS
# ============================================================================

@router.get("/", response_model=List[schemas.ReportList])
def list_reports(db: Session = Depends(get_db)):
    """List all reports with basic info."""
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    
    # Add projects count
    result = []
    for report in reports:
        report_data = schemas.ReportList.model_validate(report)
        report_data.projects_count = len(report.project_snapshots)
        result.append(report_data)
    
    return result


@router.post("/", response_model=schemas.Report, status_code=status.HTTP_201_CREATED)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    """Create a new report with project snapshots."""
    
    # Get template config if specified
    template_config = report.template_config
    if report.template_id:
        template = db.query(ReportTemplate).filter(ReportTemplate.id == report.template_id).first()
        if template:
            template_config = template.config
    
    # Create report
    db_report = Report(
        name=report.name,
        period_start=report.period_start,
        period_end=report.period_end,
        status=report.status,
        template_config=template_config,
        description=report.description
    )
    db.add(db_report)
    db.flush()  # Get report ID
    
    # Create project snapshots
    if report.project_ids:
        for idx, project_id in enumerate(report.project_ids):
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                # Create snapshot from current project data
                snapshot = _create_project_snapshot(db_report.id, project, idx, db)
                db.add(snapshot)
    
    # Create executive summary (empty for now, will be calculated)
    exec_summary = ReportExecutiveSummary(report_id=db_report.id)
    db.add(exec_summary)
    
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/{report_id}", response_model=schemas.Report)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report with all details."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=schemas.Report)
def update_report(report_id: int, report: schemas.ReportUpdate, db: Session = Depends(get_db)):
    """Update report metadata."""
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    update_data = report.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report."""
    db_report = db.query(Report).filter(Report.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(db_report)
    db.commit()
    return


@router.post("/{report_id}/copy", response_model=schemas.Report, status_code=status.HTTP_201_CREATED)
def copy_report(report_id: int, copy_data: schemas.ReportCopy, db: Session = Depends(get_db)):
    """Create a copy of an existing report with new period."""
    original = db.query(Report).filter(Report.id == report_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create new report
    new_report = Report(
        name=copy_data.name,
        period_start=copy_data.period_start,
        period_end=copy_data.period_end,
        status=ReportStatus.DRAFT,
        template_config=original.template_config,
        description=original.description
    )
    db.add(new_report)
    db.flush()
    
    # Copy project snapshots
    for snapshot in original.project_snapshots:
        new_snapshot = ReportProjectSnapshot(
            report_id=new_report.id,
            project_id=snapshot.project_id,
            sort_order=snapshot.sort_order,
            name=snapshot.name,
            project_type=snapshot.project_type,
            status=snapshot.status,
            description=snapshot.description,
            start_date=snapshot.start_date,
            end_date=snapshot.end_date,
            financial_data=snapshot.financial_data,
            team_data=snapshot.team_data,
            stakeholder_data=snapshot.stakeholder_data,
            client_data=snapshot.client_data,
            activities_data=snapshot.activities_data,
            notes=snapshot.notes,
            custom_fields=snapshot.custom_fields
        )
        db.add(new_snapshot)
    
    # Copy executive summary
    if original.executive_summary:
        new_summary = ReportExecutiveSummary(
            report_id=new_report.id,
            actual_revenue_total=original.executive_summary.actual_revenue_total,
            actual_saving_total=original.executive_summary.actual_saving_total,
            actual_projects_count=original.executive_summary.actual_projects_count,
            forecast_revenue_total=original.executive_summary.forecast_revenue_total,
            forecast_saving_total=original.executive_summary.forecast_saving_total,
            forecast_projects_count=original.executive_summary.forecast_projects_count,
            notes=original.executive_summary.notes
        )
        db.add(new_summary)
    
    db.commit()
    db.refresh(new_report)
    return new_report


# ============================================================================
# PROJECT SNAPSHOTS
# ============================================================================

@router.get("/{report_id}/projects", response_model=List[schemas.ReportProjectSnapshot])
def list_report_projects(report_id: int, db: Session = Depends(get_db)):
    """Get all project snapshots in a report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report.project_snapshots


@router.post("/{report_id}/projects", response_model=schemas.ReportProjectSnapshot, status_code=status.HTTP_201_CREATED)
def add_project_to_report(report_id: int, snapshot: schemas.ReportProjectSnapshotCreate, db: Session = Depends(get_db)):
    """Add a project snapshot to report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # If project_id provided, create snapshot from existing project
    if snapshot.project_id:
        project = db.query(Project).filter(Project.id == snapshot.project_id).first()
        if project:
            db_snapshot = _create_project_snapshot(report_id, project, snapshot.sort_order, db)
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    else:
        # Create snapshot from provided data
        db_snapshot = ReportProjectSnapshot(report_id=report_id, **snapshot.model_dump(exclude={"project_id"}))
    
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    return db_snapshot


@router.put("/{report_id}/projects/{snapshot_id}", response_model=schemas.ReportProjectSnapshot)
def update_project_snapshot(
    report_id: int,
    snapshot_id: int,
    snapshot: schemas.ReportProjectSnapshotUpdate,
    db: Session = Depends(get_db)
):
    """Update a project snapshot (this is where editing happens!)."""
    db_snapshot = db.query(ReportProjectSnapshot).filter(
        ReportProjectSnapshot.id == snapshot_id,
        ReportProjectSnapshot.report_id == report_id
    ).first()
    
    if not db_snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    update_data = snapshot.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_snapshot, field, value)
    
    db.commit()
    db.refresh(db_snapshot)
    
    # Also update the original project if it still exists
    if db_snapshot.project_id:
        _sync_snapshot_to_project(db_snapshot, db)
    
    return db_snapshot


@router.delete("/{report_id}/projects/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_from_report(report_id: int, snapshot_id: int, db: Session = Depends(get_db)):
    """Remove a project snapshot from report."""
    db_snapshot = db.query(ReportProjectSnapshot).filter(
        ReportProjectSnapshot.id == snapshot_id,
        ReportProjectSnapshot.report_id == report_id
    ).first()
    
    if not db_snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    db.delete(db_snapshot)
    db.commit()
    return


# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================

@router.put("/{report_id}/executive-summary", response_model=schemas.ReportExecutiveSummary)
def update_executive_summary(
    report_id: int,
    summary: schemas.ReportExecutiveSummaryUpdate,
    db: Session = Depends(get_db)
):
    """Update executive summary."""
    db_summary = db.query(ReportExecutiveSummary).filter(
        ReportExecutiveSummary.report_id == report_id
    ).first()
    
    if not db_summary:
        raise HTTPException(status_code=404, detail="Executive summary not found")
    
    update_data = summary.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_summary, field, value)
    
    db.commit()
    db.refresh(db_summary)
    return db_summary


@router.post("/{report_id}/calculate", response_model=schemas.ReportExecutiveSummary)
def calculate_executive_summary(report_id: int, db: Session = Depends(get_db)):
    """Calculate executive summary from project snapshots."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.executive_summary:
        exec_summary = ReportExecutiveSummary(report_id=report_id)
        db.add(exec_summary)
    else:
        exec_summary = report.executive_summary
    
    # Calculate totals from snapshots
    from decimal import Decimal
    total_revenue = Decimal("0.00")
    total_saving = Decimal("0.00")
    
    for snapshot in report.project_snapshots:
        if snapshot.financial_data:
            # Sum up revenue
            revenue_capex = Decimal(str(snapshot.financial_data.get("revenue_capex", 0)))
            revenue_subscription = Decimal(str(snapshot.financial_data.get("revenue_subscription", 0)))
            total_revenue += revenue_capex + revenue_subscription
            
            # Sum up saving
            saving_capex = Decimal(str(snapshot.financial_data.get("saving_capex", 0)))
            saving_subscription = Decimal(str(snapshot.financial_data.get("saving_subscription", 0)))
            total_saving += saving_capex + saving_subscription
    
    exec_summary.actual_revenue_total = total_revenue
    exec_summary.actual_saving_total = total_saving
    exec_summary.actual_projects_count = len(report.project_snapshots)
    
    db.commit()
    db.refresh(exec_summary)
    return exec_summary


# ============================================================================
# PDF GENERATION (placeholder)
# ============================================================================

@router.post("/{report_id}/generate-pdf")
def generate_pdf(report_id: int, request: schemas.GeneratePDFRequest, db: Session = Depends(get_db)):
    """Generate PDF for report (placeholder)."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # TODO: Implement PDF generation with WeasyPrint
    # For now, just update status if requested
    if request.finalize:
        report.status = ReportStatus.FINAL
        report.pdf_generated_at = datetime.utcnow()
        db.commit()
    
    return {
        "message": "PDF generation not yet implemented",
        "report_id": report_id,
        "status": report.status
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _create_project_snapshot(report_id: int, project: Project, sort_order: int, db: Session) -> ReportProjectSnapshot:
    """Create a snapshot from a project."""
    
    # Gather financial data
    financial_data = {
        "revenue_capex": float(sum([r.amount for r in project.revenue_one_time]) if project.revenue_one_time else 0),
        "revenue_subscription": float(sum([s.amount_per_period for s in project.subscriptions if s.impact_type == "REVENUE"]) if project.subscriptions else 0),
        "saving_capex": 0,  # TODO: Calculate from one-time saving
        "saving_subscription": float(sum([s.amount_per_period for s in project.subscriptions if s.impact_type == "SAVING"]) if project.subscriptions else 0),
        "costs": {
            "internal": float(sum([c.amount for c in project.costs if c.category == "INTERNAL"]) if project.costs else 0),
            "vendor": float(sum([c.amount for c in project.costs if c.category == "VENDOR"]) if project.costs else 0),
            "infrastructure": float(sum([c.amount for c in project.costs if c.category == "INFRASTRUCTURE"]) if project.costs else 0)
        }
    }
    
    # Gather team data
    team_data = [{"name": tm.team_member.name, "role": tm.role} for tm in project.team] if project.team else []
    
    # Gather stakeholder data
    stakeholder_data = [{"name": ps.stakeholder.name} for ps in project.stakeholders] if project.stakeholders else []
    
    # Gather client data
    client_data = [{"name": pc.client.name} for pc in project.clients] if project.clients else []
    
    # Gather activities
    activities_data = [
        {
            "name": a.name,
            "status": a.status,
            "start_date": a.start_date.isoformat() if a.start_date else None,
            "end_date": a.end_date.isoformat() if a.end_date else None
        }
        for a in project.activities
    ] if project.activities else []
    
    return ReportProjectSnapshot(
        report_id=report_id,
        project_id=project.id,
        sort_order=sort_order,
        name=project.name,
        project_type=project.project_type,
        status=project.status,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        financial_data=financial_data,
        team_data=team_data,
        stakeholder_data=stakeholder_data,
        client_data=client_data,
        activities_data=activities_data
    )


def _sync_snapshot_to_project(snapshot: ReportProjectSnapshot, db: Session):
    """Sync edited snapshot data back to original project."""
    if not snapshot.project_id:
        return
    
    project = db.query(Project).filter(Project.id == snapshot.project_id).first()
    if not project:
        return
    
    # Update basic fields
    project.name = snapshot.name
    project.description = snapshot.description
    project.status = snapshot.status
    project.start_date = snapshot.start_date
    project.end_date = snapshot.end_date
    
    db.commit()
