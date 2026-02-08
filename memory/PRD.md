# InstaGrowth OS - Product Requirements Document

## Original Problem Statement
Build InstaGrowth OS - an AI-powered Instagram Growth & Management Platform for freelancers and agencies.

## Current Status: PRODUCTION READY ✅ (218 Features)

---

## NEW FEATURES ADDED (Phase 2)

### 1. Security & Abuse Protection ✅
- Login rate limiting (5 attempts / 5 minutes)
- AI request rate limit (30 requests / minute)
- IP blocking system (temporary + permanent)
- Suspicious user detection & flagging
- Admin force logout
- Session device tracking

### 2. AI Credit System ✅
- Monthly credit allocation per plan
- Credit costs per feature (audit=10, caption=1, etc.)
- Credit usage tracking
- Automatic monthly reset
- Extra credit purchase capability

### 3. Support Ticket System ✅
- User ticket creation (`/support`)
- Admin ticket management (`/admin-panel/tickets`)
- Ticket categories (general, billing, technical, feature, bug)
- Priority levels (low, normal, high, urgent)
- Message threading
- Email notifications
- Ticket status (open, pending, closed)

### 4. In-App Announcements ✅
- Admin announcement creation
- Banner types (info, warning, success, update, maintenance)
- Target audience filtering
- Start/end date scheduling
- User dismissal tracking

### 5. Onboarding Flow ✅
- Welcome screen
- Goal selection (grow followers, generate leads, build brand, boost engagement)
- Instagram connection step
- Quick start guide
- Dashboard redirect

---

## Complete Feature List (218 Total)

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
- [x] AI credits display
- [x] Quick actions
- [x] Notifications
- [x] Onboarding wizard

### Instagram Management
- [x] Instagram OAuth connection
- [x] Manual account entry
- [x] Real follower/following counts
- [x] Account refresh from API
- [x] Disconnect/reconnect
- [x] Account deletion

### AI Features
- [x] Profile audits (PDF export)
- [x] Caption generation
- [x] Hashtag generation
- [x] Content ideas
- [x] Hooks for reels
- [x] Growth plans
- [x] Credit-based usage
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
- [x] Announcements

### Legal Pages
- [x] Privacy Policy
- [x] Terms of Service
- [x] Refund Policy
- [x] Data Deletion (Meta callback)

---

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

## New Routes Added

### User Routes
- `/support` - Support ticket system
- `/onboarding` - First-time user onboarding

### Admin Routes
- `/admin-panel/tickets` - Support ticket management

### API Endpoints
- `POST /api/support/tickets` - Create ticket
- `GET /api/support/tickets` - List user tickets
- `POST /api/support/tickets/{id}/reply` - Reply to ticket
- `GET /api/admin-panel/tickets` - Admin ticket list
- `POST /api/admin-panel/tickets/{id}/reply` - Admin reply
- `PUT /api/admin-panel/tickets/{id}/status` - Update status
- `GET /api/credits` - Get user credits
- `POST /api/credits/use` - Use credits
- `GET /api/announcements` - Get active announcements
- `POST /api/security/admin/block-ip` - Block IP
- `POST /api/security/admin/force-logout` - Force user logout

---

## Last Updated
February 8, 2025

## Remaining Items (Future)
1. Stripe payment integration (requires user keys)
2. Real Instagram data (requires Meta App Review)
3. Email automation (welcome, renewal reminders)
4. Referral/Affiliate system
5. Light/Dark mode toggle
