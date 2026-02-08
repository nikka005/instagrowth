import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Book, Instagram, BarChart3, Sparkles, Calendar, MessageSquare,
  Target, FlaskConical, Gift, CreditCard, Settings, Search,
  ChevronDown, ChevronRight, HelpCircle, ExternalLink, Play,
  Zap, Users, TrendingUp, FileText, CheckCircle2, ArrowRight
} from "lucide-react";
import DashboardLayout from "../components/DashboardLayout";

const HelpCenterPage = ({ auth }) => {
  const [expandedSection, setExpandedSection] = useState('getting-started');
  const [searchQuery, setSearchQuery] = useState('');

  const sections = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: Book,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/20',
      content: [
        {
          title: 'Welcome to InstaGrowth OS!',
          description: 'InstaGrowth OS is your AI-powered Instagram growth platform. Here\'s how to get the most out of it.',
        },
        {
          title: 'Quick Start (5 Minutes)',
          steps: [
            'Connect your Instagram account',
            'Run your first AI audit to see your account health',
            'Generate content ideas for your niche',
            'Create a 7-day growth plan',
            'Start posting and growing!'
          ]
        },
        {
          title: 'Understanding AI Credits',
          description: 'AI features use credits from your monthly allowance. Different features cost different amounts:',
          list: [
            'AI Audit: 10 credits - Full account analysis',
            'Growth Plan: 15 credits - Personalized roadmap',
            'Competitor Analysis: 5 credits - Spy on competitors',
            'Content Ideas: 2 credits - Viral reel ideas',
            'Captions/Hashtags/Hooks: 1 credit each'
          ]
        },
        {
          title: 'Your Plan',
          description: 'Check your current plan and limits on the Billing page. Upgrade anytime to get more credits and accounts.',
        }
      ]
    },
    {
      id: 'accounts',
      title: 'Instagram Accounts',
      icon: Instagram,
      color: 'text-pink-400',
      bg: 'bg-pink-500/20',
      content: [
        {
          title: 'Connecting Your Account',
          description: 'There are two ways to connect your Instagram:',
          list: [
            'OAuth (Recommended): Click "Connect with Instagram" for secure official connection',
            'Manual Entry: Enter your username and niche for basic features'
          ]
        },
        {
          title: 'OAuth Connection Steps',
          steps: [
            'Click "Connect Instagram Account"',
            'Login to your Instagram/Facebook',
            'Grant permission to InstaGrowth OS',
            'Your account is connected!'
          ]
        },
        {
          title: 'Account Limits by Plan',
          list: [
            'Free/Starter: 1 Instagram account',
            'Pro: Up to 5 accounts',
            'Agency: Up to 25 accounts',
            'Enterprise: Unlimited accounts'
          ]
        },
        {
          title: 'Refreshing Account Data',
          description: 'Click the refresh icon on any account to update follower counts and metrics from Instagram.',
        },
        {
          title: 'Disconnecting Accounts',
          description: 'Click the disconnect icon to remove an account. You can reconnect it anytime.',
        }
      ]
    },
    {
      id: 'audit',
      title: 'AI Account Audit',
      icon: BarChart3,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/20',
      content: [
        {
          title: 'What is an AI Audit?',
          description: 'The AI Audit analyzes your Instagram account and provides a comprehensive health report with actionable insights.',
        },
        {
          title: 'What You Get',
          list: [
            'Overall Account Score (0-100)',
            'Engagement Rate Analysis',
            'Content Consistency Score',
            'Shadowban Risk Assessment',
            'Growth Mistakes Identified',
            'Personalized Recommendations',
            '30-Day Recovery Roadmap'
          ]
        },
        {
          title: 'How to Run an Audit',
          steps: [
            'Go to AI Audit page',
            'Select the account to audit',
            'Click "Generate Audit"',
            'Wait 30-60 seconds for AI analysis',
            'Review your comprehensive report'
          ]
        },
        {
          title: 'Export to PDF',
          description: 'Click "Download PDF" to get a professional report you can share with clients or team members.',
        },
        {
          title: 'Credit Cost',
          description: '10 credits per audit. Run audits monthly to track your progress.',
        }
      ]
    },
    {
      id: 'content',
      title: 'AI Content Engine',
      icon: Sparkles,
      color: 'text-teal-400',
      bg: 'bg-teal-500/20',
      content: [
        {
          title: 'Content Types',
          description: 'Generate multiple types of content:',
          list: [
            'Reel Ideas: Viral video concepts for your niche',
            'Viral Hooks: First 3 seconds that grab attention',
            'Captions: Engaging post captions with CTAs',
            'Hashtags: Curated hashtag clusters for reach'
          ]
        },
        {
          title: 'How to Generate Content',
          steps: [
            'Select content type (Reels, Hooks, Captions, etc.)',
            'Choose your Instagram account',
            'Add topic or let AI decide based on your niche',
            'Click "Generate"',
            'Copy and use in your posts!'
          ]
        },
        {
          title: 'Best Practices',
          list: [
            'Generate multiple options and pick the best',
            'Customize AI output to match your voice',
            'Mix trending and evergreen content',
            'Test different hooks to see what works'
          ]
        },
        {
          title: 'Credit Costs',
          description: 'Reel Ideas: 2 credits | Hooks: 1 credit | Captions: 1 credit | Hashtags: 1 credit',
        }
      ]
    },
    {
      id: 'growth',
      title: 'Growth Planner',
      icon: Calendar,
      color: 'text-orange-400',
      bg: 'bg-orange-500/20',
      content: [
        {
          title: 'What is Growth Planner?',
          description: 'Get a personalized day-by-day plan to grow your Instagram account with specific tasks and content ideas.',
        },
        {
          title: 'Plan Durations',
          list: [
            '7-Day Plan: Quick sprint for fast results',
            '14-Day Plan: Balanced growth strategy',
            '30-Day Plan: Comprehensive long-term growth'
          ]
        },
        {
          title: 'Creating a Growth Plan',
          steps: [
            'Go to Growth Planner',
            'Select your Instagram account',
            'Choose your growth goal',
            'Select plan duration (7/14/30 days)',
            'Click "Generate Plan"',
            'Follow daily tasks to grow!'
          ]
        },
        {
          title: 'What\'s Included',
          list: [
            'Daily content tasks',
            'Engagement activities',
            'Posting schedule',
            'Hashtag strategy',
            'Growth milestones',
            'Progress checkpoints'
          ]
        },
        {
          title: 'Export for Clients',
          description: 'Agency users can export branded PDF plans to share with clients.',
        },
        {
          title: 'Credit Cost',
          description: '15 credits per growth plan. Worth it for the comprehensive roadmap!',
        }
      ]
    },
    {
      id: 'dm-templates',
      title: 'DM Templates',
      icon: MessageSquare,
      color: 'text-purple-400',
      bg: 'bg-purple-500/20',
      content: [
        {
          title: 'What are DM Templates?',
          description: 'Save time with pre-written DM templates for common scenarios. AI can also generate custom replies.',
        },
        {
          title: 'Template Categories',
          list: [
            'Welcome Messages: Greet new followers',
            'Collaboration: Reach out to brands/influencers',
            'Sales: Pitch your products/services',
            'Support: Handle customer questions',
            'Follow-up: Nurture leads'
          ]
        },
        {
          title: 'Creating Templates',
          steps: [
            'Go to DM Templates',
            'Click "Create Template"',
            'Choose a category',
            'Write your message (use {name} for personalization)',
            'Save and use!'
          ]
        },
        {
          title: 'AI-Generated Replies',
          description: 'Click "Generate Reply" on any template to get AI-powered response suggestions based on incoming messages.',
        },
        {
          title: 'Credit Cost',
          description: 'AI Reply Generation: 1 credit per reply',
        }
      ]
    },
    {
      id: 'competitors',
      title: 'Competitor Analysis',
      icon: Target,
      color: 'text-red-400',
      bg: 'bg-red-500/20',
      content: [
        {
          title: 'Why Analyze Competitors?',
          description: 'Learn what\'s working for similar accounts and get actionable insights to outperform them.',
        },
        {
          title: 'Analysis Includes',
          list: [
            'Content Strategy Breakdown',
            'Posting Frequency & Timing',
            'Top Performing Content',
            'Hashtag Strategy',
            'Engagement Tactics',
            'Growth Opportunities You\'re Missing'
          ]
        },
        {
          title: 'How to Analyze',
          steps: [
            'Go to Competitors page',
            'Enter competitor\'s username',
            'Select your account for comparison',
            'Click "Analyze"',
            'Review insights and recommendations'
          ]
        },
        {
          title: 'Credit Cost',
          description: '5 credits per competitor analysis',
        }
      ]
    },
    {
      id: 'ab-testing',
      title: 'A/B Testing',
      icon: FlaskConical,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/20',
      content: [
        {
          title: 'What is A/B Testing?',
          description: 'Test different content variations to see what resonates best with your audience.',
        },
        {
          title: 'What You Can Test',
          list: [
            'Captions: Different styles and CTAs',
            'Hashtags: Different cluster combinations',
            'Hooks: Various opening lines',
            'Posting Times: Morning vs evening'
          ]
        },
        {
          title: 'Creating a Test',
          steps: [
            'Go to A/B Testing',
            'Select test type',
            'Enter Variation A and B',
            'Set test duration',
            'Launch test and track results'
          ]
        },
        {
          title: 'Credit Cost',
          description: '2 credits per A/B test',
        }
      ]
    },
    {
      id: 'referrals',
      title: 'Referral Program',
      icon: Gift,
      color: 'text-green-400',
      bg: 'bg-green-500/20',
      content: [
        {
          title: 'Earn by Referring',
          description: 'Share InstaGrowth OS with friends and earn credits and cash!',
        },
        {
          title: 'Rewards',
          list: [
            '50 AI Credits: When someone signs up with your link',
            '25 Credits for Friend: They get a welcome bonus too',
            '20% Commission: On their first payment',
            'Minimum Payout: $50 (request anytime after)'
          ]
        },
        {
          title: 'How It Works',
          steps: [
            'Go to Referrals page',
            'Copy your unique referral link',
            'Share with friends, social media, or your audience',
            'Earn credits when they sign up',
            'Earn commission when they subscribe'
          ]
        },
        {
          title: 'Tracking',
          description: 'Your Referrals page shows clicks, signups, conversions, and earnings in real-time.',
        },
        {
          title: 'Request Payout',
          description: 'Once you have $50+ in earnings, click "Request Payout" to get paid.',
        }
      ]
    },
    {
      id: 'billing',
      title: 'Billing & Plans',
      icon: CreditCard,
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/20',
      content: [
        {
          title: 'Available Plans',
          list: [
            'Free: 5 credits/month, 1 account - $0',
            'Starter: 10 credits/month, 1 account - $19/mo',
            'Pro: 100 credits/month, 5 accounts - $49/mo',
            'Agency: 500 credits/month, 25 accounts - $149/mo',
            'Enterprise: 2000 credits/month, unlimited - $299/mo'
          ]
        },
        {
          title: 'Upgrading Your Plan',
          steps: [
            'Go to Billing page',
            'Review plan comparison',
            'Click "Upgrade" on your chosen plan',
            'Enter payment details',
            'Enjoy increased limits!'
          ]
        },
        {
          title: 'Credit Reset',
          description: 'AI credits reset on the 1st of each month. Unused credits don\'t roll over.',
        },
        {
          title: 'Cancellation',
          description: 'You can cancel anytime. Access continues until the end of your billing period.',
        }
      ]
    },
    {
      id: 'support',
      title: 'Getting Help',
      icon: HelpCircle,
      color: 'text-blue-400',
      bg: 'bg-blue-500/20',
      content: [
        {
          title: 'Support Options',
          list: [
            'Help Center: You\'re here! Browse guides above',
            'Support Tickets: Submit a ticket for direct help',
            'Email: Contact support via email'
          ]
        },
        {
          title: 'Creating a Support Ticket',
          steps: [
            'Go to Support page',
            'Click "New Ticket"',
            'Select category and priority',
            'Describe your issue in detail',
            'Submit and wait for response'
          ]
        },
        {
          title: 'Response Times',
          list: [
            'Urgent: Within 2 hours',
            'High: Within 4 hours',
            'Medium: Within 24 hours',
            'Low: Within 48 hours'
          ]
        },
        {
          title: 'Before Contacting Support',
          description: 'Check this Help Center first - your question might already be answered!',
        }
      ]
    }
  ];

  const filteredSections = searchQuery
    ? sections.filter(section => 
        section.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        section.content.some(item => 
          item.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.description?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    : sections;

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto">
          <h1 className="font-display text-3xl md:text-4xl font-bold text-white mb-4">
            Help Center
          </h1>
          <p className="text-white/60 text-lg">
            Everything you need to know about using InstaGrowth OS
          </p>
        </div>

        {/* Search */}
        <div className="max-w-xl mx-auto">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
            <input
              type="text"
              placeholder="Search for help..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-white/30 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-lg"
            />
          </div>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: Instagram, label: 'Connect Account', section: 'accounts' },
            { icon: BarChart3, label: 'Run Audit', section: 'audit' },
            { icon: Sparkles, label: 'Create Content', section: 'content' },
            { icon: Gift, label: 'Earn Rewards', section: 'referrals' },
          ].map((item, idx) => (
            <button
              key={idx}
              onClick={() => setExpandedSection(item.section)}
              className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-indigo-500/50 hover:bg-indigo-500/10 transition-all text-center group"
            >
              <item.icon className="w-6 h-6 text-indigo-400 mx-auto mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-sm text-white/70 group-hover:text-white">{item.label}</span>
            </button>
          ))}
        </div>

        {/* Content Sections */}
        <div className="space-y-4">
          {filteredSections.map((section) => {
            const Icon = section.icon;
            const isExpanded = expandedSection === section.id;
            
            return (
              <motion.div
                key={section.id}
                initial={false}
                className="bg-[#0F0F11]/80 border border-white/5 rounded-2xl overflow-hidden"
              >
                <button
                  onClick={() => setExpandedSection(isExpanded ? '' : section.id)}
                  className="w-full flex items-center justify-between p-5 hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 ${section.bg} rounded-xl`}>
                      <Icon className={`w-6 h-6 ${section.color}`} />
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
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="px-5 pb-6 space-y-6"
                  >
                    {section.content.map((item, idx) => (
                      <div key={idx} className="pl-16">
                        {item.title && (
                          <h3 className="text-base font-medium text-white mb-2">{item.title}</h3>
                        )}
                        {item.description && (
                          <p className="text-white/60 text-sm leading-relaxed">{item.description}</p>
                        )}
                        
                        {item.steps && (
                          <ol className="mt-3 space-y-2">
                            {item.steps.map((step, stepIdx) => (
                              <li key={stepIdx} className="text-white/60 text-sm flex items-start gap-3">
                                <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs flex-shrink-0">
                                  {stepIdx + 1}
                                </span>
                                <span className="mt-0.5">{step}</span>
                              </li>
                            ))}
                          </ol>
                        )}
                        
                        {item.list && (
                          <ul className="mt-3 space-y-2">
                            {item.list.map((listItem, listIdx) => (
                              <li key={listIdx} className="text-white/60 text-sm flex items-start gap-2">
                                <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                                <span>{listItem}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Credit Costs Summary */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 via-purple-600/20 to-pink-600/20 border border-indigo-500/20">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-indigo-400" />
            AI Credit Costs Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { feature: 'AI Audit', credits: 10, color: 'text-indigo-400' },
              { feature: 'Growth Plan', credits: 15, color: 'text-orange-400' },
              { feature: 'Competitor Analysis', credits: 5, color: 'text-red-400' },
              { feature: 'Content Ideas', credits: 2, color: 'text-teal-400' },
              { feature: 'Captions', credits: 1, color: 'text-purple-400' },
              { feature: 'Hashtags', credits: 1, color: 'text-green-400' },
              { feature: 'Hooks', credits: 1, color: 'text-cyan-400' },
              { feature: 'DM Reply', credits: 1, color: 'text-pink-400' },
            ].map((item, idx) => (
              <div key={idx} className="bg-black/20 rounded-lg p-3 text-center">
                <p className={`text-2xl font-bold ${item.color}`}>{item.credits}</p>
                <p className="text-white/50 text-xs">{item.feature}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Still Need Help */}
        <div className="text-center p-8 rounded-2xl bg-white/5 border border-white/10">
          <HelpCircle className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Still Need Help?</h3>
          <p className="text-white/60 mb-6">Our support team is here to help you succeed</p>
          <a 
            href="/support"
            className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-colors"
          >
            Contact Support
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default HelpCenterPage;
