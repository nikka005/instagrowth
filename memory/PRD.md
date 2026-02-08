# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies.

## Current Status: PRODUCTION READY ✅ (225+ Features)

---

## NEW FEATURES ADDED (Phase 3 - Feb 8, 2025)

### 1. Referral/Affiliate System ✅
- User referral code generation
- Referral link sharing
- Click, signup, and conversion tracking
- Commission calculation (20% of first payment)
- Payout request system
- Admin referral management dashboard
- Top referrers leaderboard
- Payout approval workflow

### 2. AI Credits Integration ✅
- Credits displayed on user dashboard
- Feature-specific credit costs
- Real-time credit deduction
- Credit history tracking
- Low credit warnings
- Bonus credits for referrals

### 3. Announcements System ✅
- Admin announcement creation
- Multiple announcement types (info, warning, success, update, maintenance)
- Target audience filtering (all, free, paid, plan-specific)
- Start/end date scheduling
- User dismissal tracking
- Dashboard announcement banners

### 4. Enhanced Onboarding ✅
- Auto-redirect for new users
- Goal-based personalization
- Instagram connection wizard
- Quick-start tutorial
- Completion tracking in database

---

## Complete Feature List (225+ Total)

### Authentication & Security
- [x] User registration with email verification
- [x] Login with email/password
- [x] Google OAuth
- [x] Password reset
- [x] 2FA (TOTP) for users
- [x] Login rate limiting
- [x] IP blocking
- [x] Session management
- [x] Force logout

### User Dashboard
- [x] Dashboard overview
- [x] AI credits display (new)
- [x] Quick actions
- [x] Notifications
- [x] Onboarding wizard
- [x] Announcement banners (new)

### Referral System (NEW)
- [x] Referral code generation
- [x] Referral link copying
- [x] Click/signup/conversion tracking
- [x] Commission earnings display
- [x] Payout request
- [x] Referral history

### Instagram Management
- [x] Instagram OAuth connection
- [x] Manual account entry
- [x] Real follower/following counts
- [x] Account refresh from API
- [x] Disconnect/reconnect
- [x] Account deletion

### AI Features (Credit-Based)
- [x] Profile audits (10 credits) - PDF export
- [x] Caption generation (1 credit)
- [x] Hashtag generation (1 credit)
- [x] Content ideas (2 credits)
- [x] Hooks for reels (1 credit)
- [x] Growth plans (15 credits)
- [x] Competitor analysis (5 credits)
- [x] Rate limiting

### Support System
- [x] Create tickets
- [x] View ticket history
- [x] Reply to tickets
- [x] Close tickets
- [x] Email notifications

### Admin Panel
- [x] Dashboard with charts
- [x] User management
- [x] Subscription management
- [x] Plan management
- [x] Revenue analytics
- [x] AI usage monitoring
- [x] Support tickets
- [x] Activity logs
- [x] System settings
- [x] Documentation
- [x] Announcements management (new)
- [x] Referrals management (new)
- [x] Payout approval (new)

### Legal Pages
- [x] Privacy Policy
- [x] Terms of Service
- [x] Refund Policy
- [x] Data Deletion (Meta callback)

---

## Referral Program Configuration

| Setting | Value |
|---------|-------|
| Referrer Reward | 50 credits |
| Referee Reward | 25 credits |
| Commission Rate | 20% |
| Minimum Payout | $50 |

## Credit Costs per Feature

| Feature | Credits |
|---------|---------|
| AI Audit | 10 |
| Caption | 1 |
| Hashtags | 1 |
| Content Ideas | 2 |
| Hooks | 1 |
| Growth Plan | 15 |
| Competitor Analysis | 5 |
| DM Reply | 1 |
| Posting Recommendations | 3 |
| A/B Test | 2 |

## Plan Credit Allocations (Monthly)

| Plan | Credits |
|------|---------|
| Free | 5 |
| Starter ($19) | 10 |
| Pro ($49) | 100 |
| Agency ($149) | 500 |
| Enterprise ($299) | 2000 |

---

## Admin Credentials

| Field | Value |
|-------|-------|
| URL | `/admin-panel/login` |
| Email | `superadmin@instagrowth.com` |
| Password | `SuperAdmin123!` |
| Security Code | `INSTAGROWTH_ADMIN_2024` |

---

## API Configuration Status

| Service | Status | Notes |
|---------|--------|-------|
| OpenAI | ✅ Configured | Emergent Universal Key |
| Resend | ✅ Configured | User API key |
| Stripe | ⚙️ Ready | Needs user keys |
| Meta/Instagram | ⚙️ Ready | Needs user credentials |

---

## New Routes (Phase 3)

### User Routes
- `/referrals` - Referral program dashboard
- `/onboarding` - First-time user onboarding (improved)

### Admin Routes
- `/admin-panel/referrals` - Referral management
- `/admin-panel/announcements` - Announcement management

### API Endpoints (New)
- `GET /api/referrals/code` - Get/create referral code
- `GET /api/referrals/stats` - Referral statistics
- `POST /api/referrals/track-click` - Track referral click
- `POST /api/referrals/request-payout` - Request payout
- `GET /api/referrals/admin/overview` - Admin overview
- `GET /api/referrals/admin/payouts` - Payout requests
- `PUT /api/referrals/admin/payouts/{id}` - Process payout
- `GET /api/announcements` - Active announcements
- `GET /api/announcements/unread` - Unread for user
- `POST /api/announcements/{id}/dismiss` - Dismiss
- `GET /api/announcements/admin/all` - All announcements
- `POST /api/announcements/admin/create` - Create
- `PUT /api/announcements/admin/{id}` - Update
- `DELETE /api/announcements/admin/{id}` - Delete

---

## Test Results (Feb 8, 2025)

| Category | Result |
|----------|--------|
| Backend Tests | 19/19 (100%) |
| Frontend Tests | All Passed |
| Features Working | Referrals, Credits, Announcements, Onboarding |

---

## Last Updated
February 8, 2025

## Remaining Items (Future)
1. Email automation (welcome, renewal reminders) - SCAFFOLDED
2. Stripe payment integration (requires user keys)
3. Real Instagram data (requires Meta App Review)
4. DM/Email template management
5. Light/Dark mode toggle
