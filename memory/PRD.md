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

## User Personas
1. **Instagram Growth Agencies** - Manage multiple client accounts, need audit reports and growth plans
2. **Social Media Freelancers** - Individual managers handling 3-5 accounts
3. **Influencers & Coaches** - Self-managing their Instagram presence
4. **Digital Marketers** - Need content ideas and engagement strategies

## Core Requirements (Static)
### MVP Features
- [ ] User Authentication (JWT + Google OAuth)
- [ ] Instagram Account Management (CRUD)
- [ ] AI Account Audit with PDF export
- [ ] AI Content Engine (reels, hooks, captions, hashtags)
- [ ] Growth Planner (7/14/30 day plans)
- [ ] Subscription Plans & Stripe Integration
- [ ] Admin Dashboard

### Subscription Tiers
| Plan | Price | Accounts | AI Usage |
|------|-------|----------|----------|
| Starter | $19/mo | 1 | 10/mo |
| Pro | $49/mo | 5 | 100/mo |
| Agency | $149/mo | 25 | 500/mo |
| Enterprise | $299/mo | 100 | 2000/mo |

## What's Been Implemented (Jan 2026)

### Backend (FastAPI)
- [x] User registration and login with JWT
- [x] Google OAuth integration via Emergent Auth
- [x] Instagram account CRUD operations
- [x] AI Audit generation with OpenAI GPT-5.2
- [x] AI Content generation (4 types)
- [x] Growth Plan generation
- [x] PDF export for audits and plans
- [x] Stripe subscription checkout
- [x] Usage limits per plan
- [x] Admin endpoints for user management

### Frontend (React)
- [x] Landing page with hero, features, pricing, testimonials
- [x] Login/Register with Google OAuth button
- [x] Dashboard with stats, quick actions, AI usage
- [x] Accounts page with add/edit/delete
- [x] AI Audit page with score visualization
- [x] Content Engine with 4 tabs (reels, hooks, captions, hashtags)
- [x] Growth Planner with task checklist
- [x] Billing page with plan comparison
- [x] Settings page (profile, notifications, security)
- [x] Admin page (user management, stats)
- [x] Dark mode premium theme (indigo/purple)

## Prioritized Backlog

### P0 - Critical (Next Sprint)
- [ ] Email verification for new accounts
- [ ] Password reset flow
- [ ] Webhook handling for Stripe events
- [ ] Rate limiting for AI endpoints

### P1 - High Priority
- [ ] White-label PDF customization (Agency/Enterprise)
- [ ] Team member management for Agency plans
- [ ] Content favorites/saved items
- [ ] Scheduling recommendations based on niche

### P2 - Medium Priority
- [ ] Instagram API integration for real follower/engagement data
- [ ] A/B testing for hooks and captions
- [ ] Performance analytics dashboard
- [ ] Export data to CSV

### P3 - Nice to Have
- [ ] DM template library
- [ ] Competitor analysis feature
- [ ] Mobile app (React Native)
- [ ] Zapier integration

## Next Tasks List
1. Implement email verification
2. Add password reset functionality
3. Enhance Stripe webhook handling for plan upgrades/downgrades
4. Add team member invitation for Agency plans
5. Implement content favorites feature

## Technical Notes
- All AI calls use emergentintegrations library with EMERGENT_LLM_KEY
- PDF generation uses ReportLab
- MongoDB collections: users, user_sessions, instagram_accounts, audits, content_items, growth_plans, payment_transactions
- All API routes prefixed with /api
