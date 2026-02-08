# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies.

## Architecture & Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async driver) - **MODULAR**
- **AI**: OpenAI GPT-5.2 via emergentintegrations library
- **Auth**: JWT (email/password) + Google OAuth + **Separate Admin Auth**
- **Payments**: Stripe subscriptions
- **Email**: Resend
- **Real-time**: WebSocket

## Authentication Systems

### User Authentication
- Email/Password with JWT tokens
- Google OAuth via Emergent Auth
- Session-based with cookies
- Email verification required

### Admin Authentication (SEPARATE)
- Dedicated admin login page: `/admin-login`
- Three-factor authentication:
  1. Admin Email
  2. Password
  3. **Admin Security Code**
- Shorter session (8 hours vs 7 days)
- Login history tracking
- Dedicated logout

## Admin Credentials
| Field | Value |
|-------|-------|
| Email | admin@instagrowth.com |
| Password | AdminPass123! |
| Admin Security Code | INSTAGROWTH_ADMIN_2024 |
| Admin Login URL | `/admin-login` |

## Backend Architecture (v2.0.0)
```
/app/backend/
├── server.py              # Main app
├── database.py            # MongoDB connection
├── dependencies.py        # Auth helpers
├── models/
│   └── __init__.py        # Pydantic models
├── utils/
│   └── __init__.py        # Helpers
├── services/
│   └── __init__.py        # AI + Email
├── routers/
│   ├── auth.py            # User authentication
│   ├── admin_auth.py      # **ADMIN AUTHENTICATION**
│   ├── accounts.py        # Instagram accounts
│   ├── audits.py          # AI audits
│   ├── content.py         # Content engine
│   ├── growth.py          # Growth planner
│   ├── teams.py           # Team management
│   ├── dm_templates.py    # DM templates
│   ├── competitors.py     # Competitor analysis
│   ├── ab_testing.py      # A/B testing
│   ├── notifications.py   # Notifications
│   ├── billing.py         # Stripe billing
│   ├── admin.py           # Admin functions
│   └── websocket.py       # Real-time
└── .env.example
```

## Admin API Endpoints

### `/api/admin-auth`
- `POST /login` - Admin login with security code
- `GET /verify` - Verify admin session
- `POST /logout` - Admin logout
- `GET /login-history` - View admin login history

### `/api/admin`
- `GET /users` - List all users
- `GET /stats` - Platform statistics
- `PUT /users/{id}/role` - Update user role
- `DELETE /users/{id}` - Delete user

## Features Completed

### Core Features
- [x] User Authentication (JWT + Google OAuth)
- [x] **Separate Admin Authentication System**
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
- [x] Admin Dashboard with User Management

### Security Features
- [x] Rate limiting on AI endpoints
- [x] Admin security code requirement
- [x] 8-hour admin session expiry
- [x] Admin login history tracking
- [x] Separate admin token storage

## Subscription Tiers
| Plan | Price | Accounts | AI Usage |
|------|-------|----------|----------|
| Starter | $19/mo | 1 | 10/mo |
| Pro | $49/mo | 5 | 100/mo |
| Agency | $149/mo | 25 | 500/mo |
| Enterprise | $299/mo | 100 | 2000/mo |

## URLs
- Landing Page: `/`
- User Login: `/login`
- User Register: `/register`
- **Admin Login: `/admin-login`**
- Dashboard: `/dashboard`
- Admin Dashboard: `/admin`

## Environment Variables
```
# Admin Security
ADMIN_SECRET_CODE=INSTAGROWTH_ADMIN_2024

# Email
RESEND_API_KEY=re_your_key
SENDER_EMAIL=noreply@yourdomain.com

# AI
EMERGENT_LLM_KEY=your_key

# Payments
STRIPE_API_KEY=sk_test_your_key
```

## Known Limitations
1. Instagram data is AI-estimated (MOCKED)
2. Email requires valid Resend API key
3. Stripe webhook is placeholder

## Future Enhancements
- [ ] Real Instagram API integration
- [ ] Mobile app
- [ ] Two-factor authentication for all users
- [ ] Admin IP whitelist
