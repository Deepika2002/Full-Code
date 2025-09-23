from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class TestFlowsTable(Base):
    __tablename__ = "test_flows_table"
    
    TestFlowId = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    TestFlowName = Column(String(200), nullable=False)
    FileName = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, passed, failed
    duration = Column(String(50))
    lastRun = Column(DateTime)
    steps = Column(Integer, default=0)
    passedSteps = Column(Integer, default=0)
    failedSteps = Column(Integer, default=0)
    projectId = Column(String(50))
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MRTable(Base):
    __tablename__ = "mr_table"
    
    mrID = Column(String(50), primary_key=True)
    author = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    totalUnitTestCoverage = Column(Float, default=0.0)
    CommaSeparatedChangedClassNamesWithPath = Column(Text)
    CommaSeparatedChangedClassSeverity = Column(Text)
    OverallSeverityScore = Column(Float, default=0.0)
    TestFlowIds = Column(JSON)  # List of TestFlowId references
    functionalChangeDescription = Column(Text)
    technicalChangeDescription = Column(Text)
    projectId = Column(String(50))
    gitDiff = Column(Text)
    analysisId = Column(String(50))
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyMetricsTable(Base):
    __tablename__ = "daily_metrics_table"
    
    dayId = Column(String(20), primary_key=True)  # YYYY-MM-DD format
    couplingValue = Column(Float, default=0.0)
    TotNoOfTestCases = Column(Integer, default=0)
    MRCountDayWise = Column(Integer, default=0)
    totalUnitTestCoverage = Column(Float, default=0.0)
    passedTests = Column(Integer, default=0)
    failedTests = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChangedClassNames(Base):
    __tablename__ = "changed_class_names"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mrID = Column(String(50), ForeignKey("mr_table.mrID"))
    className = Column(String(200))
    classPath = Column(String(500))
    severity = Column(String(20))  # High, Medium, Low
    reason = Column(Text)
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mr = relationship("MRTable")

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
    gcsVectorPath = Column(String(500))  # Google Cloud Storage path
    createdAt = Column(DateTime, default=datetime.utcnow)

class VectorMetadata(Base):
    __tablename__ = "vector_metadata"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    vectorId = Column(Integer)  # Vector index ID
    sourceType = Column(String(50))  # 'dependency', 'code', 'class'
    sourceId = Column(String(100))  # class name, file path, etc.
    projectId = Column(String(50))
    content = Column(Text)  # Original text that was embedded
    metadata = Column(JSON)  # Additional metadata
    gcsPath = Column(String(500))  # Google Cloud Storage path
    createdAt = Column(DateTime, default=datetime.utcnow)

class TestCaseResults(Base):
    __tablename__ = "test_case_results"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    TestFlowId = Column(String(50), ForeignKey("test_flows_table.TestFlowId"))
    mrID = Column(String(50), ForeignKey("mr_table.mrID"))
    executionId = Column(String(50))
    status = Column(String(50))  # running, passed, failed, timeout
    startTime = Column(DateTime)
    endTime = Column(DateTime)
    duration = Column(Integer)  # in seconds
    errorMessage = Column(Text)
    logOutput = Column(Text)
    gcsLogPath = Column(String(500))  # Google Cloud Storage path for logs
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_flow = relationship("TestFlowsTable")
    mr = relationship("MRTable")