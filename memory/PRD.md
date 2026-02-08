# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies.

## Architecture Overview

### Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Recharts
- **Backend**: FastAPI + MongoDB (Motor) - **FULLY MODULAR**
- **AI**: OpenAI GPT-5.2 via emergentintegrations
- **Auth**: JWT + Google OAuth + **Separate Admin Panel Auth**
- **Payments**: Stripe subscriptions
- **Email**: Resend
- **Real-time**: WebSocket
- **2FA**: TOTP (Google Authenticator compatible)

## Authentication Systems

### 1. User Authentication (`/login`)
- Email/Password with JWT
- Google OAuth
- **Two-Factor Authentication (TOTP) Support**
- 7-day sessions

### 2. Admin Panel (`/admin-panel/login`)
- Production-grade SaaS admin
- 3-factor authentication (Email + Password + Security Code)
- **2FA Support (TOTP)**
- **IP Whitelist**
- Role-based access control (super_admin, support, finance)
- 8-hour sessions
- Full audit logging

## Admin Panel Features - COMPLETED

### Dashboard
- Total Users, Subscriptions, Accounts, AI Requests
- Revenue chart (30 days)
- New Users chart (30 days)
- AI Usage trend
- Users by Plan distribution (Pie chart)

### User Management
- View all users with search/filter
- Change user plans
- Block/Unblock users
- Reset passwords
- Delete users
- Export to CSV

### Subscription Management
- View all subscriptions
- Cancel subscriptions
- Change plans
- Sync with Stripe

### Plan Management
- Create new plans
- Edit pricing and limits
- Set: Account limit, AI credits, Team seats, White-label
- Enable/Disable plans
- View subscriber counts

### Revenue Dashboard
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- Churn Rate
- ARPU (Average Revenue Per User)
- Revenue by Plan chart

### AI Usage Monitoring
- Requests today/month
- Estimated cost
- Usage by feature
- Top users table

### System Settings (Super Admin only)
- Platform name
- Support email
- Default AI model
- API Keys: OpenAI, Stripe, Resend, Meta

### Activity Logs
- All admin actions logged
- Filter by action/type
- IP address tracking
- Timestamps

### Security - COMPLETED
- **2FA with TOTP for admins**
- **IP Whitelist per admin**
- Backup codes
- Session management

## User 2FA - COMPLETED

### Features
- Enable/Disable 2FA in Settings > Security tab
- QR code generation for authenticator apps
- Manual entry key support
- 10 backup codes generated on setup
- Backup code regeneration with verification
- 2FA required on login when enabled

## Admin WebSocket - COMPLETED

### Real-time Notifications
- New user registrations
- Subscription changes
- AI usage alerts
- System events
- Notification dropdown in admin header

## Admin Credentials

### Super Admin (Full Access)
| Field | Value |
|-------|-------|
| Email | superadmin@instagrowth.com |
| Password | SuperAdmin123! |
| Security Code | INSTAGROWTH_ADMIN_2024 |
| Login URL | `/admin-panel/login` |

## Admin Roles & Permissions

| Role | Permissions |
|------|-------------|
| super_admin | Full access (all features) |
| support | Users, Accounts, Logs |
| finance | Subscriptions, Revenue, Plans |

## Backend Architecture

```
/app/backend/
├── server.py                    # Main app
├── database.py                  # MongoDB
├── dependencies.py              # Auth helpers
├── models/
│   ├── __init__.py              # User models
│   └── admin_models.py          # Admin models
├── utils/
│   └── __init__.py              # Helpers
├── services/
│   └── __init__.py              # AI + Email
├── routers/
│   ├── auth.py                  # User auth with 2FA
│   ├── user_2fa.py              # User 2FA management
│   ├── admin_auth.py            # Simple admin auth
│   ├── admin_panel_auth.py      # Full admin panel auth + 2FA + IP
│   ├── admin_panel_users.py     # User management
│   ├── admin_panel_subscriptions.py  # Subs + Plans
│   ├── admin_panel_dashboard.py # Dashboard + Analytics
│   ├── admin_websocket.py       # Real-time notifications
│   ├── accounts.py
│   ├── audits.py
│   ├── content.py
│   ├── growth.py
│   ├── teams.py
│   ├── dm_templates.py
│   ├── competitors.py
│   ├── ab_testing.py
│   ├── notifications.py
│   ├── billing.py
│   ├── admin.py
│   ├── instagram_api.py         # Instagram API (placeholder)
│   └── websocket.py
└── .env.example
```

## Frontend Pages

### User Pages
- `/` - Landing Page
- `/login` - User Login (with 2FA support)
- `/register` - User Registration
- `/dashboard` - User Dashboard
- `/accounts` - Instagram Accounts
- `/audit` - AI Audit
- `/content` - Content Engine
- `/planner` - Growth Plans
- `/billing` - Subscription
- `/settings` - User Settings (with 2FA in Security tab)
- `/team` - Team Management
- `/dm-templates` - DM Templates
- `/competitors` - Competitor Analysis
- `/ab-testing` - A/B Testing

### Admin Panel Pages
- `/admin-panel/login` - Admin Login
- `/admin-panel` - Dashboard
- `/admin-panel/users` - User Management
- `/admin-panel/plans` - Plan Management
- `/admin-panel/revenue` - Revenue Analytics
- `/admin-panel/ai-usage` - AI Usage
- `/admin-panel/logs` - Activity Logs
- `/admin-panel/settings` - System Settings

## Completed Features (December 2025)

### User Features
- [x] User Authentication (JWT + Google OAuth)
- [x] Email Verification
- [x] Password Reset
- [x] **Two-Factor Authentication (2FA/TOTP) for users**
- [x] Instagram Account Management
- [x] AI Audits with PDF Export
- [x] Content Engine (4 types)
- [x] Growth Planner
- [x] Team Management
- [x] Stripe Billing (4 tiers)
- [x] DM Templates
- [x] Competitor Analysis
- [x] A/B Testing
- [x] WebSocket Notifications

### Admin Panel Features
- [x] Separate Admin Authentication
- [x] **Two-Factor Authentication (2FA/TOTP) for admins**
- [x] **IP Whitelist per Admin**
- [x] Role-Based Access Control
- [x] Dashboard with Charts
- [x] User Management (CRUD)
- [x] Plan Management
- [x] Revenue Analytics
- [x] AI Usage Monitoring
- [x] System Settings
- [x] Activity Logs
- [x] CSV Export
- [x] **Real-time WebSocket notifications**

## Subscription Plans

| Plan | Price | Accounts | AI | Team |
|------|-------|----------|-----|------|
| Starter | $19/mo | 1 | 10 | 0 |
| Pro | $49/mo | 5 | 100 | 0 |
| Agency | $149/mo | 25 | 500 | 5 |
| Enterprise | $299/mo | 100 | 2000 | 20 |

## Known Limitations
1. Instagram data is AI-estimated (MOCKED)
2. Requires valid Resend API key for emails
3. Meta API requires approval for real Instagram data

## Future Enhancements (Backlog)
- [ ] Real Instagram API integration (requires Meta API approval)
- [ ] Mobile app (React Native)
- [ ] Admin notifications panel
- [ ] Light/Dark mode toggle
- [ ] Bulk user operations in admin
- [ ] Advanced analytics dashboard
