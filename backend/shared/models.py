from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class MRTable(Base):
    __tablename__ = "mr_table"
    
    mrID = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    author = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    totalUnitTestCoverage = Column(Float, default=0.0)
    CommaSeparatedChangedClassNames = Column(Text)
    SeverityScore = Column(Float, default=0.0)
    TestExecutedIDs = Column(JSON)  # List of test flow IDs
    description = Column(Text)
    projectId = Column(String(50))
    gitDiff = Column(Text)
    analysisId = Column(String(50))
    
    # Relationships
    changed_classes = relationship("ChangedClassNames", back_populates="mr")

class TestFlowsTable(Base):
    __tablename__ = "test_flows_table"
    
    testFlowName = Column(String(200), primary_key=True)
    fileName = Column(String(500))
    status = Column(String(50), default="pending")  # pending, running, passed, failed
    duration = Column(String(50))
    lastRun = Column(DateTime)
    steps = Column(Integer, default=0)
    passedSteps = Column(Integer, default=0)
    failedSteps = Column(Integer, default=0)
    projectId = Column(String(50))

class DailyMetricsTable(Base):
    __tablename__ = "daily_metrics_table"
    
    dayId = Column(String(20), primary_key=True)  # YYYY-MM-DD format
    couplingValue = Column(Float, default=0.0)
    TotNoOfTestCases = Column(Integer, default=0)
    MRCountDayWise = Column(Integer, default=0)
    totalUnitTestCoverage = Column(Float, default=0.0)
    passedTests = Column(Integer, default=0)
    failedTests = Column(Integer, default=0)

class ChangedClassNames(Base):
    __tablename__ = "changed_class_names"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mrID = Column(String(50), ForeignKey("mr_table.mrID"))
    className = Column(String(200))
    severity = Column(String(20))  # High, Medium, Low
    reason = Column(Text)
    
    # Relationships
    mr = relationship("MRTable", back_populates="changed_classes")

class DependencyGraph(Base):
    __tablename__ = "dependency_graph"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    projectId = Column(String(50))
    repoUrl = Column(String(500))
    commitHash = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    author = Column(String(100))
    graphData = Column(JSON)  # Store nodes and edges
    vectorStorePath = Column(String(500))
    indexId = Column(String(50))

class VectorMetadata(Base):
    __tablename__ = "vector_metadata"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vectorId = Column(Integer)  # FAISS vector ID
    sourceType = Column(String(50))  # 'dependency', 'code', 'class'
    sourceId = Column(String(100))  # class name, file path, etc.
    projectId = Column(String(50))
    content = Column(Text)  # Original text that was embedded
    metadata = Column(JSON)  # Additional metadata