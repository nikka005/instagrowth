import React, { useState, useEffect } from 'react';
import { CreditCard, Search, Filter, MoreVertical, Check, X, Clock, RefreshCw } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SubscriptionsPage = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      const token = localStorage.getItem('admin_panel_token');
      const response = await fetch(`${API_URL}/api/admin-panel/subscriptions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSubscriptions(data.subscriptions || []);
      }
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-500/20 text-green-400 border-green-500/30',
      cancelled: 'bg-red-500/20 text-red-400 border-red-500/30',
      past_due: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      trialing: 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs border ${styles[status] || styles.active}`}>
        {status?.replace('_', ' ').toUpperCase() || 'ACTIVE'}
      </span>
    );
  };

  const filteredSubscriptions = subscriptions.filter(sub => {
    const matchesSearch = sub.user_email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         sub.plan_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || sub.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Subscriptions</h1>
          <p className="text-white/50">Manage user subscriptions and billing</p>
        </div>
        <button
          onClick={fetchSubscriptions}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg text-white"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Check className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Active</p>
              <p className="text-xl font-bold text-white">
                {subscriptions.filter(s => s.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Clock className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Trialing</p>
              <p className="text-xl font-bold text-white">
                {subscriptions.filter(s => s.status === 'trialing').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Clock className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Past Due</p>
              <p className="text-xl font-bold text-white">
                {subscriptions.filter(s => s.status === 'past_due').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <X className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Cancelled</p>
              <p className="text-xl font-bold text-white">
                {subscriptions.filter(s => s.status === 'cancelled').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by email or plan..."
            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-indigo-500"
          />
        </div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-indigo-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="trialing">Trialing</option>
          <option value="past_due">Past Due</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
          </div>
        ) : filteredSubscriptions.length === 0 ? (
          <div className="text-center py-12">
            <CreditCard className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <p className="text-white/50">No subscriptions found</p>
            <p className="text-white/30 text-sm mt-1">Subscriptions will appear here when users subscribe to plans</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">User</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Plan</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Status</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Amount</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Next Billing</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredSubscriptions.map((sub) => (
                <tr key={sub.subscription_id} className="hover:bg-white/5">
                  <td className="px-6 py-4">
                    <p className="text-white font-medium">{sub.user_email}</p>
                    <p className="text-white/40 text-sm">{sub.user_id}</p>
                  </td>
                  <td className="px-6 py-4 text-white">{sub.plan_name || 'N/A'}</td>
                  <td className="px-6 py-4">{getStatusBadge(sub.status)}</td>
                  <td className="px-6 py-4 text-white">${sub.amount || '0'}/mo</td>
                  <td className="px-6 py-4 text-white/70">
                    {sub.next_billing_date ? new Date(sub.next_billing_date).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <button className="p-1 hover:bg-white/10 rounded">
                      <MoreVertical className="w-4 h-4 text-white/50" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default SubscriptionsPage;
