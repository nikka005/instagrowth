import React, { useState, useEffect } from 'react';
import { FileText, Search, Filter, ChevronLeft, ChevronRight, Loader2, User, Settings, CreditCard, Shield } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LogsPage = ({ admin }) => {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [actionFilter, setActionFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const limit = 50;

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter, typeFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/admin-panel/logs?skip=${page * limit}&limit=${limit}`;
      if (actionFilter) url += `&action=${actionFilter}`;
      if (typeFilter) url += `&target_type=${typeFilter}`;

      const response = await fetch(url, { credentials: 'include', headers });
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs || []);
        setTotal(data.total || 0);
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    if (action.includes('user') || action.includes('login')) return User;
    if (action.includes('plan') || action.includes('subscription')) return CreditCard;
    if (action.includes('setting') || action.includes('system')) return Settings;
    return Shield;
  };

  const getActionColor = (action) => {
    if (action.includes('delete') || action.includes('block') || action.includes('disable')) return 'text-red-400 bg-red-500/20';
    if (action.includes('create') || action.includes('enable') || action.includes('login')) return 'text-green-400 bg-green-500/20';
    if (action.includes('update') || action.includes('change')) return 'text-amber-400 bg-amber-500/20';
    return 'text-blue-400 bg-blue-500/20';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Activity Logs</h1>
        <p className="text-white/50 mt-1">Track all admin actions and system events</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <select
          value={actionFilter}
          onChange={(e) => { setActionFilter(e.target.value); setPage(0); }}
          className="px-4 py-2.5 bg-[#1e293b] border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
        >
          <option value="">All Actions</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="change_plan">Change Plan</option>
          <option value="reset_password">Reset Password</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(0); }}
          className="px-4 py-2.5 bg-[#1e293b] border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
        >
          <option value="">All Types</option>
          <option value="user">User</option>
          <option value="plan">Plan</option>
          <option value="subscription">Subscription</option>
          <option value="auth">Authentication</option>
          <option value="system">System</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      {/* Logs Table */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Action</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Admin</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Target</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Details</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">IP Address</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Time</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-white/50">No logs found</td>
                </tr>
              ) : (
                logs.map((log) => {
                  const Icon = getActionIcon(log.action);
                  const colorClass = getActionColor(log.action);
                  return (
                    <tr key={log.log_id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${colorClass}`}>
                            <Icon className="w-4 h-4" />
                          </div>
                          <span className="text-white font-medium">{log.action.replace(/_/g, ' ')}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-white/70">{log.admin_email}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-white/5 text-white/60 text-xs rounded">{log.target_type}</span>
                        {log.target_id && <span className="text-white/40 text-xs ml-2">{log.target_id}</span>}
                      </td>
                      <td className="px-6 py-4 text-white/50 text-sm max-w-xs truncate">
                        {JSON.stringify(log.details)}
                      </td>
                      <td className="px-6 py-4 text-white/50 text-sm font-mono">{log.ip_address}</td>
                      <td className="px-6 py-4 text-white/50 text-sm">{new Date(log.created_at).toLocaleString()}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
          <p className="text-sm text-white/50">
            Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="p-2 text-white/50 hover:text-white hover:bg-white/10 rounded-lg disabled:opacity-30"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * limit >= total}
              className="p-2 text-white/50 hover:text-white hover:bg-white/10 rounded-lg disabled:opacity-30"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogsPage;
