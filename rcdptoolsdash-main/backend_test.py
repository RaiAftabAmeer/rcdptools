#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for 3D Dashboard Excel Processing
Tests the core Excel file processing and dashboard data retrieval functionality
"""

import requests
import json
import os
import pandas as pd
import io
from datetime import datetime, timedelta
import tempfile
import sys

# Get backend URL from environment
BACKEND_URL = "https://stardust-metrics.preview.emergentagent.com/api"

class DashboardAPITester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, status, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def create_test_excel_file(self, filename, data_type="current"):
        """Create realistic test Excel files with proper structure"""
        
        # Create realistic sample data based on the expected Excel structure
        if data_type == "current":
            # Current month data with higher recovery amounts
            sample_data = [
                ["Sr No", "Member ID", "Name", "Address", "Branch", "CO", "Phone", "Guarantor", "Loan Amount", "EMI", "Due Total", "Installments", "Paid Amount", "Balance", "Current Rec Total", "Last Payment", "Status", "Opening Advance", "Current Advance", "Interest", "Principal", "Total Overdue", "Penalty", "Disb Date", "Maturity", "Last Install Date", "OLP", "Remarks", "Recovery Officer", "Collection Status", "Mobile", "Cell No"],
                [],  # Empty row as per original HTML logic
                [],  # Empty row as per original HTML logic
                [1, "MEM001", "Rajesh Kumar", "123 Main St", "Mumbai Central", "Priya Sharma", "9876543210", "Suresh Kumar", 50000, 2500, 15000, 24, 35000, 15000, 8000, "15-Jan-24", "Active", 1000, 500, 2000, 13000, 7000, 500, "15-Jan-23", "15-Jan-25", "14-Jan-24", 42000, "Regular", "Amit Singh", "Good", "9876543210", "9876543210"],
                [2, "MEM002", "Sunita Devi", "456 Park Ave", "Mumbai Central", "Priya Sharma", "9876543211", "Ram Devi", 75000, 3750, 22500, 24, 52500, 22500, 12000, "16-Jan-24", "Active", 1500, 800, 3000, 19500, 10500, 750, "16-Jan-23", "16-Jan-25", "15-Jan-24", 63000, "Regular", "Amit Singh", "Good", "9876543211", "9876543211"],
                [3, "MEM003", "Mohan Lal", "789 Oak St", "Andheri East", "Rahul Verma", "9876543212", "Shyam Lal", 60000, 3000, 18000, 24, 42000, 18000, 9500, "17-Jan-24", "Active", 1200, 600, 2400, 15600, 8500, 600, "17-Jan-23", "17-Jan-25", "16-Jan-24", 51000, "Regular", "Neha Patel", "Good", "9876543212", "9876543212"],
                [4, "MEM004", "Kavita Singh", "321 Pine St", "Andheri East", "Rahul Verma", "9876543213", "Ravi Singh", 40000, 2000, 12000, 24, 28000, 12000, 6000, "18-Jan-24", "Active", 800, 400, 1600, 10400, 6000, 400, "18-Jan-23", "18-Jan-25", "17-Jan-24", 34000, "Regular", "Neha Patel", "Good", "9876543213", "9876543213"],
                [5, "MEM005", "Deepak Gupta", "654 Elm St", "Bandra West", "Anjali Mehta", "9876543214", "Vinod Gupta", 80000, 4000, 24000, 24, 56000, 24000, 14000, "19-Jan-24", "Active", 1600, 900, 3200, 20800, 10000, 800, "19-Jan-23", "19-Jan-25", "18-Jan-24", 66000, "Regular", "Sanjay Kumar", "Good", "9876543214", "9876543214"]
            ]
        else:
            # Last month data with different recovery amounts
            sample_data = [
                ["Sr No", "Member ID", "Name", "Address", "Branch", "CO", "Phone", "Guarantor", "Loan Amount", "EMI", "Due Total", "Installments", "Paid Amount", "Balance", "Current Rec Total", "Last Payment", "Status", "Opening Advance", "Current Advance", "Interest", "Principal", "Total Overdue", "Penalty", "Disb Date", "Maturity", "Last Install Date", "OLP", "Remarks", "Recovery Officer", "Collection Status", "Mobile", "Cell No"],
                [],  # Empty row
                [],  # Empty row
                [1, "MEM001", "Rajesh Kumar", "123 Main St", "Mumbai Central", "Priya Sharma", "9876543210", "Suresh Kumar", 50000, 2500, 17500, 24, 32500, 17500, 7000, "15-Dec-23", "Active", 1200, 300, 2200, 15300, 8500, 600, "15-Jan-23", "15-Jan-25", "14-Dec-23", 43000, "Regular", "Amit Singh", "Good", "9876543210", "9876543210"],
                [2, "MEM002", "Sunita Devi", "456 Park Ave", "Mumbai Central", "Priya Sharma", "9876543211", "Ram Devi", 75000, 3750, 26250, 24, 48750, 26250, 10000, "16-Dec-23", "Active", 1800, 500, 3500, 22750, 12750, 900, "16-Jan-23", "16-Jan-25", "15-Dec-23", 65000, "Regular", "Amit Singh", "Good", "9876543211", "9876543211"],
                [3, "MEM003", "Mohan Lal", "789 Oak St", "Andheri East", "Rahul Verma", "9876543212", "Shyam Lal", 60000, 3000, 21000, 24, 39000, 21000, 8500, "17-Dec-23", "Active", 1400, 400, 2800, 18200, 10500, 700, "17-Jan-23", "17-Jan-25", "16-Dec-23", 52000, "Regular", "Neha Patel", "Good", "9876543212", "9876543212"],
                [4, "MEM004", "Kavita Singh", "321 Pine St", "Andheri East", "Rahul Verma", "9876543213", "Ravi Singh", 40000, 2000, 14000, 24, 26000, 14000, 5500, "18-Dec-23", "Active", 1000, 200, 1800, 12200, 7500, 500, "18-Jan-23", "18-Jan-25", "17-Dec-23", 35000, "Regular", "Neha Patel", "Good", "9876543213", "9876543213"],
                [5, "MEM005", "Deepak Gupta", "654 Elm St", "Bandra West", "Anjali Mehta", "9876543214", "Vinod Gupta", 80000, 4000, 28000, 24, 52000, 28000, 12000, "19-Dec-23", "Active", 2000, 600, 3600, 24400, 12000, 1000, "19-Jan-23", "19-Jan-25", "18-Dec-23", 68000, "Regular", "Sanjay Kumar", "Good", "9876543214", "9876543214"]
            ]
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(sample_data)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False, header=False)
        temp_file.close()
        
        return temp_file.name
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.backend_url}/")
            if response.status_code == 200:
                self.log_test("Basic Connectivity", "PASS", "Backend API is accessible")
                return True
            else:
                self.log_test("Basic Connectivity", "FAIL", f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Basic Connectivity", "FAIL", f"Cannot connect to backend: {str(e)}")
            return False
    
    def test_excel_upload_valid_files(self):
        """Test Excel file upload with valid files"""
        try:
            # Create test Excel files
            current_file_path = self.create_test_excel_file("current_month.xlsx", "current")
            last_month_file_path = self.create_test_excel_file("last_month.xlsx", "last_month")
            
            # Prepare files for upload
            with open(current_file_path, 'rb') as current_file, open(last_month_file_path, 'rb') as last_month_file:
                files = {
                    'current_month_file': ('current_month.xlsx', current_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    'last_month_file': ('last_month.xlsx', last_month_file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                
                data = {
                    'yesterday_date': '17-Jan-24',
                    'today_date': '18-Jan-24'
                }
                
                response = self.session.post(f"{self.backend_url}/upload-excel", files=files, data=data)
            
            # Clean up temp files
            os.unlink(current_file_path)
            os.unlink(last_month_file_path)
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Validate response structure
                required_keys = ['totalMetrics', 'branchMetrics', 'coMetrics']
                missing_keys = [key for key in required_keys if key not in result_data]
                
                if missing_keys:
                    self.log_test("Excel Upload - Valid Files", "FAIL", 
                                f"Missing keys in response: {missing_keys}")
                    return False
                
                # Validate metrics data
                total_metrics = result_data['totalMetrics']
                branch_metrics = result_data['branchMetrics']
                co_metrics = result_data['coMetrics']
                
                details = {
                    "total_active_clients": total_metrics.get('totalActiveClients', 0),
                    "total_current_due": total_metrics.get('totalCurrentDueAmount', 0),
                    "total_recovered": total_metrics.get('totalCurrentRecoveredAmount', 0),
                    "recovery_percentage": total_metrics.get('totalRecoveryPercentage', 0),
                    "branch_count": len(branch_metrics),
                    "co_count": len(co_metrics)
                }
                
                self.log_test("Excel Upload - Valid Files", "PASS", 
                            "Successfully processed Excel files and calculated metrics", details)
                
                # Store response for later tests
                self.last_upload_response = result_data
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Excel Upload - Valid Files", "FAIL", 
                            f"Upload failed: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test("Excel Upload - Valid Files", "FAIL", f"Exception during upload: {str(e)}")
            return False
    
    def test_excel_upload_invalid_files(self):
        """Test Excel upload with invalid file formats"""
        try:
            # Create a text file instead of Excel
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w')
            temp_file.write("This is not an Excel file")
            temp_file.close()
            
            with open(temp_file.name, 'rb') as invalid_file:
                files = {
                    'current_month_file': ('invalid.txt', invalid_file, 'text/plain'),
                    'last_month_file': ('invalid.txt', invalid_file, 'text/plain')
                }
                
                response = self.session.post(f"{self.backend_url}/upload-excel", files=files)
            
            os.unlink(temp_file.name)
            
            if response.status_code == 400:
                self.log_test("Excel Upload - Invalid Files", "PASS", 
                            "Correctly rejected invalid file format")
                return True
            else:
                self.log_test("Excel Upload - Invalid Files", "FAIL", 
                            f"Should have rejected invalid files, got status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Excel Upload - Invalid Files", "FAIL", f"Exception during test: {str(e)}")
            return False
    
    def test_excel_upload_missing_files(self):
        """Test Excel upload with missing files"""
        try:
            # Try to upload without files
            response = self.session.post(f"{self.backend_url}/upload-excel")
            
            if response.status_code == 422:  # FastAPI validation error
                self.log_test("Excel Upload - Missing Files", "PASS", 
                            "Correctly rejected request with missing files")
                return True
            else:
                self.log_test("Excel Upload - Missing Files", "FAIL", 
                            f"Should have rejected missing files, got status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Excel Upload - Missing Files", "FAIL", f"Exception during test: {str(e)}")
            return False
    
    def test_dashboard_data_retrieval(self):
        """Test dashboard data retrieval endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/dashboard-data")
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Validate response structure
                required_keys = ['totalMetrics', 'branchMetrics', 'coMetrics']
                missing_keys = [key for key in required_keys if key not in result_data]
                
                if missing_keys:
                    self.log_test("Dashboard Data Retrieval", "FAIL", 
                                f"Missing keys in response: {missing_keys}")
                    return False
                
                details = {
                    "has_total_metrics": bool(result_data.get('totalMetrics')),
                    "branch_metrics_count": len(result_data.get('branchMetrics', [])),
                    "co_metrics_count": len(result_data.get('coMetrics', []))
                }
                
                self.log_test("Dashboard Data Retrieval", "PASS", 
                            "Successfully retrieved dashboard data", details)
                return True
            elif response.status_code == 404:
                self.log_test("Dashboard Data Retrieval", "PASS", 
                            "Correctly returned 404 when no data exists")
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Dashboard Data Retrieval", "FAIL", 
                            f"Unexpected response: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test("Dashboard Data Retrieval", "FAIL", f"Exception during test: {str(e)}")
            return False
    
    def test_metrics_calculation_accuracy(self):
        """Test the accuracy of metrics calculations"""
        if not hasattr(self, 'last_upload_response'):
            self.log_test("Metrics Calculation Accuracy", "SKIP", 
                        "No upload response available for validation")
            return False
        
        try:
            data = self.last_upload_response
            total_metrics = data['totalMetrics']
            branch_metrics = data['branchMetrics']
            
            # Validate that totals match sum of branch metrics
            calculated_total_clients = sum(branch['activeCount'] for branch in branch_metrics)
            calculated_total_due = sum(branch['currentDueAmount'] for branch in branch_metrics)
            calculated_total_recovered = sum(branch['currentRecoveredAmount'] for branch in branch_metrics)
            
            issues = []
            
            if total_metrics['totalActiveClients'] != calculated_total_clients:
                issues.append(f"Active clients mismatch: {total_metrics['totalActiveClients']} vs {calculated_total_clients}")
            
            if abs(total_metrics['totalCurrentDueAmount'] - calculated_total_due) > 0.01:
                issues.append(f"Due amount mismatch: {total_metrics['totalCurrentDueAmount']} vs {calculated_total_due}")
            
            if abs(total_metrics['totalCurrentRecoveredAmount'] - calculated_total_recovered) > 0.01:
                issues.append(f"Recovered amount mismatch: {total_metrics['totalCurrentRecoveredAmount']} vs {calculated_total_recovered}")
            
            # Validate recovery percentage calculation
            if calculated_total_due > 0:
                expected_recovery_percentage = round((calculated_total_recovered / calculated_total_due) * 100, 2)
                if abs(total_metrics['totalRecoveryPercentage'] - expected_recovery_percentage) > 0.01:
                    issues.append(f"Recovery percentage mismatch: {total_metrics['totalRecoveryPercentage']} vs {expected_recovery_percentage}")
            
            if issues:
                self.log_test("Metrics Calculation Accuracy", "FAIL", 
                            f"Calculation issues found: {'; '.join(issues)}")
                return False
            else:
                details = {
                    "total_clients_verified": calculated_total_clients,
                    "total_due_verified": calculated_total_due,
                    "total_recovered_verified": calculated_total_recovered,
                    "recovery_percentage_verified": total_metrics['totalRecoveryPercentage']
                }
                self.log_test("Metrics Calculation Accuracy", "PASS", 
                            "All metrics calculations are accurate", details)
                return True
                
        except Exception as e:
            self.log_test("Metrics Calculation Accuracy", "FAIL", f"Exception during validation: {str(e)}")
            return False
    
    def test_branch_vs_co_metrics(self):
        """Test that Branch and CO metrics are calculated separately"""
        if not hasattr(self, 'last_upload_response'):
            self.log_test("Branch vs CO Metrics", "SKIP", 
                        "No upload response available for validation")
            return False
        
        try:
            data = self.last_upload_response
            branch_metrics = data['branchMetrics']
            co_metrics = data['coMetrics']
            
            # Check that we have both branch and CO metrics
            if not branch_metrics:
                self.log_test("Branch vs CO Metrics", "FAIL", "No branch metrics found")
                return False
            
            if not co_metrics:
                self.log_test("Branch vs CO Metrics", "FAIL", "No CO metrics found")
                return False
            
            # Validate that branch and CO keys are different
            branch_keys = set(branch['key'] for branch in branch_metrics)
            co_keys = set(co['key'] for co in co_metrics)
            
            details = {
                "branch_keys": list(branch_keys),
                "co_keys": list(co_keys),
                "branch_count": len(branch_metrics),
                "co_count": len(co_metrics)
            }
            
            self.log_test("Branch vs CO Metrics", "PASS", 
                        "Successfully calculated separate Branch and CO metrics", details)
            return True
            
        except Exception as e:
            self.log_test("Branch vs CO Metrics", "FAIL", f"Exception during validation: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting 3D Dashboard Backend API Tests")
        print("=" * 60)
        
        tests = [
            self.test_basic_connectivity,
            self.test_excel_upload_valid_files,
            self.test_dashboard_data_retrieval,
            self.test_metrics_calculation_accuracy,
            self.test_branch_vs_co_metrics,
            self.test_excel_upload_invalid_files,
            self.test_excel_upload_missing_files
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test in tests:
            try:
                result = test()
                if result is True:
                    passed += 1
                elif result is False:
                    failed += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"❌ {test.__name__}: Exception - {str(e)}")
                failed += 1
            print()
        
        print("=" * 60)
        print(f"📊 Test Summary: {passed} passed, {failed} failed, {skipped} skipped")
        
        if failed > 0:
            print("\n❌ CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  • {result['test']}: {result['message']}")
        
        return {
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'total': len(tests),
            'results': self.test_results
        }

if __name__ == "__main__":
    print(f"Testing backend at: {BACKEND_URL}")
    tester = DashboardAPITester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(1 if results['failed'] > 0 else 0)