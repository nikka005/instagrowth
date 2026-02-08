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

## What's Been Implemented (Jan 2026)

### Backend (FastAPI) v1.1.0
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

## Prioritized Backlog

### P0 - Critical (Next Sprint)
- [ ] Rate limiting for AI endpoints
- [ ] Resend API key configuration for production emails

### P1 - High Priority
- [ ] Content favorites/saved items
- [ ] Scheduling recommendations based on niche
- [ ] Notification system for team invites

### P2 - Medium Priority
- [ ] Instagram API integration for real follower/engagement data (when Meta API available)
- [ ] A/B testing for hooks and captions
- [ ] Performance analytics dashboard
- [ ] Export data to CSV

### P3 - Nice to Have
- [ ] DM template library
- [ ] Competitor analysis feature
- [ ] Mobile app (React Native)
- [ ] Zapier integration

## Next Tasks List
1. Configure production Resend API key for emails
2. Add rate limiting to AI endpoints
3. Implement content favorites feature
4. Add notification system for team invites
5. Build scheduling recommendation engine

## Technical Notes
- All AI calls use emergentintegrations library with EMERGENT_LLM_KEY
- Email service uses Resend (needs production API key for live emails)
- PDF generation uses ReportLab with white-label support
- MongoDB collections: users, user_sessions, instagram_accounts, audits, content_items, growth_plans, payment_transactions, teams, team_members, password_resets
- All API routes prefixed with /api
