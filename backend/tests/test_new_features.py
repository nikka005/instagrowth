"""
Test Suite for New Features:
- Referral/Affiliate System
- AI Credits System
- Announcements System
- Support Ticketing System
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER = {
    "email": "testuser@example.com",
    "password": "TestPassword123!"
}
ADMIN_CREDS = {
    "email": "superadmin@instagrowth.com",
    "password": "SuperAdmin123!",
    "admin_code": "INSTAGROWTH_ADMIN_2024"
}


class TestCreditsAPI:
    """AI Credits system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login before each test"""
        self.session = requests.Session()
        # Login as test user
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code != 200:
            pytest.skip("Test user login failed - user may not exist")
    
    def test_get_credits_costs_public(self):
        """Test /api/credits/costs - public endpoint for feature costs"""
        response = requests.get(f"{BASE_URL}/api/credits/costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "costs" in data
        assert "plan_allocations" in data
        
        # Verify cost structure
        costs = data["costs"]
        assert "audit" in costs
        assert "caption" in costs
        assert "hashtags" in costs
        print(f"Credits costs retrieved: {costs}")
    
    def test_get_user_credits(self):
        """Test /api/credits - get user's credit information"""
        response = self.session.get(f"{BASE_URL}/api/credits")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_credits" in data
        assert "remaining_credits" in data
        assert "used_credits" in data
        print(f"User credits: remaining={data['remaining_credits']}, total={data['total_credits']}")
    
    def test_get_credits_history(self):
        """Test /api/credits/history - get credit usage history"""
        response = self.session.get(f"{BASE_URL}/api/credits/history")
        assert response.status_code == 200
        
        data = response.json()
        assert "history" in data
        print(f"Credit history entries: {len(data['history'])}")


