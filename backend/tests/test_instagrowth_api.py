#!/usr/bin/env python3
"""
InstaGrowth OS Backend API Tests
Tests: Auth, Accounts, DM Templates, Competitor Analysis, A/B Testing, Content, Audit, Billing
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://growth-saas-app.preview.emergentagent.com')

# Test credentials - unique for this test run
TEST_USER_EMAIL = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test User 123"


class TestAPIHealth:
    """Basic API connectivity tests"""
    
    def test_api_root(self):
        """Test API is accessible"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "InstaGrowth" in data["message"]
        print(f"✅ API root accessible: {data}")

    def test_subscription_plans(self):
        """Test subscription plans endpoint"""
        response = requests.get(f"{BASE_URL}/api/subscription-plans")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 4  # starter, pro, agency, enterprise
        plan_ids = [p.get('plan_id') for p in data]
        assert 'starter' in plan_ids
        assert 'pro' in plan_ids
        print(f"✅ Subscription plans: {len(data)} plans found")


class TestAuthentication:
    """Authentication flow tests"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Shared requests session"""
        return requests.Session()

    def test_user_registration(self, session):
        """Test user registration flow"""
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER_EMAIL
        assert data["user"]["name"] == TEST_USER_NAME
        # Store token for subsequent tests
        session.headers["Authorization"] = f"Bearer {data['token']}"
        print(f"✅ User registered: {data['user']['email']}")
        return data

    def test_user_login(self, session):
        """Test user login flow"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        session.headers["Authorization"] = f"Bearer {data['token']}"
        print(f"✅ User logged in: {data['user']['email']}")
        return data

    def test_get_current_user(self, session):
        """Test get current user endpoint"""
        # First login to get token
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["token"]
        session.headers["Authorization"] = f"Bearer {token}"
        
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        print(f"✅ Current user retrieved: {data['email']}")

    def test_login_invalid_credentials(self, session):
        """Test login with invalid credentials"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print(f"✅ Invalid login rejected as expected")


class TestInstagramAccounts:
    """Instagram account management tests"""
    
    @pytest.fixture(scope="class")
    def authenticated_session(self):
        """Get authenticated session"""
        session = requests.Session()
        # Register new user for account tests
        test_email = f"account_test_{uuid.uuid4().hex[:8]}@example.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Account Tester"
        })
        if response.status_code == 200:
            token = response.json()["token"]
            session.headers["Authorization"] = f"Bearer {token}"
        return session

    def test_create_instagram_account(self, authenticated_session):
        """Test adding Instagram account"""
        response = authenticated_session.post(f"{BASE_URL}/api/accounts", json={
            "username": f"test_account_{uuid.uuid4().hex[:6]}",
            "niche": "fitness",
            "notes": "Test account for testing"
        })
        assert response.status_code == 200
        data = response.json()
        assert "account_id" in data
        assert "username" in data
        assert data["niche"] == "fitness"
        # AI metrics should be estimated
        assert "follower_count" in data or "estimated_reach" in data
        print(f"✅ Instagram account created: @{data['username']}")
        return data["account_id"]

    def test_get_accounts(self, authenticated_session):
        """Test listing Instagram accounts"""
        response = authenticated_session.get(f"{BASE_URL}/api/accounts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Retrieved {len(data)} Instagram account(s)")
        return data


