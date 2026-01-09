"""Project-related models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Date, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ProjectType(str, enum.Enum):
    """Project type enum."""
    INTERNAL = "INTERNAL"
    PARTNER = "PARTNER"
    CLIENT = "CLIENT"


class ProjectStatus(str, enum.Enum):
    """Project status enum."""
    FORECAST = "FORECAST"
    PROPOSAL = "PROPOSAL"
    SOLD = "SOLD"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    GO_LIVE = "GO_LIVE"
    OPERATIONAL = "OPERATIONAL"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ActivityStatus(str, enum.Enum):
    """Activity status enum."""
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class CostCategory(str, enum.Enum):
    """Cost category enum."""
    INTERNAL = "INTERNAL"
    VENDOR = "VENDOR"
    INFRASTRUCTURE = "INFRASTRUCTURE"


class Project(Base):
    """Project model."""
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.FORECAST)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stakeholders = relationship("ProjectStakeholder", back_populates="project", cascade="all, delete-orphan")
    clients = relationship("ProjectClient", back_populates="project", cascade="all, delete-orphan")
    team = relationship("ProjectTeam", back_populates="project", cascade="all, delete-orphan")
    activities = relationship("ProjectActivity", back_populates="project", cascade="all, delete-orphan")
    costs = relationship("ProjectCost", back_populates="project", cascade="all, delete-orphan")
    revenue_one_time = relationship("RevenueOneTime", back_populates="project", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="project", cascade="all, delete-orphan")


class Stakeholder(Base):
    """Stakeholder model (Customer Care, Sales, Marketing, etc.)."""
    
    __tablename__ = "stakeholders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    projects = relationship("ProjectStakeholder", back_populates="stakeholder")


class ProjectStakeholder(Base):
    """Many-to-many relationship between projects and stakeholders."""
    
    __tablename__ = "project_stakeholders"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(255))  # e.g., "Primary", "Secondary"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="stakeholders")
    stakeholder = relationship("Stakeholder", back_populates="projects")


class Client(Base):
    """Client model (NORMA, ASL CUNEO, Casadei, etc.)."""
    
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    projects = relationship("ProjectClient", back_populates="client")


class ProjectClient(Base):
    """Many-to-many relationship between projects and clients."""
    
    __tablename__ = "project_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="clients")
    client = relationship("Client", back_populates="projects")


class TeamMember(Base):
    """Team member model (J. Cotrina, F. Savarese, etc.)."""
    
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    role = Column(String(255))  # e.g., "PM", "Developer", "Architect"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    projects = relationship("ProjectTeam", back_populates="team_member")


class ProjectTeam(Base):
    """Many-to-many relationship between projects and team members."""
    
    __tablename__ = "project_team"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    team_member_id = Column(Integer, ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False)
    role_in_project = Column(String(255))  # Specific role in this project
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="team")
    team_member = relationship("TeamMember", back_populates="projects")


class ProjectActivity(Base):
    """Project activity/milestone model."""
    
    __tablename__ = "project_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ActivityStatus), nullable=False, default=ActivityStatus.PLANNED)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="activities")


class ProjectCost(Base):
    """Project cost model (INTERNAL, VENDOR, INFRASTRUCTURE)."""
    
    __tablename__ = "project_costs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    category = Column(SQLEnum(CostCategory), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="costs")
