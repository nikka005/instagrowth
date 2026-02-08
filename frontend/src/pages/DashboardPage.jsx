import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Instagram, BarChart3, Sparkles, Calendar, TrendingUp, 
  ArrowRight, Plus, Zap, Target, AlertCircle, X, Info, CheckCircle2, AlertTriangle
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Progress } from "../components/ui/progress";
import DashboardLayout from "../components/DashboardLayout";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DashboardPage = ({ auth }) => {
  const [stats, setStats] = useState(null);
  const [credits, setCredits] = useState(null);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchCredits();
    fetchAnnouncements();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/dashboard/stats`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCredits = async () => {
    try {
      const response = await fetch(`${API_URL}/api/credits`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setCredits(data);
      }
    } catch (error) {
      console.error("Failed to fetch credits:", error);
    }
  };

  const fetchAnnouncements = async () => {
    try {
      const response = await fetch(`${API_URL}/api/announcements/unread`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setAnnouncements(data.announcements || []);
      }
    } catch (error) {
      console.error("Failed to fetch announcements:", error);
    }
  };

  const dismissAnnouncement = async (announcementId) => {
    try {
      await fetch(`${API_URL}/api/announcements/${announcementId}/dismiss`, {
        method: "POST",
        credentials: "include",
      });
      setAnnouncements(prev => prev.filter(a => a.announcement_id !== announcementId));
    } catch (error) {
      console.error("Failed to dismiss:", error);
    }
  };

  const getAnnouncementIcon = (type) => {
    switch (type) {
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'success': return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      default: return <Info className="w-5 h-5 text-indigo-400" />;
    }
  };

  const quickActions = [
    { icon: <Instagram className="w-5 h-5" />, label: "Add Account", path: "/accounts", color: "from-pink-500 to-rose-500" },
    { icon: <BarChart3 className="w-5 h-5" />, label: "Run Audit", path: "/audit", color: "from-indigo-500 to-purple-500" },
    { icon: <Sparkles className="w-5 h-5" />, label: "Generate Content", path: "/content", color: "from-teal-500 to-cyan-500" },
    { icon: <Calendar className="w-5 h-5" />, label: "Create Plan", path: "/planner", color: "from-orange-500 to-red-500" },
  ];

  // Mock chart data
  const chartData = stats?.recent_audits?.map((audit, index) => ({
    name: audit.username || `Audit ${index + 1}`,
    engagement: audit.engagement_score || 0,
    consistency: audit.content_consistency || 0,
  })) || [];

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-8">
        {/* Announcements Banner */}
        <AnimatePresence>
          {announcements.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-3"
            >
              {announcements.slice(0, 2).map((announcement) => (
                <div
                  key={announcement.announcement_id}
                  className={`p-4 rounded-xl border flex items-start gap-3 ${
                    announcement.type === 'warning' 
                      ? 'bg-yellow-500/10 border-yellow-500/20'
                      : announcement.type === 'success'
                      ? 'bg-green-500/10 border-green-500/20'
                      : 'bg-indigo-500/10 border-indigo-500/20'
                  }`}
                >
                  {getAnnouncementIcon(announcement.type)}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-white">{announcement.title}</h4>
                    <p className="text-white/60 text-sm mt-0.5">{announcement.message}</p>
                    {announcement.link_url && (
                      <a 
                        href={announcement.link_url} 
                        className="text-indigo-400 text-sm mt-2 inline-block hover:underline"
                      >
                        {announcement.link_text || 'Learn more'}
                      </a>
                    )}
                  </div>
                  <button
                    onClick={() => dismissAnnouncement(announcement.announcement_id)}
                    className="p-1 text-white/40 hover:text-white"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Welcome Section */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">
              Welcome back, {auth.user?.name?.split(' ')[0]}!
            </h1>
            <p className="text-white/60 mt-1">Here's what's happening with your accounts today.</p>
          </div>
          <Link to="/accounts">
            <Button className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]" data-testid="add-account-btn">
              <Plus className="w-5 h-5 mr-2" />
              Add Account
            </Button>
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Instagram Accounts", value: stats?.accounts_count || 0, limit: auth.user?.account_limit || 1, icon: <Instagram className="w-5 h-5" />, color: "text-pink-400" },
            { label: "Audits Generated", value: stats?.audits_count || 0, icon: <BarChart3 className="w-5 h-5" />, color: "text-indigo-400" },
            { label: "Content Items", value: stats?.content_items_count || 0, icon: <Sparkles className="w-5 h-5" />, color: "text-teal-400" },
            { label: "Growth Plans", value: stats?.growth_plans_count || 0, icon: <Calendar className="w-5 h-5" />, color: "text-orange-400" },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5 hover:border-white/10 transition-colors"
            >
              <div className="flex items-center justify-between mb-4">
                <span className={stat.color}>{stat.icon}</span>
                {stat.limit && (
                  <span className="text-xs text-white/40">{stat.value}/{stat.limit}</span>
                )}
              </div>
              <div className="text-3xl font-display font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-white/50">{stat.label}</div>
              {stat.limit && (
                <Progress value={(stat.value / stat.limit) * 100} className="mt-3 h-1.5 bg-white/10" />
              )}
            </motion.div>
          ))}
        </div>

        {/* AI Credits & Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AI Credits Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center">
                <Zap className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-white">AI Usage</h3>
                <p className="text-sm text-white/50">This month</p>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-display font-bold text-white">
                  {stats?.ai_usage?.current || 0}
                </span>
                <span className="text-white/50">/ {stats?.ai_usage?.limit || 10}</span>
              </div>
              <Progress 
                value={((stats?.ai_usage?.current || 0) / (stats?.ai_usage?.limit || 10)) * 100} 
                className="h-2 bg-white/10" 
              />
              {(stats?.ai_usage?.current || 0) >= (stats?.ai_usage?.limit || 10) && (
                <div className="flex items-center gap-2 text-amber-400 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  <span>Upgrade for more AI generations</span>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
            <h3 className="font-display font-semibold text-white mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {quickActions.map((action, index) => (
                <Link
                  key={index}
                  to={action.path}
                  className="group p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all text-center"
                  data-testid={`quick-action-${action.label.toLowerCase().replace(' ', '-')}`}
                >
                  <div className={`w-10 h-10 mx-auto rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                    {action.icon}
                  </div>
                  <span className="text-sm text-white/70 group-hover:text-white">{action.label}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Performance Chart */}
        <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-display font-semibold text-white">Audit Performance</h3>
              <p className="text-sm text-white/50">Recent audit scores across your accounts</p>
            </div>
            <Link to="/audit">
              <Button variant="ghost" className="text-indigo-400 hover:text-indigo-300">
                View All
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
          
          {chartData.length > 0 ? (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="engagementGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366F1" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#6366F1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="consistencyGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#14B8A6" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#14B8A6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                  <XAxis dataKey="name" stroke="#52525B" fontSize={12} />
                  <YAxis stroke="#52525B" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#0F0F11', 
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '12px',
                      color: '#fff'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="#6366F1" 
                    fill="url(#engagementGradient)"
                    strokeWidth={2}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="consistency" 
                    stroke="#14B8A6" 
                    fill="url(#consistencyGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-[300px] flex items-center justify-center">
              <div className="text-center">
                <Target className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/50">No audit data yet</p>
                <Link to="/audit">
                  <Button variant="link" className="text-indigo-400 mt-2">
                    Run your first audit
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Upgrade CTA */}
        {auth.user?.role === "starter" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-gradient-to-r from-indigo-600/20 via-purple-600/20 to-indigo-600/20 border border-indigo-500/20 flex flex-col md:flex-row items-center justify-between gap-4"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-indigo-400" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-white">Upgrade to Pro</h3>
                <p className="text-sm text-white/60">Get 5 accounts, 100 AI generations, and PDF exports</p>
              </div>
            </div>
            <Link to="/billing">
              <Button className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium" data-testid="upgrade-btn">
                Upgrade Now
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