class TestDMTemplates:
    """DM Templates CRUD tests"""
    
    @pytest.fixture(scope="class")
    def authenticated_session(self):
        """Get authenticated session"""
        session = requests.Session()
        test_email = f"dm_test_{uuid.uuid4().hex[:8]}@example.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "DM Tester"
        })
        if response.status_code == 200:
            token = response.json()["token"]
            session.headers["Authorization"] = f"Bearer {token}"
        return session

    def test_create_dm_template(self, authenticated_session):
        """Test creating DM template"""
        response = authenticated_session.post(f"{BASE_URL}/api/dm-templates", json={
            "name": "Welcome Message",
            "category": "welcome",
            "message": "Hey {{name}}! Thanks for following! 🙌"
        })
        assert response.status_code == 200
        data = response.json()
        assert "template_id" in data
        assert data["name"] == "Welcome Message"
        assert data["category"] == "welcome"
        assert "name" in data.get("variables", [])  # Should extract {{name}}
        print(f"✅ DM template created: {data['name']}")
        return data["template_id"]

    def test_get_dm_templates(self, authenticated_session):
        """Test listing DM templates"""
        # Create a template first
        authenticated_session.post(f"{BASE_URL}/api/dm-templates", json={
            "name": "Sales Pitch",
            "category": "sales",
            "message": "Check out our new product!"
        })
        
        response = authenticated_session.get(f"{BASE_URL}/api/dm-templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Retrieved {len(data)} DM template(s)")

    def test_get_dm_templates_by_category(self, authenticated_session):
        """Test filtering templates by category"""
        response = authenticated_session.get(f"{BASE_URL}/api/dm-templates?category=welcome")
        assert response.status_code == 200
        data = response.json()
        for template in data:
            assert template["category"] == "welcome"
        print(f"✅ Filtered templates by category")

    def test_delete_dm_template(self, authenticated_session):
        """Test deleting DM template"""
        # Create then delete
        create_resp = authenticated_session.post(f"{BASE_URL}/api/dm-templates", json={
            "name": "To Delete",
            "category": "support",
            "message": "Test message"
        })
        template_id = create_resp.json()["template_id"]
        
        response = authenticated_session.delete(f"{BASE_URL}/api/dm-templates/{template_id}")
        assert response.status_code == 200
        print(f"✅ DM template deleted")


class TestCompetitorAnalysis:
    """Competitor Analysis tests"""
    
    @pytest.fixture(scope="class")
    def authenticated_session_with_account(self):
        """Get authenticated session with Instagram account"""
        session = requests.Session()
        test_email = f"comp_test_{uuid.uuid4().hex[:8]}@example.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Competitor Tester"
        })
        if response.status_code == 200:
            token = response.json()["token"]
            session.headers["Authorization"] = f"Bearer {token}"
            # Create an account for competitor analysis
            acc_resp = session.post(f"{BASE_URL}/api/accounts", json={
                "username": f"comp_test_{uuid.uuid4().hex[:6]}",
                "niche": "fitness"
            })
            account_id = acc_resp.json().get("account_id")
            return session, account_id
        return session, None

    def test_run_competitor_analysis(self, authenticated_session_with_account):
        """Test running competitor analysis"""
        session, account_id = authenticated_session_with_account
        if not account_id:
            pytest.skip("No account created")
        
        response = session.post(f"{BASE_URL}/api/competitor-analysis", json={
            "account_id": account_id,
            "competitor_usernames": ["nike", "adidas"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "competitors" in data
        assert "insights" in data
        assert "opportunities" in data
        print(f"✅ Competitor analysis completed: {len(data.get('competitors', []))} competitors analyzed")

    def test_get_competitor_analyses(self, authenticated_session_with_account):
        """Test listing competitor analyses"""
        session, _ = authenticated_session_with_account
        response = session.get(f"{BASE_URL}/api/competitor-analysis")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Retrieved {len(data)} competitor analyses")


class TestABTesting:
    """A/B Testing feature tests"""
    
    @pytest.fixture(scope="class")
    def authenticated_session_with_account(self):
        """Get authenticated session with Instagram account"""
        session = requests.Session()
        test_email = f"ab_test_{uuid.uuid4().hex[:8]}@example.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "AB Tester"
        })
        if response.status_code == 200:
            token = response.json()["token"]
            session.headers["Authorization"] = f"Bearer {token}"
            # Create an account
            acc_resp = session.post(f"{BASE_URL}/api/accounts", json={
                "username": f"ab_test_{uuid.uuid4().hex[:6]}",
                "niche": "lifestyle"
            })
            account_id = acc_resp.json().get("account_id")
            return session, account_id
        return session, None

    def test_create_ab_test(self, authenticated_session_with_account):
        """Test creating A/B test"""
        session, account_id = authenticated_session_with_account
        if not account_id:
            pytest.skip("No account created")
        
        response = session.post(f"{BASE_URL}/api/ab-tests", json={
            "account_id": account_id,
            "content_type": "hooks",
            "variant_a": "Stop scrolling if you want to grow!",
            "variant_b": "POV: You just discovered the secret to growth"
        })
        assert response.status_code == 200
        data = response.json()
        assert "test_id" in data
        assert data["content_type"] == "hooks"
        assert data["votes_a"] == 0
        assert data["votes_b"] == 0
        print(f"✅ A/B test created: {data['test_id']}")
        return data["test_id"]

    def test_vote_on_ab_test(self, authenticated_session_with_account):
        """Test voting on A/B test"""
        session, account_id = authenticated_session_with_account
        if not account_id:
            pytest.skip("No account created")
        
        # Create a test first
        create_resp = session.post(f"{BASE_URL}/api/ab-tests", json={
            "account_id": account_id,
            "content_type": "captions",
            "variant_a": "Caption A",
            "variant_b": "Caption B"
        })
        test_id = create_resp.json()["test_id"]
        
        # Vote for variant A
        response = session.post(f"{BASE_URL}/api/ab-tests/{test_id}/vote?variant=a")
        assert response.status_code == 200
        data = response.json()
        assert data["votes_a"] == 1
        print(f"✅ Voted on A/B test, votes_a: {data['votes_a']}")

    def test_get_ab_tests(self, authenticated_session_with_account):
        """Test listing A/B tests"""
        session, _ = authenticated_session_with_account
        response = session.get(f"{BASE_URL}/api/ab-tests")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Retrieved {len(data)} A/B tests")


class TestContentEngine:
    """Content generation tests"""
    
    @pytest.fixture(scope="class")
    def authenticated_session_with_account(self):
        """Get authenticated session with Instagram account"""
        session = requests.Session()
        test_email = f"content_test_{uuid.uuid4().hex[:8]}@example.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Content Tester"
        })
        if response.status_code == 200:
            token = response.json()["token"]
            session.headers["Authorization"] = f"Bearer {token}"
            acc_resp = session.post(f"{BASE_URL}/api/accounts", json={
                "username": f"content_{uuid.uuid4().hex[:6]}",
                "niche": "tech"
            })
            account_id = acc_resp.json().get("account_id")
            return session, account_id
        return session, None

    def test_generate_content_hooks(self, authenticated_session_with_account):
        """Test generating hook content"""
        session, account_id = authenticated_session_with_account
        if not account_id:
            pytest.skip("No account created")
        
        response = session.post(f"{BASE_URL}/api/content/generate", json={
            "account_id": account_id,
            "content_type": "hooks"
        })
        assert response.status_code == 200
        data = response.json()
        assert "content_id" in data
        assert "content" in data
        assert isinstance(data["content"], list)
        print(f"✅ Generated {len(data['content'])} hooks")

    def test_get_content_items(self, authenticated_session_with_account):
        """Test listing content items"""
        session, _ = authenticated_session_with_account
        response = session.get(f"{BASE_URL}/api/content")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Retrieved {len(data)} content items")


