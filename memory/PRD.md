# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies. All-in-one AI wrapper that runs Instagram growth accounts like a pro manager.

## Architecture & Tech Stack
- **Frontend**: React 19 + Tailwind CSS + Shadcn UI + Framer Motion
- **Backend**: FastAPI + MongoDB (Motor async driver)
- **AI**: OpenAI GPT-5.2 via emergentintegrations library
- **Auth**: JWT (email/password) + Emergent Google OAuth
- **Payments**: Stripe subscriptions via emergentintegrations
- **PDF Generation**: ReportLab
- **Email**: Resend (for verification & password reset)

## User Personas
1. **Instagram Growth Agencies** - Manage multiple client accounts, need audit reports and growth plans
2. **Social Media Freelancers** - Individual managers handling 3-5 accounts
3. **Influencers & Coaches** - Self-managing their Instagram presence
4. **Digital Marketers** - Need content ideas and engagement strategies

## Core Requirements (Static)
### MVP Features
- [x] User Authentication (JWT + Google OAuth)
- [x] Email Verification via Resend
- [x] Password Reset Flow
- [x] Instagram Account Management (CRUD)
- [x] AI Account Audit with PDF export
- [x] AI Content Engine (reels, hooks, captions, hashtags)
- [x] Growth Planner (7/14/30 day plans)
- [x] Subscription Plans & Stripe Integration
- [x] Team Management (invite + roles) for Agency/Enterprise
- [x] White-label PDF Customization (logo + colors)
- [x] AI-based Instagram Metrics Estimation
- [x] Admin Dashboard

### Subscription Tiers
| Plan | Price | Accounts | AI Usage | Team Features |
|------|-------|----------|----------|---------------|
| Starter | $19/mo | 1 | 10/mo | No |
| Pro | $49/mo | 5 | 100/mo | No |
| Agency | $149/mo | 25 | 500/mo | Yes |
| Enterprise | $299/mo | 100 | 2000/mo | Yes |

## What's Been Implemented (Feb 2026)

### Backend (FastAPI) v2.0.0
- [x] User registration and login with JWT
- [x] Google OAuth integration via Emergent Auth
- [x] Email verification flow (Resend integration)
- [x] Password reset with secure tokens
- [x] Instagram account CRUD operations
- [x] AI-based Instagram metrics estimation
- [x] AI Audit generation with OpenAI GPT-5.2
- [x] AI Content generation (4 types)
- [x] Growth Plan generation
- [x] White-label PDF export for audits and plans
- [x] Stripe subscription checkout
- [x] Usage limits per plan
- [x] Team management (create, invite, roles)
- [x] Team settings (logo upload, brand color)
- [x] Admin endpoints for user management
- [x] DM Templates - Create, read, update, delete templates with variable extraction
- [x] Competitor Analysis - AI-powered competitor insights and opportunities
- [x] A/B Testing - Create tests, vote, determine winners
- [x] Posting Recommendations - AI-based best time to post
- [x] Content Favorites - Save/favorite content items
- [x] Notifications System - Team invites, system alerts, plan upgrades
- [x] Rate Limiting - Protect AI endpoints from abuse
- [x] CSV Export - Export data for external analysis
- [x] One-Time Products - Purchase individual reports and content packs
- [x] **AI Timeout Handling** - Configurable timeouts (30s/60s/120s) for AI operations

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
- [x] Team Management page (Agency/Enterprise only)
- [x] Admin page (user management, stats)
- [x] Dark mode premium theme (indigo/purple)
- [x] DM Templates Page - Manage auto-reply templates
- [x] Competitor Analysis Page - Analyze competitor accounts
- [x] A/B Testing Page - Test content variants
- [x] **Mobile Sidebar Overlay** - Fixed z-index and backdrop blur

### Modular Backend Structure (Created)
```
/app/backend/
├── server.py          # Main application (existing, with timeout handling)
├── models/            # Pydantic models
│   └── __init__.py
├── utils/             # Helper functions (hash, tokens, rate limiting)
│   └── __init__.py
├── services/          # AI and email services with timeout handling
│   └── __init__.py
├── routers/           # API routers (ready for migration)
│   └── auth.py
└── .env.example       # Configuration template with Resend setup guide
```

### Testing Status (Feb 8, 2026)
- Backend: 95.5% pass rate (21/22 tests)
- Frontend: 100% pass rate
- Mobile: Sidebar overlay working correctly
- Test report: `/app/test_reports/iteration_3.json`

## Completed Tasks (This Session)
- [x] P0: Documented Resend API key configuration (.env.example created)
- [x] P1: Created modular backend structure (models, utils, services, routers)
- [x] P1: Fixed mobile sidebar overlay z-index issue
- [x] P2: Added AI timeout handling (30s/60s/120s configurable)

## Prioritized Backlog

### P0 - Critical
- [ ] Complete migration of server.py to use modular routers

### P1 - High Priority
- [ ] Real Instagram API integration (when Meta API available)
- [ ] Add more comprehensive error handling for AI failures

### P2 - Medium Priority
- [ ] Performance analytics dashboard
- [ ] More detailed competitor metrics
- [ ] Automated scheduling integration
- [ ] Zapier integration

### P3 - Nice to Have
- [ ] Mobile app (React Native)
- [ ] Light mode toggle
- [ ] Chrome extension for Instagram
- [ ] Real-time notifications with WebSocket

## Next Tasks List
1. Complete backend refactoring - move all routes to routers/
2. Add WebSocket support for real-time notifications
3. Enhance competitor analysis with more metrics
4. Build scheduling recommendation engine

## Technical Notes
- All AI calls use emergentintegrations library with EMERGENT_LLM_KEY
- AI Timeout configuration: SHORT=30s, MEDIUM=60s, LONG=120s
- Email service uses Resend (see .env.example for setup)
- PDF generation uses ReportLab with white-label support
- MongoDB collections: users, user_sessions, instagram_accounts, audits, content_items, growth_plans, payment_transactions, teams, team_members, password_resets, dm_templates, competitor_analyses, ab_tests, notifications, one_time_purchases
- All API routes prefixed with /api
- Instagram metrics are AI-estimated (MOCKED - not real Instagram API)

## Configuration Required
See `/app/backend/.env.example` for complete configuration guide including:
- Resend API key setup for production emails
- Stripe API key configuration
- JWT secret generation
- MongoDB connection

## Known Limitations
1. Instagram data is AI-estimated (real API requires Meta approval)
2. Email sending requires valid Resend API key (currently using placeholder)
