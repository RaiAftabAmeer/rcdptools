from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import pandas as pd
import openpyxl
import io
from fastapi.responses import JSONResponse


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ExcelData(BaseModel):
    srNo: int
    memberId: str
    name: str
    branch: str
    co: str
    dueTotal: float
    currentRecTotal: float
    totalOverdue: float
    currentAdvance: float
    openingAdvance: float
    disbDate: str
    lastInstallDate: str
    olp: float
    cellNo: str

class DashboardMetrics(BaseModel):
    key: str
    activeCount: int
    currentDueClients: int
    currentDueAmount: float
    currentRecoveredClients: int
    currentRecoveredAmount: float
    lastMonthTillClients: int
    lastMonthTillAmount: float
    remainingDueClients: int
    remainingDueAmount: float
    yesterdayRecoveredClients: int
    yesterdayRecoveredAmount: float
    todayRecoveredClients: int
    todayRecoveredAmount: float
    currentAdvanceClients: int
    currentAdvanceAmount: float
    openingAdvanceClients: int
    openingAdvanceAmount: float
    olpAmount: float
    recoveryPercentage: float
    clients: List[ExcelData] = []

class ProcessedDashboardData(BaseModel):
    totalMetrics: Dict[str, Any]
    branchMetrics: List[DashboardMetrics]
    coMetrics: List[DashboardMetrics]

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

def process_excel_file(file_content: bytes, file_name: str) -> List[ExcelData]:
    """Process Excel file and extract data similar to the HTML version logic"""
    try:
        # Read Excel file
        df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
        
        # Skip first 2 rows and process data (similar to HTML logic)
        if len(df) <= 2:
            raise ValueError("Excel file has insufficient data")
        
        data = df.iloc[2:].reset_index(drop=True)  # Skip first 2 rows
        
        processed_data = []
        for index, row in data.iterrows():
            try:
                # Safe value extraction with defaults
                def safe_get(series, idx, default=''):
                    return series.iloc[idx] if idx < len(series) and pd.notna(series.iloc[idx]) else default
                
                def safe_float(value):
                    try:
                        return float(value) if pd.notna(value) else 0.0
                    except:
                        return 0.0
                
                def format_date(date_val):
                    if pd.isna(date_val):
                        return ''
                    if isinstance(date_val, datetime):
                        return date_val.strftime('%d-%b-%y')
                    return str(date_val)
                
                item = ExcelData(
                    srNo=index + 1,
                    memberId=str(safe_get(row, 1, '')),
                    name=str(safe_get(row, 2, '')),
                    branch=str(safe_get(row, 4, 'Unknown')),
                    co=str(safe_get(row, 5, 'Unknown')),
                    dueTotal=safe_float(safe_get(row, 10)),
                    currentRecTotal=safe_float(safe_get(row, 14)),
                    totalOverdue=safe_float(safe_get(row, 21)),
                    currentAdvance=safe_float(safe_get(row, 18)),
                    openingAdvance=safe_float(safe_get(row, 17)),
                    disbDate=format_date(safe_get(row, 23)),
                    lastInstallDate=format_date(safe_get(row, 26)),
                    olp=safe_float(safe_get(row, 27)),
                    cellNo=str(safe_get(row, 31, ''))
                )
                
                # Filter out items with Unknown branch/co
                if item.branch != 'Unknown' and item.co != 'Unknown':
                    processed_data.append(item)
                    
            except Exception as e:
                logger.warning(f"Error processing row {index}: {e}")
                continue
        
        return processed_data
        
    except Exception as e:
        logger.error(f"Error processing Excel file {file_name}: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")

