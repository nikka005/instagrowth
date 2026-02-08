import React, { useState, useEffect } from 'react';
import { 
  Users, CreditCard, Instagram, Cpu, DollarSign, 
  TrendingUp, TrendingDown, ArrowUpRight, Activity
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboardPage = ({ admin }) => {
  const [stats, setStats] = useState(null);
  const [revenueChart, setRevenueChart] = useState([]);
  const [usersChart, setUsersChart] = useState([]);
  const [aiChart, setAiChart] = useState([]);
  const [loading, setLoading] = useState(true);

  const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef'];

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    const token = localStorage.getItem('admin_panel_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    try {
      const [statsRes, revenueRes, usersRes, aiRes] = await Promise.all([
        fetch(`${API_URL}/api/admin-panel/dashboard/stats`, { credentials: 'include', headers }),
        fetch(`${API_URL}/api/admin-panel/dashboard/charts/revenue?days=30`, { credentials: 'include', headers }),
        fetch(`${API_URL}/api/admin-panel/dashboard/charts/users?days=30`, { credentials: 'include', headers }),
        fetch(`${API_URL}/api/admin-panel/dashboard/charts/ai-usage?days=30`, { credentials: 'include', headers })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (revenueRes.ok) setRevenueChart((await revenueRes.json()).chart_data || []);
      if (usersRes.ok) setUsersChart((await usersRes.json()).chart_data || []);
      if (aiRes.ok) setAiChart((await aiRes.json()).chart_data || []);
    } catch (error) {
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, change, color }) => (
    <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-white/50 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
          {change && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${change > 0 ? 'text-green-400' : 'text-red-400'}`}>
              {change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span>{Math.abs(change)}% from last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  const planData = stats?.plan_distribution ? Object.entries(stats.plan_distribution).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  })) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard Overview</h1>
        <p className="text-white/50 mt-1">Welcome back, {admin?.name}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Users" 
          value={stats?.total_users?.toLocaleString() || 0} 
          icon={Users} 
          color="bg-indigo-500"
        />
        <StatCard 
          title="Active Subscriptions" 
          value={stats?.active_subscriptions?.toLocaleString() || 0} 
          icon={CreditCard} 
          color="bg-purple-500"
        />
        <StatCard 
          title="Instagram Accounts" 
          value={stats?.total_accounts?.toLocaleString() || 0} 
          icon={Instagram} 
          color="bg-pink-500"
        />
        <StatCard 
          title="AI Requests Today" 
          value={stats?.ai_requests_today?.toLocaleString() || 0} 
          icon={Cpu} 
          color="bg-cyan-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Revenue (Last 30 Days)</h3>
            <DollarSign className="w-5 h-5 text-white/30" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={revenueChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* New Users Chart */}
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">New Users (Last 30 Days)</h3>
            <Users className="w-5 h-5 text-white/30" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={usersChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="users" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Plan Distribution */}
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-white mb-6">Users by Plan</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={planData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {planData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-3 mt-4 justify-center">
            {planData.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                <span className="text-sm text-white/60">{entry.name}: {entry.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Usage Trend */}
        <div className="lg:col-span-2 bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">AI Usage Trend</h3>
            <Activity className="w-5 h-5 text-white/30" />
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={aiChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Line type="monotone" dataKey="requests" stroke="#06b6d4" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5 text-center">
          <p className="text-2xl font-bold text-white">{stats?.new_users_today || 0}</p>
          <p className="text-white/50 text-sm mt-1">New Users Today</p>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5 text-center">
          <p className="text-2xl font-bold text-white">{stats?.audits_today || 0}</p>
          <p className="text-white/50 text-sm mt-1">Audits Today</p>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5 text-center">
          <p className="text-2xl font-bold text-white">{stats?.total_audits || 0}</p>
          <p className="text-white/50 text-sm mt-1">Total Audits</p>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5 text-center">
          <p className="text-2xl font-bold text-white">{stats?.total_content || 0}</p>
          <p className="text-white/50 text-sm mt-1">Content Items</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboardPage;
