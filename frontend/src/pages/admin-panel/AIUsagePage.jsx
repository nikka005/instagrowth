import React, { useState, useEffect } from 'react';
import { Cpu, TrendingUp, DollarSign, Users, Loader2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AIUsagePage = ({ admin }) => {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const token = localStorage.getItem('admin_panel_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    try {
      const [statsRes, chartRes] = await Promise.all([
        fetch(`${API_URL}/api/admin-panel/ai-usage/stats`, { credentials: 'include', headers }),
        fetch(`${API_URL}/api/admin-panel/dashboard/charts/ai-usage?days=30`, { credentials: 'include', headers })
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (chartRes.ok) setChartData((await chartRes.json()).chart_data || []);
    } catch (error) {
      console.error('Failed to fetch AI usage data:', error);
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

  const featureData = stats?.usage_by_feature ? Object.entries(stats.usage_by_feature).map(([name, value]) => ({
    name: name.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
    requests: value
  })) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">AI Usage</h1>
        <p className="text-white/50 mt-1">Monitor AI API usage and costs</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">Requests Today</span>
            <Cpu className="w-5 h-5 text-cyan-400" />
          </div>
          <p className="text-3xl font-bold text-white">{stats?.total_requests_today?.toLocaleString() || 0}</p>
        </div>

        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">Requests This Month</span>
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <p className="text-3xl font-bold text-white">{stats?.total_requests_month?.toLocaleString() || 0}</p>
        </div>

        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-white/50 text-sm">Estimated Cost</span>
            <DollarSign className="w-5 h-5 text-green-400" />
          </div>
          <p className="text-3xl font-bold text-white">${stats?.estimated_cost_month?.toFixed(2) || 0}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Trend */}
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-white mb-6">Usage Trend (30 Days)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
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

        {/* Usage by Feature */}
        <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-white mb-6">Usage by Feature</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fontSize: 12 }} width={120} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="requests" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Users */}
      <div className="bg-[#1e293b] rounded-xl p-6 border border-white/5">
        <h3 className="text-lg font-semibold text-white mb-6">Top Users by AI Usage</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-4 py-3 text-sm font-medium text-white/50">User</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-white/50">Plan</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-white/50">Usage</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-white/50">Limit</th>
                <th className="text-left px-4 py-3 text-sm font-medium text-white/50">%</th>
              </tr>
            </thead>
            <tbody>
              {stats?.top_users?.map((user, index) => (
                <tr key={user.user_id} className="border-b border-white/5">
                  <td className="px-4 py-3">
                    <div>
                      <p className="text-white font-medium">{user.name || 'Unknown'}</p>
                      <p className="text-white/50 text-sm">{user.email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 text-xs rounded-full capitalize">
                      {user.plan}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-white">{user.usage}</td>
                  <td className="px-4 py-3 text-white/50">{user.limit}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${(user.usage / user.limit) > 0.8 ? 'bg-red-500' : 'bg-cyan-500'}`}
                          style={{ width: `${Math.min(100, (user.usage / user.limit) * 100)}%` }}
                        />
                      </div>
                      <span className="text-white/50 text-sm">{Math.round((user.usage / user.limit) * 100)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AIUsagePage;
