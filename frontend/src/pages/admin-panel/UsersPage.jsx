import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, MoreHorizontal, Eye, Edit, Key, Ban, 
  Trash2, Download, ChevronLeft, ChevronRight, Loader2,
  User, Mail, Calendar, Shield
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const UsersPage = ({ admin }) => {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  const [page, setPage] = useState(0);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const limit = 20;

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchUsers();
  }, [page, search, planFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/admin-panel/users?skip=${page * limit}&limit=${limit}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (planFilter) url += `&plan=${planFilter}`;

      const response = await fetch(url, { credentials: 'include', headers });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
        setTotal(data.total || 0);
      }
    } catch (error) {
      toast.error('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const viewUser = async (userId) => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/users/${userId}`, { credentials: 'include', headers });
      if (response.ok) {
        const data = await response.json();
        setSelectedUser(data);
        setShowUserModal(true);
      }
    } catch (error) {
      toast.error('Failed to fetch user details');
    }
  };

  const changePlan = async (userId, plan) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/users/${userId}/plan?plan=${plan}`, {
        method: 'PUT',
        credentials: 'include',
        headers
      });
      if (response.ok) {
        toast.success('Plan updated');
        fetchUsers();
        if (selectedUser) viewUser(userId);
      } else {
        throw new Error('Failed to update plan');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setActionLoading(false);
    }
  };

  const changeStatus = async (userId, status) => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/users/${userId}/status?status=${status}`, {
        method: 'PUT',
        credentials: 'include',
        headers
      });
      if (response.ok) {
        toast.success(`User ${status}`);
        fetchUsers();
      }
    } catch (error) {
      toast.error('Failed to update status');
    } finally {
      setActionLoading(false);
    }
  };

  const resetPassword = async (userId) => {
    const newPassword = prompt('Enter new password:');
    if (!newPassword) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/users/${userId}/reset-password?new_password=${encodeURIComponent(newPassword)}`, {
        method: 'POST',
        credentials: 'include',
        headers
      });
      if (response.ok) {
        toast.success('Password reset');
      }
    } catch (error) {
      toast.error('Failed to reset password');
    } finally {
      setActionLoading(false);
    }
  };

  const deleteUser = async (userId) => {
    if (!confirm('Are you sure? This will delete all user data.')) return;

    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/users/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
        headers
      });
      if (response.ok) {
        toast.success('User deleted');
        fetchUsers();
        setShowUserModal(false);
      }
    } catch (error) {
      toast.error('Failed to delete user');
    } finally {
      setActionLoading(false);
    }
  };

  const exportUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/users/export/csv`, { credentials: 'include', headers });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'users_export.csv';
        a.click();
      }
    } catch (error) {
      toast.error('Failed to export');
    }
  };

  const getRoleBadge = (role) => {
    const colors = {
      starter: 'bg-gray-500/20 text-gray-400',
      pro: 'bg-blue-500/20 text-blue-400',
      agency: 'bg-purple-500/20 text-purple-400',
      enterprise: 'bg-amber-500/20 text-amber-400',
      admin: 'bg-red-500/20 text-red-400'
    };
    return colors[role] || colors.starter;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Users</h1>
          <p className="text-white/50 mt-1">{total} total users</p>
        </div>
        <button onClick={exportUsers} className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors">
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            placeholder="Search users..."
            className="w-full pl-11 pr-4 py-2.5 bg-[#1e293b] border border-white/10 rounded-lg text-white placeholder-white/30 focus:border-indigo-500 focus:outline-none"
          />
        </div>
        <select
          value={planFilter}
          onChange={(e) => { setPlanFilter(e.target.value); setPage(0); }}
          className="px-4 py-2.5 bg-[#1e293b] border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
        >
          <option value="">All Plans</option>
          <option value="starter">Starter</option>
          <option value="pro">Pro</option>
          <option value="agency">Agency</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/5">
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">User</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Plan</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Accounts</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">AI Usage</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-white/50">Joined</th>
                <th className="text-right px-6 py-4 text-sm font-medium text-white/50">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-white/50">No users found</td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.user_id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-medium">
                          {user.name?.charAt(0) || 'U'}
                        </div>
                        <div>
                          <p className="text-white font-medium">{user.name}</p>
                          <p className="text-white/50 text-sm">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getRoleBadge(user.role)}`}>
                        {user.role?.charAt(0).toUpperCase() + user.role?.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-white/70">{user.accounts_count || 0}</td>
                    <td className="px-6 py-4 text-white/70">{user.ai_usage_current || 0} / {user.ai_usage_limit || 0}</td>
                    <td className="px-6 py-4 text-white/50 text-sm">{user.created_at?.slice(0, 10)}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => viewUser(user.user_id)} className="p-2 text-white/50 hover:text-white hover:bg-white/10 rounded-lg">
                          <Eye className="w-4 h-4" />
                        </button>
                        <select
                          value={user.role}
                          onChange={(e) => changePlan(user.user_id, e.target.value)}
                          className="px-2 py-1 bg-white/5 border border-white/10 rounded text-white text-sm focus:outline-none"
                        >
                          <option value="starter">Starter</option>
                          <option value="pro">Pro</option>
                          <option value="agency">Agency</option>
                          <option value="enterprise">Enterprise</option>
                        </select>
                        <button onClick={() => changeStatus(user.user_id, user.status === 'blocked' ? 'active' : 'blocked')} className="p-2 text-white/50 hover:text-amber-400 hover:bg-white/10 rounded-lg">
                          <Ban className="w-4 h-4" />
                        </button>
                        <button onClick={() => deleteUser(user.user_id)} className="p-2 text-white/50 hover:text-red-400 hover:bg-white/10 rounded-lg">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
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

      {/* User Detail Modal */}
      {showUserModal && selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-[#1e293b] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">User Details</h2>
                <button onClick={() => setShowUserModal(false)} className="text-white/50 hover:text-white">&times;</button>
              </div>
            </div>
            <div className="p-6 space-y-6">
              {/* User Info */}
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                  {selectedUser.user?.name?.charAt(0) || 'U'}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{selectedUser.user?.name}</h3>
                  <p className="text-white/50">{selectedUser.user?.email}</p>
                  <span className={`inline-block mt-1 px-2.5 py-1 rounded-full text-xs font-medium ${getRoleBadge(selectedUser.user?.role)}`}>
                    {selectedUser.user?.role}
                  </span>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white/5 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-white">{selectedUser.accounts?.length || 0}</p>
                  <p className="text-white/50 text-sm">Accounts</p>
                </div>
                <div className="bg-white/5 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-white">{selectedUser.recent_audits?.length || 0}</p>
                  <p className="text-white/50 text-sm">Recent Audits</p>
                </div>
                <div className="bg-white/5 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-white">{selectedUser.ai_usage?.current_month || 0} / {selectedUser.ai_usage?.limit || 0}</p>
                  <p className="text-white/50 text-sm">AI Usage</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-3">
                <button onClick={() => resetPassword(selectedUser.user?.user_id)} className="flex items-center gap-2 px-4 py-2 bg-white/5 text-white rounded-lg hover:bg-white/10">
                  <Key className="w-4 h-4" />
                  Reset Password
                </button>
                <button onClick={() => changeStatus(selectedUser.user?.user_id, 'blocked')} className="flex items-center gap-2 px-4 py-2 bg-amber-500/20 text-amber-400 rounded-lg hover:bg-amber-500/30">
                  <Ban className="w-4 h-4" />
                  Block User
                </button>
                <button onClick={() => deleteUser(selectedUser.user?.user_id)} className="flex items-center gap-2 px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30">
                  <Trash2 className="w-4 h-4" />
                  Delete User
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
