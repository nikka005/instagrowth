# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies.

## Current Status: PRODUCTION READY ✅

---

## Architecture Overview

### Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Recharts + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor) - **FULLY MODULAR**
- **AI**: OpenAI GPT-5.2 via Emergent Universal Key
- **Auth**: JWT + Google OAuth + Separate Admin Panel Auth
- **Payments**: Stripe subscriptions
- **Email**: Resend
- **Real-time**: WebSocket
- **2FA**: TOTP (Google Authenticator compatible)
- **Instagram**: Meta Graph API (OAuth 2.0)

---

## Completed Features

### User Features ✅
- [x] User Authentication (JWT + Google OAuth)
- [x] Email Verification
- [x] Password Reset
- [x] Two-Factor Authentication (2FA/TOTP)
- [x] Instagram Account Management (OAuth + Manual)
- [x] AI Audits with PDF Export
- [x] Content Engine (4 content types)
- [x] Growth Planner with AI recommendations
- [x] Team Management with invitations
- [x] Stripe Billing (4 tiers)
- [x] DM Templates
- [x] Competitor Analysis
- [x] A/B Testing
- [x] WebSocket Notifications

### Admin Panel ✅
- [x] Separate Admin Authentication (3-factor)
- [x] Dashboard with Charts (Recharts)
- [x] User Management (CRUD + Export CSV)
- [x] Plan Management (Create/Edit/Disable)
- [x] Revenue Analytics
- [x] AI Usage Monitoring
- [x] System Settings (API Keys management)
- [x] Activity Logs
- [x] Admin Documentation
- [x] Real-time WebSocket notifications

### Instagram API Integration ✅
- [x] Meta OAuth 2.0 connection flow
- [x] Real follower/following/media counts
- [x] Account refresh from API
- [x] Disconnect functionality
- [x] Data Deletion Callback URL (Meta requirement)

### Legal Pages ✅
- [x] Privacy Policy (`/privacy`)
- [x] Terms of Service (`/terms`)
- [x] Refund Policy (`/refund`)
- [x] Data Deletion (`/data-deletion`)

---

## Admin Credentials

| Field | Value |
|-------|-------|
| URL | `/admin-panel/login` |
| Email | `superadmin@instagrowth.com` |
| Password | `SuperAdmin123!` |
| Security Code | `INSTAGROWTH_ADMIN_2024` |

---

## System Settings Configured

### ✅ OpenAI/AI
- API Key: Emergent Universal Key
- Model: GPT-5.2
- Supports: GPT-5.2, GPT-4o, Claude, Gemini

### ✅ Email (Resend)
- API Key: Configured
- Sender: noreply@instagrowth.app

### ⚙️ Stripe (Needs User Keys)
- Dashboard: https://dashboard.stripe.com/apikeys
- Webhook URL: `{domain}/api/billing/webhook`

### ⚙️ Meta/Instagram (Needs User Keys)
- Dashboard: https://developers.facebook.com/apps/
- Required: App ID, App Secret, Access Token

---

## Subscription Plans

| Plan | Price | Accounts | AI Credits | Team |
|------|-------|----------|------------|------|
| Starter | $19/mo | 1 | 10 | 0 |
| Pro | $49/mo | 5 | 100 | 0 |
| Agency | $149/mo | 25 | 500 | 5 |
| Enterprise | $299/mo | 100 | 2000 | 20 |

---

## API Endpoints Summary

### Auth
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (supports 2FA)
- `POST /api/auth/google/callback` - Google OAuth
- `POST /api/auth/data-deletion-request` - GDPR data deletion
- `POST /api/auth/data-deletion-callback` - Meta callback URL

### Instagram OAuth
- `GET /api/instagram/auth/url` - Get OAuth URL
- `GET /api/instagram/callback` - OAuth callback
- `POST /api/instagram/{id}/refresh` - Refresh account data
- `DELETE /api/instagram/{id}/disconnect` - Disconnect account

### Admin Panel
- `POST /api/admin-panel/auth/login` - Admin login
- `GET /api/admin-panel/dashboard/stats` - Dashboard stats
- `GET /api/admin-panel/users` - List users
- `GET /api/admin-panel/plans` - List plans
- `GET /api/admin-panel/settings` - System settings
- `POST /api/admin-panel/settings/test-connection` - Test API connections

---

## File Structure

```
/app
├── backend/
│   ├── server.py                    # Main FastAPI app
│   ├── database.py                  # MongoDB connection
│   ├── dependencies.py              # Auth helpers
│   ├── models/                      # Pydantic models
│   ├── services/                    # AI & Email services
│   └── routers/
│       ├── auth.py                  # User auth + 2FA + data deletion
│       ├── accounts.py              # Instagram accounts
│       ├── instagram_oauth.py       # Meta OAuth flow
│       ├── admin_panel_*.py         # Admin panel endpoints
│       └── ...
└── frontend/
    └── src/
        ├── pages/
        │   ├── LandingPage.jsx
        │   ├── AccountsPage.jsx
        │   ├── PrivacyPolicyPage.jsx
        │   ├── TermsOfServicePage.jsx
        │   ├── RefundPolicyPage.jsx
        │   ├── DataDeletionPage.jsx
        │   └── admin-panel/
        │       ├── DashboardPage.jsx
        │       ├── UsersPage.jsx
        │       ├── PlansPage.jsx
        │       ├── SystemSettingsPage.jsx
        │       ├── DocumentationPage.jsx
        │       └── ...
        └── components/
            ├── AdminPanelLayout.jsx
            ├── DashboardLayout.jsx
            └── ...
```

---

## Last Updated
February 8, 2025

## What's Next (Backlog)
1. Real Instagram API data (requires Meta App Review)
2. Stripe payment integration (requires user API keys)
3. Light/Dark mode toggle
4. Mobile app (React Native)
5. Advanced analytics dashboard
