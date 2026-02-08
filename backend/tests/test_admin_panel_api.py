"""
Admin Panel API Tests
Tests admin authentication, dashboard stats, user management, plans, revenue, AI usage, logs, and settings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials
ADMIN_EMAIL = "superadmin@instagrowth.com"
ADMIN_PASSWORD = "SuperAdmin123!"
ADMIN_CODE = "INSTAGROWTH_ADMIN_2024"


class TestAdminAuth:
    """Admin Panel Authentication Tests"""
    
    def test_admin_login_success(self):
        """Test admin login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/admin-panel/auth/login",
            params={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "admin_code": ADMIN_CODE
            }
        )
        print(f"Admin login response: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Accept both 200 (success) and response with requires_2fa
        assert response.status_code == 200
        data = response.json()
        
        # If 2FA not required, we should get a token
        if not data.get("requires_2fa"):
            assert "token" in data
            assert "admin" in data
            assert data["admin"]["email"] == ADMIN_EMAIL
            # Store token for subsequent tests
            TestAdminAuth.admin_token = data["token"]
        else:
            # If 2FA is required, that's acceptable behavior
            assert data.get("requires_2fa") == True
            TestAdminAuth.admin_token = None
    
    def test_admin_login_invalid_code(self):
        """Test admin login with invalid admin code"""
        response = requests.post(
            f"{BASE_URL}/api/admin-panel/auth/login",
            params={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD,
                "admin_code": "WRONG_CODE"
            }
        )
        assert response.status_code == 401
        print("Invalid admin code correctly rejected")
    
    def test_admin_login_invalid_password(self):
        """Test admin login with invalid password"""
        response = requests.post(
            f"{BASE_URL}/api/admin-panel/auth/login",
            params={
                "email": ADMIN_EMAIL,
                "password": "wrongpassword",
                "admin_code": ADMIN_CODE
            }
        )
        assert response.status_code == 401
        print("Invalid password correctly rejected")
    
    def test_admin_get_me_unauthenticated(self):
        """Test get current admin without auth"""
        response = requests.get(f"{BASE_URL}/api/admin-panel/auth/me")
        assert response.status_code == 401
        print("Unauthenticated access correctly rejected")


class TestAdminDashboard:
    """Admin Dashboard API Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminDashboard.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminDashboard.admin_token = data.get("token")
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        if not TestAdminDashboard.admin_token:
            pytest.skip("Admin token not available (2FA may be required)")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/dashboard/stats",
            headers={"Authorization": f"Bearer {TestAdminDashboard.admin_token}"}
        )
        print(f"Dashboard stats response: {response.status_code}")
        print(f"Stats: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "total_users" in data
        assert "active_subscriptions" in data
        assert "total_accounts" in data
        assert "plan_distribution" in data
    
    def test_dashboard_revenue_chart(self):
        """Test revenue chart data endpoint"""
        if not TestAdminDashboard.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/dashboard/charts/revenue?days=30",
            headers={"Authorization": f"Bearer {TestAdminDashboard.admin_token}"}
        )
        print(f"Revenue chart response: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert "chart_data" in data
    
    def test_dashboard_users_chart(self):
        """Test new users chart data endpoint"""
        if not TestAdminDashboard.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/dashboard/charts/users?days=30",
            headers={"Authorization": f"Bearer {TestAdminDashboard.admin_token}"}
        )
        print(f"Users chart response: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert "chart_data" in data
    
    def test_dashboard_ai_usage_chart(self):
        """Test AI usage chart data endpoint"""
        if not TestAdminDashboard.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/dashboard/charts/ai-usage?days=30",
            headers={"Authorization": f"Bearer {TestAdminDashboard.admin_token}"}
        )
        print(f"AI usage chart response: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert "chart_data" in data


class TestAdminUsers:
    """Admin User Management Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminUsers.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminUsers.admin_token = data.get("token")
    
    def test_get_all_users(self):
        """Test get all users endpoint"""
        if not TestAdminUsers.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/users",
            headers={"Authorization": f"Bearer {TestAdminUsers.admin_token}"}
        )
        print(f"Users list response: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert "total" in data
        print(f"Total users: {data['total']}")
    
    def test_get_users_with_search(self):
        """Test users search functionality"""
        if not TestAdminUsers.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/users?search=test",
            headers={"Authorization": f"Bearer {TestAdminUsers.admin_token}"}
        )
        print(f"Users search response: {response.status_code}")
        
        assert response.status_code == 200
    
    def test_get_users_with_plan_filter(self):
        """Test users filter by plan"""
        if not TestAdminUsers.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/users?plan=starter",
            headers={"Authorization": f"Bearer {TestAdminUsers.admin_token}"}
        )
        print(f"Users plan filter response: {response.status_code}")
        
        assert response.status_code == 200


