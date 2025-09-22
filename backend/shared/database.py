from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from .models import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:password@localhost:3306/impact_analyzer"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def init_sample_data():
    """Initialize sample data for testing"""
    from datetime import datetime, timedelta
    from .models import DailyMetricsTable, TestFlowsTable
    
    db = SessionLocal()
    try:
        # Check if sample data already exists
        existing_metrics = db.query(DailyMetricsTable).first()
        if existing_metrics:
            return
            
        # Create yesterday's metrics
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_metrics = DailyMetricsTable(
            dayId=yesterday,
            couplingValue=0.73,
            TotNoOfTestCases=1247,
            MRCountDayWise=23,
            totalUnitTestCoverage=87.5,
            passedTests=156,
            failedTests=8
        )
        
        # Create today's metrics
        today = datetime.now().strftime('%Y-%m-%d')
        today_metrics = DailyMetricsTable(
            dayId=today,
            couplingValue=0.75,
            TotNoOfTestCases=1250,
            MRCountDayWise=7,
            totalUnitTestCoverage=89.2,
            passedTests=160,
            failedTests=5
        )
        
        # Create sample test flows
        test_flows = [
            TestFlowsTable(
                testFlowName="User Registration Flow",
                fileName="UserRegistrationTest.java",
                status="passed",
                duration="2m 34s",
                lastRun=datetime.now(),
                steps=12,
                passedSteps=12,
                failedSteps=0,
                projectId="angular-springboot-ecommerce"
            ),
            TestFlowsTable(
                testFlowName="Payment Processing Flow",
                fileName="PaymentProcessingTest.java",
                status="failed",
                duration="1m 45s",
                lastRun=datetime.now(),
                steps=8,
                passedSteps=6,
                failedSteps=2,
                projectId="angular-springboot-ecommerce"
            ),
            TestFlowsTable(
                testFlowName="Order Management Flow",
                fileName="OrderManagementTest.java",
                status="running",
                duration="3m 12s",
                lastRun=datetime.now(),
                steps=15,
                passedSteps=10,
                failedSteps=0,
                projectId="angular-springboot-ecommerce"
            ),
            TestFlowsTable(
                testFlowName="Product Catalog Flow",
                fileName="ProductCatalogTest.java",
                status="passed",
                duration="1m 58s",
                lastRun=datetime.now(),
                steps=9,
                passedSteps=9,
                failedSteps=0,
                projectId="angular-springboot-ecommerce"
            ),
            TestFlowsTable(
                testFlowName="Category Management Flow",
                fileName="CategoryManagementTest.java",
                status="pending",
                duration="-",
                lastRun=None,
                steps=6,
                passedSteps=0,
                failedSteps=0,
                projectId="angular-springboot-ecommerce"
            )
        ]
        
        db.add(yesterday_metrics)
        db.add(today_metrics)
        for flow in test_flows:
            db.add(flow)
            
        db.commit()
        print("Sample data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()