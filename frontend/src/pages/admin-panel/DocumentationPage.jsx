import React, { useState } from 'react';
import { 
  Book, Users, CreditCard, Package, BarChart3, Cpu, 
  FileText, Settings, Shield, ChevronDown, ChevronRight,
  Search, HelpCircle, ExternalLink, Copy, Check, Gift, 
  Mail, Megaphone, MessageSquare, Instagram, Sparkles,
  Calendar, Target, Zap, DollarSign
} from 'lucide-react';

const DocumentationPage = () => {
  const [expandedSection, setExpandedSection] = useState('getting-started');
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedText, setCopiedText] = useState('');

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(''), 2000);
  };

  const sections = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: Book,
      content: [
        {
          title: 'Admin Panel Overview',
          description: 'The Admin Panel provides complete control over your InstaGrowth OS platform. You can manage users, subscriptions, plans, monitor AI usage, track revenue, manage referrals, email automation, announcements, and configure system settings.',
        },
        {
          title: 'Login Credentials',
          description: 'Access the admin panel at /admin-panel/login using your admin email, password, and security code.',
          code: 'URL: /admin-panel/login\nEmail: superadmin@instagrowth.com\nPassword: SuperAdmin123!\nSecurity Code: INSTAGROWTH_ADMIN_2024'
        },
        {
          title: 'Admin Roles',
          description: 'Three role levels exist: Super Admin (full access), Support (users, tickets & logs), Finance (subscriptions, revenue & referrals).',
        },
        {
          title: 'Navigation',
          description: 'The sidebar contains all management sections. Key areas include Dashboard, Users, Subscriptions, Plans, Instagram, AI Usage, Revenue, Support Tickets, Referrals, Announcements, Email Automation, Team Management, System Settings, and Logs.',
        }
      ]
    },
    {
      id: 'dashboard',
      title: 'Dashboard',
      icon: BarChart3,
      content: [
        {
          title: 'Overview Stats',
          description: 'The dashboard displays key metrics:',
          list: [
            'Total Users: All registered accounts',
            'Active Subscriptions: Paid subscribers',
            'Instagram Accounts: Connected IG accounts',
            'AI Requests Today: Daily AI usage count'
          ]
        },
        {
          title: 'Revenue Chart',
          description: 'Shows revenue trends over the last 30 days. Hover over data points to see exact values.',
        },
        {
          title: 'User Growth Chart',
          description: 'Displays new user registrations over time. Helps identify growth patterns and marketing effectiveness.',
        },
        {
          title: 'Plan Distribution',
          description: 'Pie chart showing how users are distributed across different subscription plans (Free, Starter, Pro, Agency, Enterprise).',
        }
      ]
    },
    {
      id: 'users',
      title: 'User Management',
      icon: Users,
      content: [
        {
          title: 'View All Users',
          description: 'Access the complete list of registered users with their email, plan, accounts count, AI credits, and join date.',
        },
        {
          title: 'Search & Filter',
          description: 'Use the search box to find users by name or email. Use the plan filter dropdown to show users on specific plans.',
        },
        {
          title: 'Change User Plan',
          description: 'Click the plan dropdown next to any user to upgrade or downgrade their subscription plan. This also adjusts their AI credits.',
          steps: ['1. Find the user in the list', '2. Click the plan dropdown', '3. Select new plan', '4. Confirm the change']
        },
        {
          title: 'Block/Unblock User',
          description: 'Click the ban icon to suspend a user account. Blocked users cannot log in until unblocked.',
        },
        {
          title: 'Reset AI Credits',
          description: 'Manually reset a user\'s AI credits if needed. Useful for support cases or promotions.',
        },
        {
          title: 'Export Users',
          description: 'Click "Export CSV" to download a spreadsheet of all users for reporting or analysis.',
        }
      ]
    },
    {
      id: 'subscriptions',
      title: 'Subscription Management',
      icon: CreditCard,
      content: [
        {
          title: 'Active Subscriptions',
          description: 'View all active subscriptions with their status, plan, billing period, and payment information.',
        },
        {
          title: 'Cancel Subscription',
          description: 'Cancel a user subscription. The user will retain access until the end of their billing period.',
        },
        {
          title: 'Subscription Status',
          description: 'Status types:',
          list: [
            'Active: Currently paying',
            'Trialing: In free trial period',
            'Past Due: Payment failed',
            'Cancelled: Will end at period end',
            'Expired: No longer active'
          ]
        },
        {
          title: 'Sync with Stripe',
          description: 'If subscription data seems outdated, use the sync button to refresh from Stripe.',
        }
      ]
    },
    {
      id: 'plans',
      title: 'Plan Management',
      icon: Package,
      content: [
        {
          title: 'Available Plans',
          description: 'Default plans configured:',
          list: [
            'Free: $0/mo - 5 AI credits, 1 account',
            'Starter: $19/mo - 10 AI credits, 1 account',
            'Pro: $49/mo - 100 AI credits, 5 accounts',
            'Agency: $149/mo - 500 AI credits, 25 accounts, white-label',
            'Enterprise: $299/mo - 2000 AI credits, unlimited accounts'
          ]
        },
        {
          title: 'Create New Plan',
          description: 'Click "Create Plan" to add a new subscription tier.',
          steps: [
            '1. Click "Create Plan" button',
            '2. Enter plan name and monthly price',
            '3. Set Instagram account limit',
            '4. Set monthly AI credits',
            '5. Set team member limit',
            '6. Enable/disable white label',
            '7. Add feature bullet points',
            '8. Save the plan'
          ]
        },
        {
          title: 'AI Credit Costs',
          description: 'Each AI feature costs different credits:',
          list: [
            'AI Audit: 10 credits',
            'Growth Plan: 15 credits',
            'Competitor Analysis: 5 credits',
            'Content Ideas: 2 credits',
            'Caption/Hashtags/Hooks: 1 credit each',
            'DM Reply: 1 credit'
          ]
        }
      ]
    },
    {
      id: 'referrals',
      title: 'Referral Program',
      icon: Gift,
      content: [
        {
          title: 'Overview',
          description: 'The referral program allows users to earn credits and cash by referring new users. Access at /admin-panel/referrals.',
        },
        {
          title: 'Program Configuration',
          description: 'Current settings:',
          list: [
            'Referrer Reward: 50 AI credits per signup',
            'Referee Reward: 25 AI credits (welcome bonus)',
            'Commission Rate: 20% of first payment',
            'Minimum Payout: $50'
          ]
        },
        {
          title: 'Stats Dashboard',
          description: 'View key metrics:',
          list: [
            'Total Referrals: All referral signups',
            'Conversions: Referrals who became paid users',
            'Conversion Rate: Signup to paid ratio',
            'Total Paid Out: Commission payments made',
            'Pending Payouts: Awaiting approval'
          ]
        },
        {
          title: 'Top Referrers',
          description: 'See leaderboard of users with most successful referrals and highest earnings.',
        },
        {
          title: 'Payout Management',
          description: 'Process payout requests:',
          steps: [
            '1. View pending payouts in the list',
            '2. Click "Pay" to approve and mark as paid',
            '3. Click "Reject" to decline with reason',
            '4. Filter by status: Pending, Approved, Paid, Rejected'
          ]
        }
      ]
    },
    {
      id: 'email-automation',
      title: 'Email Automation',
      icon: Mail,
      content: [
        {
          title: 'Overview',
          description: 'Automated email system with 9 templates for user lifecycle. Access at /admin-panel/email-automation.',
        },
        {
          title: 'Email Templates',
          description: 'Available automated emails:',
          list: [
            'Welcome Email: Sent on user registration',
            'Subscription Activated: When user upgrades to paid plan',
            '7-Day Renewal Reminder: Before subscription renews',
            '3-Day Renewal Reminder: Urgent renewal notice',
            'Low Credits Alert: When AI credits < 20%',
            'Subscription Cancelled: Churn prevention email',
            'Weekly Digest: Growth report sent weekly',
            'Inactivity Reminder: After 7+ days inactive',
            'Referral Reward: When someone earns referral credits'
          ]
        },
        {
          title: 'Enable/Disable Templates',
          description: 'Toggle any template on/off. Disabled templates won\'t send to users.',
        },
        {
          title: 'Send Test Email',
          description: 'Test any template:',
          steps: [
            '1. Enter test email address at the top',
            '2. Click "Test" button on any template',
            '3. Check your inbox for the preview'
          ]
        },
        {
          title: 'View Email Logs',
          description: 'Click "Logs" tab to see all sent emails with:',
          list: [
            'Email type and recipient',
            'Subject line',
            'Status (Sent/Failed/Skipped)',
            'Timestamp',
            'Filter by type or status'
          ]
        },
        {
          title: 'Run Scheduled Tasks',
          description: 'Click "Run Scheduled Tasks" button to manually trigger:',
          list: [
            'Renewal reminder checks',
            'Low credits alerts',
            'Inactivity reminders'
          ]
        },
        {
          title: 'Preview Templates',
          description: 'Click the eye icon on any template to preview the HTML email design.',
        }
      ]
    },
    {
      id: 'announcements',
      title: 'Announcements',
      icon: Megaphone,
      content: [
        {
          title: 'Overview',
          description: 'Create in-app announcements shown on user dashboards. Access at /admin-panel/announcements.',
        },
        {
          title: 'Create Announcement',
          description: 'Click "New Announcement" to create:',
          steps: [
            '1. Enter title and message',
            '2. Select type (info, warning, success, update, maintenance)',
            '3. Choose target audience (all, free, paid, specific plan)',
            '4. Set optional start/end dates',
            '5. Add optional link URL and text',
            '6. Save and publish'
          ]
        },
        {
          title: 'Announcement Types',
          description: 'Different styles for different purposes:',
          list: [
            'Info: General announcements (blue)',
            'Warning: Important notices (yellow)',
            'Success: Positive news (green)',
            'Update: New features (blue)',
            'Maintenance: Scheduled downtime (orange)'
          ]
        },
        {
          title: 'Target Audiences',
          description: 'Show announcements to specific users:',
          list: [
            'All Users: Everyone sees it',
            'Free Users: Non-paying users only',
            'Paid Users: Subscribers only',
            'Starter/Pro/Agency: Specific plan users'
          ]
        },
        {
          title: 'Edit/Delete',
          description: 'Click edit icon to modify or trash icon to delete announcements.',
        }
      ]
    },
    {
      id: 'support-tickets',
      title: 'Support Tickets',
      icon: MessageSquare,
      content: [
        {
          title: 'Overview',
          description: 'Manage user support requests at /admin-panel/tickets.',
        },
        {
          title: 'Ticket List',
          description: 'View all tickets with:',
          list: [
            'Ticket ID and subject',
            'User who created it',
            'Category and priority',
            'Status (Open, In Progress, Resolved, Closed)',
            'Created date'
          ]
        },
        {
          title: 'Respond to Tickets',
          description: 'Click any ticket to view details and reply. Users receive email notification on reply.',
        },
        {
          title: 'Update Status',
          description: 'Change ticket status as you work on it. Mark as resolved when complete.',
        },
        {
          title: 'Priority Levels',
          description: 'Tickets have priority: Low, Medium, High, Urgent. Sort by priority to handle urgent issues first.',
        }
      ]
    },
    {
      id: 'revenue',
      title: 'Revenue Analytics',
      icon: DollarSign,
      content: [
        {
          title: 'Key Metrics',
          description: 'Track important revenue metrics:',
          list: [
            'MRR (Monthly Recurring Revenue): Total monthly subscription income',
            'ARR (Annual Recurring Revenue): MRR × 12',
            'Churn Rate: Percentage of cancellations',
            'ARPU (Average Revenue Per User): Revenue / Users'
          ]
        },
        {
          title: 'Revenue by Plan',
          description: 'See revenue breakdown by subscription plan to identify your most profitable tiers.',
        },
        {
          title: 'Growth Trends',
          description: 'Monitor revenue growth over time to track business health.',
        },
        {
          title: 'Referral Commissions',
          description: 'Track commission payouts and their impact on revenue.',
        }
      ]
    },
    {
      id: 'ai-usage',
      title: 'AI Usage Monitoring',
      icon: Cpu,
      content: [
        {
          title: 'Usage Overview',
          description: 'Monitor AI consumption across the platform:',
          list: [
            'Requests Today: AI calls made today',
            'Requests This Month: Monthly total',
            'Estimated Cost: Based on API pricing',
            'Usage by Feature: Breakdown by AI feature type'
          ]
        },
        {
          title: 'Credit Costs',
          description: 'AI feature credit costs:',
          list: [
            'AI Audit: 10 credits',
            'Growth Plan: 15 credits',
            'Competitor Analysis: 5 credits',
            'Posting Recommendations: 3 credits',
            'Content Ideas: 2 credits',
            'A/B Test: 2 credits',
            'Caption/Hashtags/Hooks/DM: 1 credit each'
          ]
        },
        {
          title: 'Top Users',
          description: 'See which users consume the most AI credits. Useful for identifying heavy users or potential abuse.',
        },
        {
          title: 'Feature Breakdown',
          description: 'Understand which AI features (audits, content, growth plans) are most popular.',
        }
      ]
    },
    {
      id: 'instagram',
      title: 'Instagram Accounts',
      icon: Instagram,
      content: [
        {
          title: 'Connected Accounts',
          description: 'View all Instagram accounts connected by users with:',
          list: [
            'Username and profile',
            'Owner (user who connected)',
            'Connection method (OAuth or Manual)',
            'Follower/following counts',
            'Connection date'
          ]
        },
        {
          title: 'Account Limits',
          description: 'Users can connect accounts based on their plan:',
          list: [
            'Free/Starter: 1 account',
            'Pro: 5 accounts',
            'Agency: 25 accounts',
            'Enterprise: Unlimited'
          ]
        },
        {
          title: 'Disconnect Account',
          description: 'Admins can disconnect accounts if needed for security or support reasons.',
        }
      ]
    },
    {
      id: 'logs',
      title: 'Activity Logs',
      icon: FileText,
      content: [
        {
          title: 'Admin Actions',
          description: 'All admin actions are logged for security and audit purposes.',
        },
        {
          title: 'Log Information',
          description: 'Each log entry contains:',
          list: [
            'Admin name and email',
            'Action performed',
            'Target (user/plan affected)',
            'IP address',
            'Timestamp'
          ]
        },
        {
          title: 'Filter Logs',
          description: 'Filter by action type (user_update, plan_change, etc.) to find specific events.',
        },
        {
          title: 'Export Logs',
          description: 'Export logs for compliance or security audits.',
        }
      ]
    },
    {
      id: 'settings',
      title: 'System Settings',
      icon: Settings,
      content: [
        {
          title: 'Access Control',
          description: 'Only Super Admins can access system settings. Other admins will see a permission error.',
          warning: 'Super Admin access required'
        },
        {
          title: 'Platform Settings',
          description: 'Configure:',
          list: [
            'Platform Name: Your SaaS name',
            'Support Email: Contact email for users',
            'Default AI Model: GPT model selection',
            'Maintenance Mode: Enable to show maintenance page'
          ]
        },
        {
          title: 'API Keys',
          description: 'Manage third-party API integrations:',
          list: [
            'OpenAI API Key: For AI features (or use Emergent Key)',
            'Stripe API Keys: For payments (publishable + secret)',
            'Resend API Key: For email sending',
            'Meta/Instagram API: For Instagram OAuth'
          ],
          warning: 'Keep API keys secure. Never share them publicly.'
        },
        {
          title: 'Stripe Configuration',
          description: 'To enable payments:',
          steps: [
            '1. Create Stripe account at stripe.com',
            '2. Get API keys from Stripe Dashboard',
            '3. Add Publishable Key and Secret Key',
            '4. Create products/prices in Stripe',
            '5. Add Price IDs to each plan'
          ]
        },
        {
          title: 'Email Configuration',
          description: 'To enable email sending:',
          steps: [
            '1. Create Resend account',
            '2. Verify your domain',
            '3. Add API key to settings',
            '4. Update sender email address'
          ]
        }
      ]
    },
    {
      id: 'security',
      title: 'Security',
      icon: Shield,
      content: [
        {
          title: 'Admin Authentication',
          description: 'Admin login requires three factors: Email, Password, and Security Code for enhanced security.',
        },
        {
          title: 'Session Management',
          description: 'Admin sessions expire after 8 hours of inactivity. You will be redirected to login.',
        },
        {
          title: 'Audit Trail',
          description: 'All admin actions are logged with IP addresses for security monitoring.',
        },
        {
          title: 'User Security',
          description: 'User security features:',
          list: [
            'Email verification required',
            'Optional 2FA with TOTP',
            'Password reset via email',
            'Session management',
            'Login rate limiting'
          ]
        },
        {
          title: 'Best Practices',
          description: 'Security recommendations:',
          list: [
            'Use strong, unique passwords',
            'Never share admin credentials',
            'Log out when done',
            'Review activity logs regularly',
            'Report suspicious activity immediately',
            'Keep API keys in environment variables',
            'Enable 2FA for admin accounts'
          ]
        }
      ]
    }
  ];

  const filteredSections = searchQuery
    ? sections.filter(section => 
        section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.content.some(item => 
          item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.description.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    : sections;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Admin Documentation</h1>
          <p className="text-white/50 mt-1">Complete guide to managing InstaGrowth OS</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-white/40">
          <span>Last updated: Feb 8, 2025</span>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
        <input
          type="text"
          placeholder="Search documentation..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      {/* Content */}
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <div className="bg-[#1e293b] border border-white/10 rounded-xl p-4 sticky top-6">
            <h3 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-4">Sections</h3>
            <nav className="space-y-1 max-h-[60vh] overflow-y-auto">
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setExpandedSection(section.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                      expandedSection === section.id
                        ? 'bg-indigo-500/20 text-indigo-400'
                        : 'text-white/70 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span className="text-sm truncate">{section.title}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-4">
          {filteredSections.map((section) => {
            const Icon = section.icon;
            const isExpanded = expandedSection === section.id;
            
            return (
              <div
                key={section.id}
                className="bg-[#1e293b] border border-white/10 rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => setExpandedSection(isExpanded ? '' : section.id)}
                  className="w-full flex items-center justify-between p-5 hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-500/20 rounded-lg">
                      <Icon className="w-5 h-5 text-indigo-400" />
                    </div>
                    <h2 className="text-lg font-semibold text-white">{section.title}</h2>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-5 h-5 text-white/50" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-white/50" />
                  )}
                </button>
                
                {isExpanded && (
                  <div className="px-5 pb-5 space-y-6">
                    {section.content.map((item, idx) => (
                      <div key={idx} className="pl-12">
                        <h3 className="text-base font-medium text-white mb-2">{item.title}</h3>
                        <p className="text-white/60 text-sm leading-relaxed">{item.description}</p>
                        
                        {item.code && (
                          <div className="mt-3 relative">
                            <pre className="bg-black/30 rounded-lg p-4 text-sm text-green-400 font-mono overflow-x-auto">
                              {item.code}
                            </pre>
                            <button
                              onClick={() => copyToClipboard(item.code)}
                              className="absolute top-2 right-2 p-2 hover:bg-white/10 rounded"
                            >
                              {copiedText === item.code ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4 text-white/50" />
                              )}
                            </button>
                          </div>
                        )}
                        
                        {item.steps && (
                          <ol className="mt-3 space-y-2">
                            {item.steps.map((step, stepIdx) => (
                              <li key={stepIdx} className="text-white/60 text-sm flex items-start gap-2">
                                <span className="text-indigo-400 font-medium min-w-[20px]">{stepIdx + 1}.</span>
                                <span>{step.replace(/^\d+\.\s*/, '')}</span>
                              </li>
                            ))}
                          </ol>
                        )}
                        
                        {item.list && (
                          <ul className="mt-3 space-y-2">
                            {item.list.map((listItem, listIdx) => (
                              <li key={listIdx} className="text-white/60 text-sm flex items-start gap-2">
                                <span className="text-indigo-400 mt-1">•</span>
                                <span>{listItem}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                        
                        {item.warning && (
                          <div className="mt-3 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                            <p className="text-amber-400 text-sm flex items-center gap-2">
                              <HelpCircle className="w-4 h-4 flex-shrink-0" />
                              {item.warning}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Reference Card */}
      <div className="bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border border-indigo-500/20 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-indigo-400" />
          Quick Reference
        </h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">Admin Roles</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Super Admin: Full access</li>
              <li>• Support: Users, Tickets & Logs</li>
              <li>• Finance: Revenue & Plans</li>
            </ul>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">Key URLs</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Admin: /admin-panel</li>
              <li>• Referrals: /admin-panel/referrals</li>
              <li>• Emails: /admin-panel/email-automation</li>
            </ul>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">Plan Pricing</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Starter: $19/mo</li>
              <li>• Pro: $49/mo</li>
              <li>• Agency: $149/mo</li>
              <li>• Enterprise: $299/mo</li>
            </ul>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">AI Credit Costs</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Audit: 10 credits</li>
              <li>• Growth Plan: 15 credits</li>
              <li>• Competitor: 5 credits</li>
              <li>• Content: 1-2 credits</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentationPage;