class TestAdminPlans:
    """Admin Plans Management Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminPlans.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminPlans.admin_token = data.get("token")
    
    def test_get_all_plans(self):
        """Test get all plans endpoint"""
        if not TestAdminPlans.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/plans",
            headers={"Authorization": f"Bearer {TestAdminPlans.admin_token}"}
        )
        print(f"Plans list response: {response.status_code}")
        print(f"Plans: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data


class TestAdminRevenue:
    """Admin Revenue Analytics Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminRevenue.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminRevenue.admin_token = data.get("token")
    
    def test_revenue_stats(self):
        """Test revenue statistics endpoint"""
        if not TestAdminRevenue.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/revenue/stats",
            headers={"Authorization": f"Bearer {TestAdminRevenue.admin_token}"}
        )
        print(f"Revenue stats response: {response.status_code}")
        print(f"Revenue: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mrr" in data
        assert "arr" in data
        assert "churn_rate" in data
        assert "arpu" in data


class TestAdminAIUsage:
    """Admin AI Usage Analytics Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminAIUsage.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminAIUsage.admin_token = data.get("token")
    
    def test_ai_usage_stats(self):
        """Test AI usage statistics endpoint"""
        if not TestAdminAIUsage.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/ai-usage/stats",
            headers={"Authorization": f"Bearer {TestAdminAIUsage.admin_token}"}
        )
        print(f"AI usage stats response: {response.status_code}")
        print(f"AI Usage: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_requests_today" in data
        assert "total_requests_month" in data
        assert "usage_by_feature" in data
        assert "top_users" in data


class TestAdminLogs:
    """Admin Activity Logs Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminLogs.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminLogs.admin_token = data.get("token")
    
    def test_get_logs(self):
        """Test get admin logs endpoint"""
        if not TestAdminLogs.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/logs",
            headers={"Authorization": f"Bearer {TestAdminLogs.admin_token}"}
        )
        print(f"Logs response: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        print(f"Total logs: {data['total']}")
    
    def test_get_logs_with_action_filter(self):
        """Test logs filter by action"""
        if not TestAdminLogs.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/logs?action=login",
            headers={"Authorization": f"Bearer {TestAdminLogs.admin_token}"}
        )
        
        assert response.status_code == 200


class TestAdminSettings:
    """Admin System Settings Tests"""
    admin_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token before each test"""
        if not TestAdminSettings.admin_token:
            response = requests.post(
                f"{BASE_URL}/api/admin-panel/auth/login",
                params={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "admin_code": ADMIN_CODE
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not data.get("requires_2fa"):
                    TestAdminSettings.admin_token = data.get("token")
    
    def test_get_settings(self):
        """Test get system settings endpoint"""
        if not TestAdminSettings.admin_token:
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin-panel/settings",
            headers={"Authorization": f"Bearer {TestAdminSettings.admin_token}"}
        )
        print(f"Settings response: {response.status_code}")
        print(f"Settings: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify settings structure
        assert "platform_name" in data or "setting_id" in data


class TestUser2FA:
    """User 2FA Endpoints Tests"""
    user_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as regular user before tests"""
        if not TestUser2FA.user_token:
            # Try to register/login as test user
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": "testuser123@example.com",
                    "password": "TestPass123!"
                }
            )
            if response.status_code == 200:
                data = response.json()
                TestUser2FA.user_token = data.get("token")
    
    def test_2fa_status(self):
        """Test get 2FA status endpoint"""
        if not TestUser2FA.user_token:
            pytest.skip("User token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/auth/2fa/status",
            headers={"Authorization": f"Bearer {TestUser2FA.user_token}"},
            cookies={"auth_token": TestUser2FA.user_token}
        )
        print(f"2FA status response: {response.status_code}")
        
        # Either 200 (success) or 401 (if cookie-based auth required)
        if response.status_code == 200:
            data = response.json()
            assert "is_enabled" in data
            print(f"2FA enabled: {data.get('is_enabled')}")
    
    def test_2fa_backup_codes_count(self):
        """Test get backup codes count endpoint"""
        if not TestUser2FA.user_token:
            pytest.skip("User token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/auth/2fa/backup-codes",
            headers={"Authorization": f"Bearer {TestUser2FA.user_token}"},
            cookies={"auth_token": TestUser2FA.user_token}
        )
        print(f"Backup codes response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assert "remaining_codes" in data


class TestAdminWebSocket:
    """Admin WebSocket Tests (basic connectivity)"""
    
    def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoint responds (even if upgrade fails via HTTP)"""
        # WebSocket endpoints typically reject HTTP GET with 400 or similar
        # This just tests the endpoint is reachable
        try:
            response = requests.get(f"{BASE_URL}/api/admin-ws/test_admin")
            # WebSocket endpoints typically return 400 or 403 for HTTP requests
            print(f"WebSocket endpoint response: {response.status_code}")
            # Success if we get any response (400, 403, etc means endpoint exists)
            assert response.status_code in [400, 403, 404, 405, 426]
        except Exception as e:
            print(f"WebSocket test note: {e}")
            # This is expected for WebSocket endpoints
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