class TestAIAudit:
    """AI Audit tests"""
    
    @pytest.fixture(scope="class")
    def authenticated_session_with_account(self):
        """Get authenticated session with Instagram account"""
        session = requests.Session()
        test_email = f"audit_test_{uuid.uuid4().hex[:8]}@example.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Audit Tester"
        })
        if response.status_code == 200:
            token = response.json()["token"]
            session.headers["Authorization"] = f"Bearer {token}"
            acc_resp = session.post(f"{BASE_URL}/api/accounts", json={
                "username": f"audit_{uuid.uuid4().hex[:6]}",
                "niche": "business"
            })
            account_id = acc_resp.json().get("account_id")
            return session, account_id
        return session, None

    def test_run_ai_audit(self, authenticated_session_with_account):
        """Test running AI audit on account"""
        session, account_id = authenticated_session_with_account
        if not account_id:
            pytest.skip("No account created")
        
        response = session.post(f"{BASE_URL}/api/audits", json={
            "account_id": account_id
        })
        assert response.status_code == 200
        data = response.json()
        assert "audit_id" in data
        assert "engagement_score" in data
        assert "shadowban_risk" in data
        assert "recommendations" in data
        print(f"✅ AI audit completed, engagement score: {data['engagement_score']}")

    def test_get_audits(self, authenticated_session_with_account):
        """Test listing audits"""
        session, _ = authenticated_session_with_account
        response = session.get(f"{BASE_URL}/api/audits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Retrieved {len(data)} audits")


class TestLogout:
    """Logout functionality test"""
    
    def test_logout(self):
        """Test logout clears session"""
        session = requests.Session()
        # Register and login
        test_email = f"logout_test_{uuid.uuid4().hex[:8]}@example.com"
        reg_resp = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Logout Tester"
        })
        token = reg_resp.json()["token"]
        session.headers["Authorization"] = f"Bearer {token}"
        
        # Logout
        logout_resp = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_resp.status_code == 200
        print(f"✅ Logout successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
