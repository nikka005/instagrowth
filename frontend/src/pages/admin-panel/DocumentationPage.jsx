import React, { useState } from 'react';
import { 
  Book, Users, CreditCard, Package, BarChart3, Cpu, 
  FileText, Settings, Shield, ChevronDown, ChevronRight,
  Search, HelpCircle, ExternalLink, Copy, Check
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
          description: 'The Admin Panel provides complete control over your InstaGrowth OS platform. You can manage users, subscriptions, plans, monitor AI usage, track revenue, and configure system settings.',
        },
        {
          title: 'Login Credentials',
          description: 'Access the admin panel at /admin-panel/login using your admin email, password, and security code. Contact the super admin to get your credentials.',
          code: 'URL: /admin-panel/login\nEmail: your-admin@email.com\nPassword: your-password\nSecurity Code: INSTAGROWTH_ADMIN_2024'
        },
        {
          title: 'Admin Roles',
          description: 'Three role levels exist: Super Admin (full access), Support (users & logs), Finance (subscriptions & revenue).',
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
          description: 'The dashboard displays key metrics: Total Users, Active Subscriptions, Instagram Accounts connected, and AI Requests today.',
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
          description: 'Pie chart showing how users are distributed across different subscription plans (Starter, Pro, Agency, Enterprise).',
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
          description: 'Access the complete list of registered users with their email, plan, accounts count, AI usage, and join date.',
        },
        {
          title: 'Search & Filter',
          description: 'Use the search box to find users by name or email. Use the plan filter dropdown to show users on specific plans.',
        },
        {
          title: 'Change User Plan',
          description: 'Click the plan dropdown next to any user to upgrade or downgrade their subscription plan.',
          steps: ['1. Find the user in the list', '2. Click the plan dropdown', '3. Select new plan', '4. Confirm the change']
        },
        {
          title: 'Block/Unblock User',
          description: 'Click the ban icon to suspend a user account. Blocked users cannot log in until unblocked.',
        },
        {
          title: 'Delete User',
          description: 'Permanently remove a user account. This action cannot be undone. All user data will be deleted.',
          warning: 'Warning: This action is irreversible!'
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
          title: 'View Plans',
          description: 'See all subscription plans with their pricing, limits, and active subscriber count.',
        },
        {
          title: 'Create New Plan',
          description: 'Click "Create Plan" to add a new subscription tier.',
          steps: [
            '1. Click "Create Plan" button',
            '2. Enter plan name and price',
            '3. Set account limit (Instagram accounts)',
            '4. Set AI credits limit',
            '5. Set team member limit',
            '6. Enable/disable white label',
            '7. Add features list',
            '8. Save the plan'
          ]
        },
        {
          title: 'Edit Plan',
          description: 'Click "Edit" on any plan to modify its settings. Changes apply to new subscribers.',
        },
        {
          title: 'Disable Plan',
          description: 'Disable a plan to prevent new signups while keeping existing subscribers active.',
        },
        {
          title: 'Plan Limits',
          description: 'Each plan defines: Account Limit (max Instagram accounts), AI Credits (monthly AI requests), Team Members (collaborators), White Label (branding removal).',
        }
      ]
    },
    {
      id: 'revenue',
      title: 'Revenue Analytics',
      icon: BarChart3,
      content: [
        {
          title: 'Key Metrics',
          description: 'Track important revenue metrics:',
          list: [
            'MRR (Monthly Recurring Revenue): Total monthly subscription income',
            'ARR (Annual Recurring Revenue): MRR × 12',
            'Churn Rate: Percentage of cancellations',
            'ARPU (Average Revenue Per User): Revenue divided by users'
          ]
        },
        {
          title: 'Revenue by Plan',
          description: 'See revenue breakdown by subscription plan to identify your most profitable tiers.',
        },
        {
          title: 'Growth Trends',
          description: 'Monitor revenue growth over time to track business health.',
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
            'Default AI Model: GPT model selection'
          ]
        },
        {
          title: 'API Keys',
          description: 'Manage third-party API integrations:',
          list: [
            'OpenAI API Key: For AI features',
            'Stripe API Key: For payments',
            'Resend API Key: For emails',
            'Meta API Key: For Instagram integration'
          ],
          warning: 'Keep API keys secure. Never share them.'
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
          title: 'Best Practices',
          description: 'Security recommendations:',
          list: [
            'Use strong, unique passwords',
            'Never share admin credentials',
            'Log out when done',
            'Review activity logs regularly',
            'Report suspicious activity immediately'
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
          <p className="text-white/50 mt-1">Complete guide to using the admin panel</p>
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
            <nav className="space-y-1">
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
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{section.title}</span>
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
                                <span className="text-indigo-400 font-medium">{stepIdx + 1}.</span>
                                {step.replace(/^\d+\.\s*/, '')}
                              </li>
                            ))}
                          </ol>
                        )}
                        
                        {item.list && (
                          <ul className="mt-3 space-y-2">
                            {item.list.map((listItem, listIdx) => (
                              <li key={listIdx} className="text-white/60 text-sm flex items-start gap-2">
                                <span className="text-indigo-400 mt-1">•</span>
                                {listItem}
                              </li>
                            ))}
                          </ul>
                        )}
                        
                        {item.warning && (
                          <div className="mt-3 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                            <p className="text-amber-400 text-sm flex items-center gap-2">
                              <HelpCircle className="w-4 h-4" />
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
              <li>• Support: Users & Logs</li>
              <li>• Finance: Revenue & Plans</li>
            </ul>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">Session Info</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Session: 8 hours</li>
              <li>• Auto-logout on idle</li>
              <li>• All actions logged</li>
            </ul>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">Keyboard Shortcuts</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Ctrl+K: Search</li>
              <li>• Esc: Close modal</li>
              <li>• Tab: Navigate</li>
            </ul>
          </div>
          <div className="bg-black/20 rounded-lg p-4">
            <h4 className="text-sm font-medium text-white/80 mb-2">Need Help?</h4>
            <ul className="text-xs text-white/50 space-y-1">
              <li>• Check activity logs</li>
              <li>• Contact super admin</li>
              <li>• Review this guide</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentationPage;
