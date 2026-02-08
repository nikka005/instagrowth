import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, Users, Percent, Loader2, ArrowUp, ArrowDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const RevenuePage = ({ admin }) => {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef'];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const token = localStorage.getItem('admin_panel_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    try {
      const [statsRes, chartRes] = await Promise.all([
        fetch(`${API_URL}/api/admin-panel/revenue/stats`, { credentials: 'include', headers }),
        fetch(`${API_URL}/api/admin-panel/dashboard/charts/revenue?days=30`, { credentials: 'include', headers })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (chartRes.ok) setChartData((await chartRes.json()).chart_data || []);
    } catch (error) {
      console.error('Failed to fetch revenue data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  const revenueByPlanData = stats?.revenue_by_plan ? Object.entries(stats.revenue_by_plan).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  })) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Revenue</h1>
        <p className="text-white/50 mt-1">Financial overview and analytics</p>
      </div>

      {/* Revenue Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">MRR</span>
            <DollarSign className="w-5 h-5 text-green-400" />
          </div>
          <p className="text-3xl font-bold text-white">${stats?.mrr?.toLocaleString() || 0}</p>
          <p className="text-white/50 text-sm mt-2">Monthly Recurring Revenue</p>
        </div>

        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">ARR</span>
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <p className="text-3xl font-bold text-white">${stats?.arr?.toLocaleString() || 0}</p>
          <p className="text-white/50 text-sm mt-2">Annual Recurring Revenue</p>
        </div>

        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">Churn Rate</span>
            <Percent className="w-5 h-5 text-amber-400" />
          </div>
          <p className="text-3xl font-bold text-white">{stats?.churn_rate || 0}%</p>
          <p className="text-white/50 text-sm mt-2">Monthly churn</p>
        </div>

        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">ARPU</span>
            <Users className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-3xl font-bold text-white">${stats?.arpu || 0}</p>
          <p className="text-white/50 text-sm mt-2">Avg Revenue Per User</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue Trend */}
        <div className="lg:col-span-2 bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-white mb-6">Revenue Trend (30 Days)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                  formatter={(value) => [`$${value}`, 'Revenue']}
                />
                <Line type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue by Plan */}
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-white mb-6">Revenue by Plan</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={revenueByPlanData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {revenueByPlanData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  formatter={(value) => [`$${value}`, 'Revenue']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
            {revenueByPlanData.map((entry, index) => (
              <div key={entry.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                  <span className="text-white/70 text-sm">{entry.name}</span>
                </div>
                <span className="text-white font-medium">${entry.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
        <h3 className="text-lg font-semibold text-white mb-4">Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p className="text-white/50 text-sm">Total Revenue</p>
            <p className="text-2xl font-bold text-white mt-1">${stats?.total_revenue?.toLocaleString() || 0}</p>
          </div>
          <div>
            <p className="text-white/50 text-sm">Active Subscriptions</p>
            <p className="text-2xl font-bold text-white mt-1">{stats?.active_subscriptions || 0}</p>
          </div>
          <div>
            <p className="text-white/50 text-sm">Projected Monthly</p>
            <p className="text-2xl font-bold text-green-400 mt-1">${stats?.mrr?.toLocaleString() || 0}</p>
          </div>
          <div>
            <p className="text-white/50 text-sm">Projected Annual</p>
            <p className="text-2xl font-bold text-blue-400 mt-1">${stats?.arr?.toLocaleString() || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RevenuePage;
