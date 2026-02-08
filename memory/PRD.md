# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies. All-in-one AI wrapper that runs Instagram growth accounts like a pro manager.

## Architecture & Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async driver) - **NOW MODULAR**
- **AI**: OpenAI GPT-5.2 via emergentintegrations library
- **Auth**: JWT (email/password) + Emergent Google OAuth
- **Payments**: Stripe subscriptions via emergentintegrations
- **PDF Generation**: ReportLab
- **Email**: Resend (for verification & password reset)
- **Real-time**: WebSocket for notifications

## Backend Architecture (v2.0.0 - MODULAR)
```
/app/backend/
├── server.py              # Main app - includes all routers
├── database.py            # MongoDB connection
├── dependencies.py        # Auth & helper dependencies
├── models/
│   └── __init__.py        # All Pydantic models
├── utils/
│   └── __init__.py        # Password hashing, tokens, rate limiting
├── services/
│   └── __init__.py        # AI services, email with timeout handling
├── routers/
│   ├── __init__.py        # Router exports
│   ├── auth.py            # Authentication endpoints
│   ├── accounts.py        # Instagram account management
│   ├── audits.py          # AI audit generation
│   ├── content.py         # Content engine
│   ├── growth.py          # Growth planner
│   ├── teams.py           # Team management
│   ├── dm_templates.py    # DM template CRUD
│   ├── competitors.py     # Competitor analysis
│   ├── ab_testing.py      # A/B testing
│   ├── notifications.py   # Notification system
│   ├── billing.py         # Stripe billing
│   ├── admin.py           # Admin dashboard
│   └── websocket.py       # Real-time WebSocket
└── .env.example           # Configuration template
```

## Admin Credentials
| Email | Password | Role |
|-------|----------|------|
| admin@instagrowth.com | AdminPass123! | admin |

## Subscription Tiers
| Plan | Price | Accounts | AI Usage | Team Features |
|------|-------|----------|----------|---------------|
| Starter | $19/mo | 1 | 10/mo | No |
| Pro | $49/mo | 5 | 100/mo | No |
| Agency | $149/mo | 25 | 500/mo | Yes |
| Enterprise | $299/mo | 100 | 2000/mo | Yes |

## Completed Features (Feb 2026)

### Backend (FastAPI) v2.0.0 - MODULAR ARCHITECTURE
- [x] User registration and login with JWT
- [x] Google OAuth integration via Emergent Auth
- [x] Email verification flow (Resend integration)
- [x] Password reset with secure tokens
- [x] Instagram account CRUD operations
- [x] AI-based Instagram metrics estimation
- [x] AI Audit generation with OpenAI GPT-5.2
- [x] AI Content generation (4 types)
- [x] Growth Plan generation with extended timeout
- [x] White-label PDF export for audits and plans
- [x] Stripe subscription checkout
- [x] Usage limits per plan
- [x] Team management (create, invite, roles)
- [x] Team settings (logo upload, brand color)
- [x] Admin endpoints for user management
- [x] DM Templates CRUD with variable extraction
- [x] Competitor Analysis AI-powered
- [x] A/B Testing with voting system
- [x] Posting Recommendations AI-based
- [x] Content Favorites system
- [x] Notifications System
- [x] Rate Limiting protection
- [x] CSV Export functionality
- [x] One-Time Products system
- [x] **WebSocket real-time notifications**
- [x] **AI Timeout Handling (30s/60s/120s)**
- [x] **Modular router architecture**

### Frontend (React)
- [x] Landing page with hero, features, pricing, testimonials
- [x] Login/Register with Google OAuth button
- [x] Forgot Password page
- [x] Reset Password page
- [x] Email Verification page
- [x] Dashboard with stats, quick actions, AI usage
- [x] Accounts page with add/edit/delete
- [x] AI Audit page with score visualization
- [x] Content Engine with 4 tabs
- [x] Growth Planner with task checklist
- [x] Billing page with plan comparison
- [x] Settings page (profile, notifications, security)
- [x] Team Management page
- [x] Admin page
- [x] DM Templates Page
- [x] Competitor Analysis Page
- [x] A/B Testing Page
- [x] Mobile Sidebar Overlay (fixed)

## Completed Tasks This Session
1. ✅ **P0: Backend Router Migration** - Split 2400+ line server.py into 13 modular routers
2. ✅ **P0: Resend Configuration** - Created .env.example with setup instructions
3. ✅ **P1: WebSocket Notifications** - Added real-time notification support
4. ✅ **P2: AI Timeout Handling** - Configurable timeouts (SHORT=30s, MEDIUM=60s, LONG=120s)
5. ✅ **P1: Mobile Sidebar Fix** - Fixed z-index and backdrop blur

## API Endpoints Reference

### Authentication (`/api/auth`)
- POST `/register` - Register new user
- POST `/login` - Login with email/password
- POST `/session` - Create session from Google OAuth
- GET `/me` - Get current user
- POST `/logout` - Logout
- POST `/verify-email` - Verify email token
- POST `/forgot-password` - Request password reset
- POST `/reset-password` - Reset password with token

### Instagram Accounts (`/api/accounts`)
- POST `/` - Create account
- GET `/` - List accounts
- GET `/{id}` - Get account
- PUT `/{id}` - Update account
- DELETE `/{id}` - Delete account
- POST `/{id}/refresh-metrics` - Refresh AI metrics
- GET `/{id}/posting-recommendations` - Get posting times

### AI Features
- POST `/api/audits` - Create AI audit
- POST `/api/content/generate` - Generate content
- POST `/api/growth-plans` - Create growth plan
- POST `/api/competitors/analyze` - Analyze competitors
- POST `/api/dm-templates/{id}/generate-reply` - Generate DM reply

### Billing (`/api/billing`)
- GET `/plans` - Get subscription plans
- POST `/create-checkout-session` - Create Stripe checkout
- GET `/subscription` - Get user subscription
- POST `/upgrade` - Upgrade plan

### WebSocket
- WS `/api/ws/{user_id}` - Real-time notifications

## Configuration Required

### Required API Keys (set in `/app/backend/.env`)
```
RESEND_API_KEY=re_your_key_here      # For email delivery
STRIPE_API_KEY=sk_test_your_key      # For payments  
EMERGENT_LLM_KEY=your_key            # For AI features
```

### Setup Resend for Production Emails
1. Go to https://resend.com
2. Create account and verify domain
3. Generate API key
4. Add to .env: `RESEND_API_KEY=re_xxxxx`
5. Update: `SENDER_EMAIL=noreply@yourdomain.com`

## Known Limitations
1. Instagram data is AI-estimated (real API requires Meta approval)
2. Email sending requires valid Resend API key
3. Stripe webhook endpoint is placeholder (configure in Stripe dashboard)

## Future Enhancements
- [ ] Real Instagram API integration
- [ ] Mobile app (React Native)
- [ ] Light mode toggle
- [ ] Chrome extension
- [ ] Zapier integration