def calculate_metrics(current_data: List[ExcelData], last_month_data: List[ExcelData], 
                     view_type: str = 'Branch', yesterday_date: str = '', today_date: str = '') -> Dict[str, DashboardMetrics]:
    """Calculate metrics similar to the HTML dashboard logic"""
    
    metrics = {}
    
    # Build last month due data map for reference
    last_month_due_data = {}
    for item in last_month_data:
        key = item.branch if view_type == 'Branch' else item.co
        if key not in last_month_due_data:
            last_month_due_data[key] = 0
        if item.dueTotal > 2:
            last_month_due_data[key] += item.dueTotal
    
    # Process current month data
    for item in current_data:
        key = item.branch if view_type == 'Branch' else item.co
        
        if key not in metrics:
            metrics[key] = DashboardMetrics(
                key=key,
                activeCount=0,
                currentDueClients=0,
                currentDueAmount=0,
                currentRecoveredClients=0,
                currentRecoveredAmount=0,
                lastMonthTillClients=0,
                lastMonthTillAmount=0,
                remainingDueClients=0,
                remainingDueAmount=0,
                yesterdayRecoveredClients=0,
                yesterdayRecoveredAmount=0,
                todayRecoveredClients=0,
                todayRecoveredAmount=0,
                currentAdvanceClients=0,
                currentAdvanceAmount=0,
                openingAdvanceClients=0,
                openingAdvanceAmount=0,
                olpAmount=0,
                recoveryPercentage=0,
                clients=[]
            )
        
        # Add to active count and client list
        metrics[key].activeCount += 1
        metrics[key].clients.append(item)
        
        # Current Due calculation
        if item.dueTotal > 2:
            metrics[key].currentDueClients += 1
            metrics[key].currentDueAmount += item.dueTotal
        
        # Current Recovered calculation  
        if item.currentRecTotal > 2:
            metrics[key].currentRecoveredClients += 1
            metrics[key].currentRecoveredAmount += item.currentRecTotal
        
        # Remaining Due calculation
        if item.totalOverdue > 5:
            metrics[key].remainingDueClients += 1
            metrics[key].remainingDueAmount += item.totalOverdue
        
        # Yesterday/Today recovered (simplified date matching)
        if item.currentRecTotal > 2 and item.lastInstallDate == yesterday_date and item.currentAdvance <= 2:
            metrics[key].yesterdayRecoveredClients += 1
            metrics[key].yesterdayRecoveredAmount += item.currentRecTotal
        
        if item.lastInstallDate == today_date and item.currentAdvance <= 1 and item.currentRecTotal > 2:
            metrics[key].todayRecoveredClients += 1
            metrics[key].todayRecoveredAmount += item.currentRecTotal
        
        # Current Advance calculation
        if item.currentAdvance > 2:
            metrics[key].currentAdvanceClients += 1
            metrics[key].currentAdvanceAmount += item.currentAdvance
        
        # Opening Advance calculation
        if item.openingAdvance > 2:
            metrics[key].openingAdvanceClients += 1
            metrics[key].openingAdvanceAmount += item.openingAdvance
        
        # OLP calculation
        metrics[key].olpAmount += item.olp
    
    # Process last month data for "Last Month Till" calculations
    for item in last_month_data:
        key = item.branch if view_type == 'Branch' else item.co
        if key in metrics and item.currentRecTotal > 2:
            metrics[key].lastMonthTillClients += 1
            metrics[key].lastMonthTillAmount += item.currentRecTotal
    
    # Calculate recovery percentages
    for key, data in metrics.items():
        if data.currentDueAmount > 0:
            data.recoveryPercentage = round((data.currentRecoveredAmount / data.currentDueAmount) * 100, 2)
    
    return metrics

@api_router.post("/upload-excel", response_model=ProcessedDashboardData)
async def upload_excel_files(
    current_month_file: UploadFile = File(...),
    last_month_file: UploadFile = File(...),
    yesterday_date: str = '',
    today_date: str = ''
):
    """Upload and process Excel files for dashboard data"""
    
    try:
        # Validate file types
        if not current_month_file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Current month file must be Excel format")
        if not last_month_file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Last month file must be Excel format")
        
        # Read file contents
        current_content = await current_month_file.read()
        last_month_content = await last_month_file.read()
        
        # Process Excel files
        current_data = process_excel_file(current_content, current_month_file.filename)
        last_month_data = process_excel_file(last_month_content, last_month_file.filename)
        
        if not current_data:
            raise HTTPException(status_code=400, detail="No valid data found in current month file")
        if not last_month_data:
            raise HTTPException(status_code=400, detail="No valid data found in last month file")
        
        # Calculate metrics for both views
        branch_metrics_dict = calculate_metrics(current_data, last_month_data, 'Branch', yesterday_date, today_date)
        co_metrics_dict = calculate_metrics(current_data, last_month_data, 'CO', yesterday_date, today_date)
        
        # Convert to lists
        branch_metrics = list(branch_metrics_dict.values())
        co_metrics = list(co_metrics_dict.values())
        
        # Calculate total metrics
        total_metrics = {
            "totalActiveClients": sum(m.activeCount for m in branch_metrics),
            "totalCurrentDueAmount": sum(m.currentDueAmount for m in branch_metrics),
            "totalCurrentRecoveredAmount": sum(m.currentRecoveredAmount for m in branch_metrics),
            "totalRecoveryPercentage": 0
        }
        
        if total_metrics["totalCurrentDueAmount"] > 0:
            total_metrics["totalRecoveryPercentage"] = round(
                (total_metrics["totalCurrentRecoveredAmount"] / total_metrics["totalCurrentDueAmount"]) * 100, 2
            )
        
        # Store processed data in database for caching
        dashboard_data = {
            "timestamp": datetime.utcnow(),
            "total_metrics": total_metrics,
            "branch_metrics": [m.dict() for m in branch_metrics],
            "co_metrics": [m.dict() for m in co_metrics]
        }
        
        await db.dashboard_data.insert_one(dashboard_data)
        
        return ProcessedDashboardData(
            totalMetrics=total_metrics,
            branchMetrics=branch_metrics,
            coMetrics=co_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Excel files: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/dashboard-data", response_model=ProcessedDashboardData)
async def get_latest_dashboard_data():
    """Get the latest processed dashboard data"""
    try:
        # Get the most recent dashboard data
        latest_data = await db.dashboard_data.find_one(
            sort=[("timestamp", -1)]
        )
        
        if not latest_data:
            raise HTTPException(status_code=404, detail="No dashboard data found. Please upload Excel files first.")
        
        return ProcessedDashboardData(
            totalMetrics=latest_data["total_metrics"],
            branchMetrics=[DashboardMetrics(**m) for m in latest_data["branch_metrics"]],
            coMetrics=[DashboardMetrics(**m) for m in latest_data["co_metrics"]]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
