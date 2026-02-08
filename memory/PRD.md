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
- 7-day sessions

### 2. Simple Admin Auth (`/admin-login`)
- For basic admin dashboard
- 3-factor: Email + Password + Security Code

### 3. Full Admin Panel (`/admin-panel/login`)
- Production-grade SaaS admin
- 3-factor authentication
- **2FA Support (TOTP)**
- **IP Whitelist**
- Role-based access control
- 8-hour sessions
- Full audit logging

## Admin Panel Features

### Dashboard
- Total Users, Subscriptions, Accounts, AI Requests
- Revenue chart (30 days)
- New Users chart (30 days)
- AI Usage trend
- Users by Plan distribution

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

### Security
- **2FA with TOTP**
- **IP Whitelist per admin**
- Backup codes
- Session management

## Admin Credentials

### Super Admin (Full Access)
| Field | Value |
|-------|-------|
| Email | superadmin@instagrowth.com |
| Password | SuperAdmin123! |
| Security Code | INSTAGROWTH_ADMIN_2024 |
| Login URL | `/admin-panel/login` |

### Simple Admin (Limited)
| Field | Value |
|-------|-------|
| Email | admin@instagrowth.com |
| Password | AdminPass123! |
| Security Code | INSTAGROWTH_ADMIN_2024 |
| Login URL | `/admin-login` |

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
│   ├── auth.py                  # User auth
│   ├── admin_auth.py            # Simple admin auth
│   ├── admin_panel_auth.py      # Full admin panel auth + 2FA + IP
│   ├── admin_panel_users.py     # User management
│   ├── admin_panel_subscriptions.py  # Subs + Plans
│   ├── admin_panel_dashboard.py # Dashboard + Analytics
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
│   └── websocket.py
└── .env.example
```

## Frontend Pages

### User Pages
- `/` - Landing Page
- `/login` - User Login
- `/register` - User Registration
- `/dashboard` - User Dashboard
- `/accounts` - Instagram Accounts
- `/audit` - AI Audit
- `/content` - Content Engine
- `/growth-planner` - Growth Plans
- `/billing` - Subscription
- `/settings` - User Settings
- `/team` - Team Management
- `/dm-templates` - DM Templates
- `/competitors` - Competitor Analysis
- `/ab-testing` - A/B Testing

### Admin Panel Pages
- `/admin-panel/login` - Admin Login
- `/admin-panel` - Dashboard
- `/admin-panel/users` - User Management
- `/admin-panel/subscriptions` - Subscriptions
- `/admin-panel/plans` - Plan Management
- `/admin-panel/instagram` - Instagram Accounts
- `/admin-panel/ai-usage` - AI Usage
- `/admin-panel/revenue` - Revenue Analytics
- `/admin-panel/team` - Admin Team
- `/admin-panel/settings` - System Settings
- `/admin-panel/logs` - Activity Logs

## API Endpoints

### Admin Panel Auth (`/api/admin-panel/auth`)
- `POST /login` - Login with 2FA support
- `POST /setup-2fa` - Setup TOTP
- `POST /verify-2fa` - Enable 2FA
- `POST /disable-2fa` - Disable 2FA
- `GET /me` - Current admin
- `POST /logout` - Logout

### Admin Panel Security (`/api/admin-panel/security`)
- `GET /ip-whitelist` - Get whitelist
- `POST /ip-whitelist` - Add IP
- `DELETE /ip-whitelist/{ip}` - Remove IP

### Admin Panel Users (`/api/admin-panel/users`)
- `GET /` - List users
- `GET /{id}` - User details
- `PUT /{id}/plan` - Change plan
- `PUT /{id}/status` - Block/Unblock
- `POST /{id}/reset-password` - Reset password
- `DELETE /{id}` - Delete user
- `GET /export/csv` - Export CSV

### Admin Panel Dashboard (`/api/admin-panel/dashboard`)
- `GET /stats` - Overview stats
- `GET /charts/revenue` - Revenue chart
- `GET /charts/users` - Users chart
- `GET /charts/ai-usage` - AI usage chart

## Completed Features

### User Features
- [x] User Authentication (JWT + Google OAuth)
- [x] Email Verification
- [x] Password Reset
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
- [x] **Two-Factor Authentication (2FA/TOTP)**
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

## Future Enhancements
- [ ] Real Instagram API integration
- [ ] Mobile app
- [ ] WebSocket for admin real-time updates
- [ ] Admin notifications
- [ ] Two-factor for regular users