class TestReferralAPI:
    """Referral/Affiliate system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code != 200:
            pytest.skip("Test user login failed")
    
    def test_get_or_create_referral_code(self):
        """Test /api/referrals/code - get or create user's referral code"""
        response = self.session.get(f"{BASE_URL}/api/referrals/code")
        assert response.status_code == 200
        
        data = response.json()
        assert "code" in data
        assert "stats" in data
        assert "rewards" in data
        
        # Verify code format (REF-XXXXXX-XXXX)
        code = data["code"]
        assert code.startswith("REF-")
        print(f"Referral code: {code}")
        
        # Verify stats structure
        stats = data["stats"]
        assert "clicks" in stats
        assert "signups" in stats
        assert "conversions" in stats
    
    def test_get_referral_stats(self):
        """Test /api/referrals/stats - get detailed referral statistics"""
        response = self.session.get(f"{BASE_URL}/api/referrals/stats")
        assert response.status_code == 200
        
        data = response.json()
        # May have stats or message if no referral yet
        if "code" in data:
            assert "overview" in data
            assert "earnings" in data
            print(f"Referral stats: clicks={data['overview']['clicks']}, signups={data['overview']['signups']}")
        else:
            print("No referral code created yet")
    
    def test_track_referral_click(self):
        """Test /api/referrals/track-click - track referral link click"""
        # First get the referral code
        code_resp = self.session.get(f"{BASE_URL}/api/referrals/code")
        assert code_resp.status_code == 200
        code = code_resp.json()["code"]
        
        # Track a click (public endpoint)
        response = requests.post(f"{BASE_URL}/api/referrals/track-click?code={code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("tracked") == True
        print(f"Click tracked for code: {code}")


class TestAnnouncementsAPI:
    """Announcements system tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code != 200:
            pytest.skip("Test user login failed")
    
    def test_get_active_announcements(self):
        """Test /api/announcements - get active announcements"""
        response = self.session.get(f"{BASE_URL}/api/announcements")
        assert response.status_code == 200
        
        data = response.json()
        assert "announcements" in data
        print(f"Active announcements: {len(data['announcements'])}")
    
    def test_get_unread_announcements(self):
        """Test /api/announcements/unread - get unread announcements for user"""
        response = self.session.get(f"{BASE_URL}/api/announcements/unread")
        assert response.status_code == 200
        
        data = response.json()
        assert "announcements" in data
        assert "count" in data
        print(f"Unread announcements: {data['count']}")


class TestSupportTicketsAPI:
    """Support ticketing system tests"""
    
    ticket_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code != 200:
            pytest.skip("Test user login failed")
    
    def test_create_support_ticket(self):
        """Test /api/support/tickets POST - create new support ticket"""
        response = self.session.post(
            f"{BASE_URL}/api/support/tickets",
            params={
                "subject": "TEST_Test ticket for testing",
                "message": "This is a test support ticket message",
                "category": "general",
                "priority": "normal"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "ticket_id" in data
        assert data["subject"] == "TEST_Test ticket for testing"
        assert data["status"] == "open"
        assert "messages" in data
        assert len(data["messages"]) == 1
        
        TestSupportTicketsAPI.ticket_id = data["ticket_id"]
        print(f"Support ticket created: {data['ticket_id']}")
    
    def test_get_user_tickets(self):
        """Test /api/support/tickets GET - get user's tickets"""
        response = self.session.get(f"{BASE_URL}/api/support/tickets")
        assert response.status_code == 200
        
        data = response.json()
        assert "tickets" in data
        print(f"User has {len(data['tickets'])} tickets")
    
    def test_get_specific_ticket(self):
        """Test /api/support/tickets/{ticket_id} - get specific ticket"""
        if not TestSupportTicketsAPI.ticket_id:
            pytest.skip("No ticket created")
        
        response = self.session.get(f"{BASE_URL}/api/support/tickets/{TestSupportTicketsAPI.ticket_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ticket_id"] == TestSupportTicketsAPI.ticket_id
        print(f"Retrieved ticket: {data['ticket_id']}, status: {data['status']}")
    
    def test_reply_to_ticket(self):
        """Test /api/support/tickets/{ticket_id}/reply - add reply to ticket"""
        if not TestSupportTicketsAPI.ticket_id:
            pytest.skip("No ticket created")
        
        response = self.session.post(
            f"{BASE_URL}/api/support/tickets/{TestSupportTicketsAPI.ticket_id}/reply",
            params={"message": "This is a test reply to the ticket"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message_id" in data
        print(f"Reply added: {data['message_id']}")
    
    def test_close_ticket(self):
        """Test /api/support/tickets/{ticket_id}/close - close a ticket"""
        if not TestSupportTicketsAPI.ticket_id:
            pytest.skip("No ticket created")
        
        response = self.session.post(f"{BASE_URL}/api/support/tickets/{TestSupportTicketsAPI.ticket_id}/close")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("message") == "Ticket closed"
        print("Ticket closed successfully")


class TestAdminReferralsAPI:
    """Admin referral management tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Admin login before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/admin-panel/auth/login", json=ADMIN_CREDS)
        if login_resp.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_admin_referral_overview(self):
        """Test /api/referrals/admin/overview - get referral system overview"""
        response = requests.get(f"{BASE_URL}/api/referrals/admin/overview", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_referrals" in data
        assert "converted" in data
        assert "conversion_rate" in data
        assert "config" in data
        print(f"Referral overview: total={data['total_referrals']}, converted={data['converted']}")
    
    def test_admin_get_payouts(self):
        """Test /api/referrals/admin/payouts - get payout requests"""
        response = requests.get(f"{BASE_URL}/api/referrals/admin/payouts", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "payouts" in data
        print(f"Pending payouts: {len(data['payouts'])}")


class TestAdminAnnouncementsAPI:
    """Admin announcements management tests"""
    
    announcement_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Admin login before each test"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/admin-panel/auth/login", json=ADMIN_CREDS)
        if login_resp.status_code != 200:
            pytest.skip("Admin login failed")
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_admin_get_all_announcements(self):
        """Test /api/announcements/admin/all - get all announcements"""
        response = requests.get(f"{BASE_URL}/api/announcements/admin/all", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "announcements" in data
        print(f"Total announcements: {len(data['announcements'])}")
    
    def test_admin_create_announcement(self):
        """Test /api/announcements/admin/create - create new announcement"""
        response = requests.post(
            f"{BASE_URL}/api/announcements/admin/create",
            headers=self.headers,
            params={
                "title": "TEST_Test Announcement",
                "message": "This is a test announcement from automated tests",
                "type": "info",
                "target": "all"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "announcement_id" in data
        assert data["title"] == "TEST_Test Announcement"
        assert data["status"] == "active"
        
        TestAdminAnnouncementsAPI.announcement_id = data["announcement_id"]
        print(f"Announcement created: {data['announcement_id']}")
    
    def test_admin_update_announcement(self):
        """Test /api/announcements/admin/{id} PUT - update announcement"""
        if not TestAdminAnnouncementsAPI.announcement_id:
            pytest.skip("No announcement created")
        
        response = requests.put(
            f"{BASE_URL}/api/announcements/admin/{TestAdminAnnouncementsAPI.announcement_id}",
            headers=self.headers,
            params={"title": "TEST_Updated Announcement"}
        )
        assert response.status_code == 200
        print("Announcement updated successfully")
    
    def test_admin_delete_announcement(self):
        """Test /api/announcements/admin/{id} DELETE - delete announcement"""
        if not TestAdminAnnouncementsAPI.announcement_id:
            pytest.skip("No announcement created")
        
        response = requests.delete(
            f"{BASE_URL}/api/announcements/admin/{TestAdminAnnouncementsAPI.announcement_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        print("Announcement deleted successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
