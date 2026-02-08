#!/usr/bin/env python3
"""
InstaGrowth OS Backend API Testing
Tests all backend endpoints and functionality
"""

import requests
import json
import sys
from datetime import datetime
import time

class InstaGrowthAPITester:
    def __init__(self, base_url="https://instagrowth-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user = None
        self.test_account_id = None
        self.test_audit_id = None
        self.test_content_id = None
        self.test_plan_id = None
        
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        
        # Test credentials
        self.test_email = f"test_user_{int(time.time())}@example.com"
        self.test_password = "TestPassword123!"
        self.test_name = "Test User"

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status=200, data=None, headers=None, critical=False):
        """Run a single API test"""
        url = f"{self.base_url}/api{endpoint}"
        test_headers = {"Content-Type": "application/json"}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers["Authorization"] = f"Bearer {self.token}"

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                if critical:
                    self.critical_failures.append(f"{name}: {response.status_code} - {response.text[:200]}")
                try:
                    error_detail = response.json().get("detail", response.text[:200])
                    self.log(f"   Error: {error_detail}", "ERROR")
                except:
                    self.log(f"   Response: {response.text[:200]}", "ERROR")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}", "ERROR")
            if critical:
                self.critical_failures.append(f"{name}: Exception - {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic API connectivity"""
        success, response = self.run_test("API Health Check", "GET", "/", 200, critical=True)
        return success

    def test_auth_register(self):
        """Test user registration"""
        data = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password
        }
        success, response = self.run_test("User Registration", "POST", "/auth/register", 200, data, critical=True)
        if success and "token" in response:
            self.token = response["token"]
            self.user = response["user"]
            self.log(f"   Registered user: {self.user.get('email', 'Unknown')}")
        return success

    def test_auth_login(self):
        """Test user login"""
        data = {
            "email": self.test_email,
            "password": self.test_password
        }
        success, response = self.run_test("User Login", "POST", "/auth/login", 200, data, critical=True)
        if success and "token" in response:
            # Use the login token instead
            self.token = response["token"]
            self.user = response["user"]
            self.log(f"   Logged in user: {self.user.get('email', 'Unknown')}")
        return success

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test("Get Current User", "GET", "/auth/me", 200, critical=True)
        if success:
            self.user = response
        return success

    def test_plans_list(self):
        """Test get subscription plans"""
        success, response = self.run_test("Get Subscription Plans", "GET", "/plans", 200)
        if success:
            plans = response if isinstance(response, list) else []
            self.log(f"   Found {len(plans)} subscription plans")
        return success

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        success, response = self.run_test("Dashboard Statistics", "GET", "/dashboard/stats", 200)
        if success:
            stats = response if isinstance(response, dict) else {}
            self.log(f"   Accounts: {stats.get('accounts_count', 0)}")
            self.log(f"   AI Usage: {stats.get('ai_usage', {}).get('current', 0)}/{stats.get('ai_usage', {}).get('limit', 0)}")
        return success

    def test_create_instagram_account(self):
        """Test creating an Instagram account"""
        data = {
            "username": f"test_account_{int(time.time())}",
            "niche": "Tech & Gadgets",
            "notes": "Test account for API testing"
        }
        success, response = self.run_test("Create Instagram Account", "POST", "/accounts", 200, data)
        if success and "account_id" in response:
            self.test_account_id = response["account_id"]
            self.log(f"   Created account: @{response.get('username')} ({self.test_account_id})")
        return success

    def test_list_accounts(self):
        """Test listing Instagram accounts"""
        success, response = self.run_test("List Instagram Accounts", "GET", "/accounts", 200)
        if success:
            accounts = response if isinstance(response, list) else []
            self.log(f"   Found {len(accounts)} accounts")
        return success

    def test_get_account(self):
        """Test getting a specific Instagram account"""
        if not self.test_account_id:
            self.log("⚠️ Skipping Get Account - No test account created")
            return True
        
        success, response = self.run_test("Get Instagram Account", "GET", f"/accounts/{self.test_account_id}", 200)
        return success

    def test_update_account(self):
        """Test updating an Instagram account"""
        if not self.test_account_id:
            self.log("⚠️ Skipping Update Account - No test account created")
            return True
        
        data = {"notes": "Updated notes for testing"}
        success, response = self.run_test("Update Instagram Account", "PUT", f"/accounts/{self.test_account_id}", 200, data)
        return success

    def test_create_audit(self):
        """Test creating an AI audit"""
        if not self.test_account_id:
            self.log("⚠️ Skipping AI Audit - No test account created")
            return True
        
        data = {"account_id": self.test_account_id}
        # AI generation might take longer
        success, response = self.run_test("Create AI Audit", "POST", "/audits", 200, data)
        if success and "audit_id" in response:
            self.test_audit_id = response["audit_id"]
            self.log(f"   Created audit: {self.test_audit_id}")
            self.log(f"   Engagement Score: {response.get('engagement_score', 'N/A')}")
            self.log(f"   Shadowban Risk: {response.get('shadowban_risk', 'N/A')}")
        return success

    def test_list_audits(self):
        """Test listing audits"""
        success, response = self.run_test("List Audits", "GET", "/audits", 200)
        if success:
            audits = response if isinstance(response, list) else []
            self.log(f"   Found {len(audits)} audits")
        return success

    def test_get_audit(self):
        """Test getting a specific audit"""
        if not self.test_audit_id:
            self.log("⚠️ Skipping Get Audit - No test audit created")
            return True
        
        success, response = self.run_test("Get Audit", "GET", f"/audits/{self.test_audit_id}", 200)
        return success

    def test_generate_content(self):
        """Test AI content generation"""
        if not self.test_account_id:
            self.log("⚠️ Skipping Content Generation - No test account created")
            return True

        content_types = ["reels", "hooks", "captions", "hashtags"]
        overall_success = True
        
        for content_type in content_types:
            data = {
                "account_id": self.test_account_id,
                "content_type": content_type,
                "topic": "social media growth"
            }
            success, response = self.run_test(f"Generate {content_type.title()}", "POST", "/content/generate", 200, data)
            if success and "content_id" in response:
                if not self.test_content_id:  # Store first successful content ID
                    self.test_content_id = response["content_id"]
                content_items = response.get("content", [])
                self.log(f"   Generated {len(content_items)} {content_type}")
            else:
                overall_success = False
        
        return overall_success

    def test_list_content(self):
        """Test listing generated content"""
        success, response = self.run_test("List Content", "GET", "/content", 200)
        if success:
            content = response if isinstance(response, list) else []
            self.log(f"   Found {len(content)} content items")
        return success

    def test_create_growth_plan(self):
        """Test creating a growth plan"""
        if not self.test_account_id:
            self.log("⚠️ Skipping Growth Plan - No test account created")
            return True

        durations = [7, 14, 30]
        overall_success = True
        
        for duration in durations:
            data = {
                "account_id": self.test_account_id,
                "duration": duration
            }
            success, response = self.run_test(f"Create {duration}-Day Growth Plan", "POST", "/growth-plans", 200, data)
            if success and "plan_id" in response:
                if not self.test_plan_id:  # Store first successful plan ID
                    self.test_plan_id = response["plan_id"]
                tasks = response.get("daily_tasks", [])
                self.log(f"   Generated {len(tasks)} daily tasks")
            else:
                overall_success = False
        
        return overall_success

    def test_list_growth_plans(self):
        """Test listing growth plans"""
        success, response = self.run_test("List Growth Plans", "GET", "/growth-plans", 200)
        if success:
            plans = response if isinstance(response, list) else []
            self.log(f"   Found {len(plans)} growth plans")
        return success

    def test_get_growth_plan(self):
        """Test getting a specific growth plan"""
        if not self.test_plan_id:
            self.log("⚠️ Skipping Get Growth Plan - No test plan created")
            return True
        
        success, response = self.run_test("Get Growth Plan", "GET", f"/growth-plans/{self.test_plan_id}", 200)
        return success

    def test_cleanup(self):
        """Clean up test data"""
        cleanup_success = True
        
        # Delete test account if created
        if self.test_account_id:
            success, _ = self.run_test("Delete Test Account", "DELETE", f"/accounts/{self.test_account_id}", 200)
            cleanup_success = cleanup_success and success
        
        return cleanup_success

    def run_all_tests(self):
        """Run all backend API tests"""
        self.log("="*60)
        self.log("Starting InstaGrowth OS Backend API Tests")
        self.log("="*60)
        
        # Critical tests first
        if not self.test_health_check():
            self.log("❌ CRITICAL: API not accessible", "CRITICAL")
            return False
        
        if not self.test_auth_register():
            self.log("❌ CRITICAL: User registration failed", "CRITICAL")
            return False
        
        if not self.test_auth_me():
            self.log("❌ CRITICAL: Authentication check failed", "CRITICAL")
            return False
        
        # Test all other endpoints
        tests = [
            self.test_auth_login,
            self.test_plans_list,
            self.test_dashboard_stats,
            self.test_create_instagram_account,
            self.test_list_accounts,
            self.test_get_account,
            self.test_update_account,
            self.test_create_audit,
            self.test_list_audits,
            self.test_get_audit,
            self.test_generate_content,
            self.test_list_content,
            self.test_create_growth_plan,
            self.test_list_growth_plans,
            self.test_get_growth_plan,
        ]
        
        for test in tests:
            test()
        
        # Cleanup
        self.test_cleanup()
        
        # Results
        self.log("="*60)
        self.log(f"Backend API Test Results:")
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.critical_failures:
            self.log("CRITICAL FAILURES:")
            for failure in self.critical_failures:
                self.log(f"  - {failure}", "CRITICAL")
            return False
        
        success_rate = (self.tests_passed/self.tests_run)*100
        if success_rate < 70:
            self.log("❌ Too many failures - Backend needs fixes", "ERROR")
            return False
        elif success_rate < 90:
            self.log("⚠️ Some issues found - May need attention", "WARN")
        else:
            self.log("✅ Backend API tests mostly successful", "SUCCESS")
        
        return success_rate >= 70

def main():
    tester = InstaGrowthAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())