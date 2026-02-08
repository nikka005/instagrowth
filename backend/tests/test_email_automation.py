"""
Test Suite for Email Automation System:
- Email Templates API (list, get single, toggle enable/disable)
- Email Stats API
- Email Logs API
- Send Test Email API
- Run Scheduled Tasks API
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Admin credentials (required for most email automation endpoints)
ADMIN_CREDS = {
    "email": "superadmin@instagrowth.com",
    "password": "SuperAdmin123!",
    "admin_code": "INSTAGROWTH_ADMIN_2024"
}

# Expected email templates
EXPECTED_TEMPLATES = [
    "welcome", "subscription_activated", "renewal_reminder_7day", 
    "renewal_reminder_3day", "credits_low", "subscription_cancelled",
    "weekly_digest", "inactivity_reminder", "referral_reward"
]


@pytest.fixture(scope="class")
def admin_session():
    """Get authenticated admin session"""
    session = requests.Session()
    login_resp = session.post(
        f"{BASE_URL}/api/admin-panel/auth/login",
        params={
            "email": ADMIN_CREDS["email"],
            "password": ADMIN_CREDS["password"],
            "admin_code": ADMIN_CREDS["admin_code"]
        }
    )
    if login_resp.status_code != 200:
        pytest.skip("Admin login failed")
    
    token = login_resp.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session


class TestEmailTemplatesAPI:
    """Email Templates API tests"""
    
    def test_get_all_templates_public(self):
        """Test /api/email-automation/templates - get all templates (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/email-automation/templates")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "templates" in data, "Response should contain 'templates' key"
        
        templates = data["templates"]
        assert len(templates) == 9, f"Expected 9 templates, got {len(templates)}"
        
        # Verify all expected templates are present
        template_ids = [t["id"] for t in templates]
        for expected_id in EXPECTED_TEMPLATES:
            assert expected_id in template_ids, f"Template {expected_id} not found"
        
        # Verify template structure
        for template in templates:
            assert "id" in template, "Template should have 'id'"
            assert "name" in template, "Template should have 'name'"
            assert "subject" in template, "Template should have 'subject'"
            assert "enabled" in template, "Template should have 'enabled'"
            assert "trigger" in template, "Template should have 'trigger'"
        
        print(f"✓ All 9 email templates retrieved successfully")
        print(f"  Template IDs: {template_ids}")
    
    def test_get_single_template(self):
        """Test /api/email-automation/templates/{template_id} - get single template"""
        response = requests.get(f"{BASE_URL}/api/email-automation/templates/welcome")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == "welcome"
        assert data["name"] == "Welcome Email"
        assert "template_html" in data, "Single template should include template_html"
        assert "<div" in data["template_html"], "Template HTML should contain HTML content"
        
        print(f"✓ Welcome template retrieved with HTML content")
    
    def test_get_invalid_template(self):
        """Test getting non-existent template returns 404"""
        response = requests.get(f"{BASE_URL}/api/email-automation/templates/invalid_template_xyz")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Invalid template properly returns 404")
    
    def test_toggle_template_requires_auth(self):
        """Test /api/email-automation/templates/{id}/toggle - requires admin auth"""
        response = requests.put(
            f"{BASE_URL}/api/email-automation/templates/welcome/toggle",
            params={"enabled": False}
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ Toggle template properly requires authentication")
    
    def test_toggle_template_with_auth(self, admin_session):
        """Test toggling template enabled status with admin auth"""
        # First get current state
        resp1 = requests.get(f"{BASE_URL}/api/email-automation/templates/inactivity_reminder")
        initial_state = resp1.json()["enabled"]
        
        # Toggle to opposite state
        new_state = not initial_state
        toggle_resp = admin_session.put(
            f"{BASE_URL}/api/email-automation/templates/inactivity_reminder/toggle",
            params={"enabled": new_state}
        )
        assert toggle_resp.status_code == 200, f"Expected 200, got {toggle_resp.status_code}"
        
        data = toggle_resp.json()
        assert data["enabled"] == new_state, f"Expected enabled={new_state}, got {data['enabled']}"
        
        # Toggle back to original state
        restore_resp = admin_session.put(
            f"{BASE_URL}/api/email-automation/templates/inactivity_reminder/toggle",
            params={"enabled": initial_state}
        )
        assert restore_resp.status_code == 200
        
        print(f"✓ Template toggle working - changed from {initial_state} to {new_state} and back")


class TestEmailStatsAPI:
    """Email Stats API tests"""
    
    def test_stats_requires_auth(self):
        """Test /api/email-automation/stats - requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/email-automation/stats")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ Stats endpoint properly requires authentication")
    
    def test_get_stats_with_auth(self, admin_session):
        """Test getting email stats with admin auth"""
        response = admin_session.get(f"{BASE_URL}/api/email-automation/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "by_type" in data, "Stats should include 'by_type'"
        assert "recent_7_days" in data, "Stats should include 'recent_7_days'"
        assert "templates_count" in data, "Stats should include 'templates_count'"
        
        assert data["templates_count"] == 9, f"Expected 9 templates, got {data['templates_count']}"
        
        print(f"✓ Email stats retrieved:")
        print(f"  - Templates: {data['templates_count']}")
        print(f"  - Recent 7 days: {data['recent_7_days']} emails")
        print(f"  - By type breakdown: {len(data['by_type'])} categories")


class TestEmailLogsAPI:
    """Email Logs API tests"""
    
    def test_logs_requires_auth(self):
        """Test /api/email-automation/logs - requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/email-automation/logs")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ Logs endpoint properly requires authentication")
    
    def test_get_logs_with_auth(self, admin_session):
        """Test getting email logs with admin auth"""
        response = admin_session.get(f"{BASE_URL}/api/email-automation/logs", params={"limit": 50})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "logs" in data, "Response should include 'logs'"
        assert "stats" in data, "Response should include 'stats'"
        
        stats = data["stats"]
        assert "total_sent" in stats, "Stats should include total_sent"
        assert "total_failed" in stats, "Stats should include total_failed"
        assert "success_rate" in stats, "Stats should include success_rate"
        
        print(f"✓ Email logs retrieved:")
        print(f"  - Log entries: {len(data['logs'])}")
        print(f"  - Total sent: {stats['total_sent']}")
        print(f"  - Total failed: {stats['total_failed']}")
        print(f"  - Success rate: {stats['success_rate']}%")
    
    def test_get_logs_with_filter(self, admin_session):
        """Test filtering logs by email type"""
        response = admin_session.get(
            f"{BASE_URL}/api/email-automation/logs",
            params={"limit": 10, "email_type": "welcome"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # If there are logs, they should all be of type 'welcome'
        for log in data["logs"]:
            assert log["type"] == "welcome", f"Filter failed: got log type {log['type']}"
        
        print(f"✓ Log filtering by type working - {len(data['logs'])} welcome logs found")
    
    def test_get_logs_with_status_filter(self, admin_session):
        """Test filtering logs by status"""
        response = admin_session.get(
            f"{BASE_URL}/api/email-automation/logs",
            params={"limit": 10, "status": "sent"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # If there are logs, they should all have status 'sent'
        for log in data["logs"]:
            assert log["status"] == "sent", f"Filter failed: got status {log['status']}"
        
        print(f"✓ Log filtering by status working - {len(data['logs'])} sent logs found")


class TestSendTestEmailAPI:
    """Send Test Email API tests"""
    
    def test_send_test_requires_auth(self):
        """Test /api/email-automation/send-test - requires admin auth"""
        response = requests.post(
            f"{BASE_URL}/api/email-automation/send-test",
            params={"template_id": "welcome", "recipient": "test@test.com"}
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✓ Send test endpoint properly requires authentication")
    
    def test_send_test_invalid_template(self, admin_session):
        """Test sending test email with invalid template"""
        response = admin_session.post(
            f"{BASE_URL}/api/email-automation/send-test",
            params={"template_id": "invalid_template", "recipient": "test@test.com"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Invalid template properly returns 404")
    
    def test_send_test_email_with_auth(self, admin_session):
        """Test sending test email with admin auth"""
        test_recipient = "testuser@example.com"
        
        response = admin_session.post(
            f"{BASE_URL}/api/email-automation/send-test",
            params={"template_id": "welcome", "recipient": test_recipient}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "success" in data, "Response should include 'success'"
        assert data["template_id"] == "welcome"
        assert data["recipient"] == test_recipient
        
        # Note: success may be False if email domain not verified (Resend)
        print(f"✓ Send test email API called successfully")
        print(f"  - Template: welcome")
        print(f"  - Recipient: {test_recipient}")
        print(f"  - Success: {data['success']}")


class TestScheduledTasksAPI:
    """Scheduled Tasks API tests"""
    
    def test_run_scheduled_tasks(self, admin_session):
        """Test /api/email-automation/run-scheduled-tasks"""
        response = admin_session.post(f"{BASE_URL}/api/email-automation/run-scheduled-tasks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "renewals" in data, "Response should include 'renewals'"
        assert "low_credits" in data, "Response should include 'low_credits'"
        assert "inactivity" in data, "Response should include 'inactivity'"
        
        print(f"✓ Scheduled tasks executed successfully:")
        print(f"  - Renewals processed: {data['renewals']}")
        print(f"  - Low credits processed: {data['low_credits']}")
        print(f"  - Inactivity processed: {data['inactivity']}")
    
    def test_run_weekly_digest(self, admin_session):
        """Test /api/email-automation/run-weekly-digest"""
        response = admin_session.post(f"{BASE_URL}/api/email-automation/run-weekly-digest")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "sent" in data, "Response should include 'sent' count"
        
        print(f"✓ Weekly digest executed: {data['sent']} emails sent")


class TestEmailTemplateContent:
    """Test email template content and structure"""
    
    @pytest.mark.parametrize("template_id", EXPECTED_TEMPLATES)
    def test_template_has_required_fields(self, template_id):
        """Test each template has required fields"""
        response = requests.get(f"{BASE_URL}/api/email-automation/templates/{template_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "subject" in data
        assert "enabled" in data
        assert "trigger" in data
        assert "template_html" in data
        
        # Check template HTML is not empty and contains basic structure
        assert len(data["template_html"]) > 100, "Template HTML seems too short"
        assert "<div" in data["template_html"], "Template should contain HTML div elements"
        
        print(f"✓ Template '{template_id}' has valid structure")


# Run tests when executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
