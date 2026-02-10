# InstaGrowth OS - Product Requirements Document

## Project Overview
InstaGrowth OS is an AI-powered Instagram Growth & Management Platform that helps users manage their Instagram accounts, run audits, generate content, and track performance.

## Core Features

### User Features
1. **Instagram Account Management**
   - Connect Instagram accounts via OAuth (Instagram Business Login API)
   - Manual account addition
   - View account metrics (followers, following, posts)
   - Refresh data from Instagram API

2. **AI Audit System**
   - Generate engagement scores
   - Shadowban risk assessment
   - Content consistency analysis
   - Growth recommendations

3. **Content Generation**
   - AI-powered captions
   - Hashtag suggestions
   - Post ideas by niche

4. **Growth Planner**
   - Daily task generation
   - Best posting times
   - Content mix recommendations

5. **Billing & Plans**
   - Starter ($19/mo): 1 account, 10 AI generations
   - Pro ($49/mo): 5 accounts, 100 AI generations
   - Agency ($149/mo): 25 accounts, 500 AI generations, team features
   - Enterprise ($299/mo): 100 accounts, 2000 AI generations

### Admin Panel Features
1. **Dashboard Overview**
   - Total users, subscriptions, accounts
   - Revenue charts
   - User growth metrics
   - AI usage tracking

2. **System Settings**
   - OpenAI API key configuration
   - Stripe payment integration
   - Instagram Business Login API setup
   - Resend email integration

3. **User Management**
   - View all users
   - Manage subscriptions
   - View Instagram accounts

## Technical Architecture

### Backend (FastAPI + Python)
- Location: `/app/backend/`
- Entry: `server.py`
- Database: MongoDB (via motor async driver)
- Auth: JWT-based authentication

### Frontend (React)
- Location: `/app/frontend/`
- UI: Tailwind CSS + Shadcn components
- State: React hooks

### Database Schema (MongoDB)
- `users`: User accounts and subscription info
- `admins`: Admin panel users
- `instagram_accounts`: Connected Instagram accounts
- `system_settings`: API keys and platform config
- `audits`: AI audit reports
- `content_items`: Generated content

## Third-Party Integrations
1. **OpenAI GPT-5.2** - AI content generation (via Emergent Universal Key)
2. **Stripe** - Payment processing
3. **Resend** - Transactional emails
4. **Instagram Business Login API** - OAuth and data access

## Completed Work (February 2026)

### Session 1 - Core Fixes
- [x] Fixed collection mismatch: Instagram OAuth now saves to `instagram_accounts` collection
- [x] Fixed data model: Added OAuth-specific fields (connection_status, instagram_id, etc.)
- [x] Fixed /api/plans endpoint to include features array for billing page
- [x] Updated requirements.txt with all dependencies
- [x] Created test user for staging environment
- [x] Verified admin panel login and System Settings page
- [x] Verified Billing page displays plans correctly with features

## Known Issues

### P0 - Critical
- Instagram OAuth needs proper Meta App configuration (App ID, Secret, redirect_uri)
- Meta App Review required for production use

### P1 - High
- Email sending requires valid Resend API key with full access
- Sender email must be from verified domain

### P2 - Medium
- WebSocket 404 errors in logs (admin-ws endpoint)

## Environment Variables

### Backend (.env)
- MONGO_URL
- DB_NAME
- JWT_SECRET
- EMERGENT_LLM_KEY
- STRIPE_API_KEY
- RESEND_API_KEY
- SENDER_EMAIL

### Frontend (.env)
- REACT_APP_BACKEND_URL

## API Endpoints

### User APIs
- POST /api/auth/login - User login
- POST /api/auth/register - User registration
- GET /api/accounts - Get user's Instagram accounts
- GET /api/instagram/auth/url - Get Instagram OAuth URL
- GET /api/instagram/callback - OAuth callback handler
- GET /api/plans - Get subscription plans

### Admin APIs
- POST /api/admin-panel/auth/login - Admin login
- GET /api/admin-panel/settings - Get system settings
- PUT /api/admin-panel/settings - Update system settings
- POST /api/admin-panel/settings/test-connection - Test API connections

## Credentials (Staging)

### Test User
- Email: gurpreets87400@gmail.com
- Password: Nikka@123

### Admin
- Email: superadmin@instagrowth.com
- Password: SuperAdmin123!
- Security Code: INSTAGROWTH_ADMIN_2024
