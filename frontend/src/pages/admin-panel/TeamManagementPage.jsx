import React, { useState, useEffect } from 'react';
import { UsersRound, Plus, Shield, Mail, Clock, MoreVertical, Check, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TeamManagementPage = () => {
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteForm, setInviteForm] = useState({ email: '', name: '', role: 'admin' });

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };

  useEffect(() => {
    fetchTeam();
  }, []);

  const fetchTeam = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/team`, { headers });
      if (response.ok) {
        const data = await response.json();
        setAdmins(data.admins || []);
      }
    } catch (error) {
      console.error('Error fetching team:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadge = (role) => {
    const styles = {
      super_admin: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      admin: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      support: 'bg-green-500/20 text-green-400 border-green-500/30',
      viewer: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs border ${styles[role] || styles.viewer}`}>
        {role?.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const getStatusBadge = (status) => {
    return status === 'active' ? (
      <span className="flex items-center gap-1 text-green-400 text-sm">
        <Check className="w-4 h-4" /> Active
      </span>
    ) : (
      <span className="flex items-center gap-1 text-red-400 text-sm">
        <X className="w-4 h-4" /> Disabled
      </span>
    );
  };

  const updateRole = async (adminId, newRole) => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/team/${adminId}/role?role=${newRole}`, {
        method: 'PUT',
        headers
      });
      if (response.ok) {
        toast.success('Role updated');
        fetchTeam();
      } else {
        toast.error('Failed to update role');
      }
    } catch (error) {
      toast.error('Error updating role');
    }
  };

  const toggleStatus = async (adminId, currentStatus) => {
    const newStatus = currentStatus === 'active' ? 'disabled' : 'active';
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/team/${adminId}/status?status=${newStatus}`, {
        method: 'PUT',
        headers
      });
      if (response.ok) {
        toast.success(`Admin ${newStatus}`);
        fetchTeam();
      } else {
        toast.error('Failed to update status');
      }
    } catch (error) {
      toast.error('Error updating status');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Team Management</h1>
          <p className="text-white/50">Manage admin users and permissions</p>
        </div>
        <button
          onClick={() => setShowInviteModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg text-white"
        >
          <Plus className="w-4 h-4" />
          Invite Admin
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Shield className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Super Admins</p>
              <p className="text-xl font-bold text-white">
                {admins.filter(a => a.role === 'super_admin').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <UsersRound className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Admins</p>
              <p className="text-xl font-bold text-white">
                {admins.filter(a => a.role === 'admin').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Check className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Active</p>
              <p className="text-xl font-bold text-white">
                {admins.filter(a => a.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-500/20 rounded-lg">
              <UsersRound className="w-5 h-5 text-gray-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Total Team</p>
              <p className="text-xl font-bold text-white">{admins.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Team Table */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          </div>
        ) : admins.length === 0 ? (
          <div className="text-center py-12">
            <UsersRound className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <p className="text-white/50">No team members found</p>
            <p className="text-white/30 text-sm mt-1">Invite admins to help manage your platform</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Admin</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Role</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Status</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">2FA</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Created</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {admins.map((admin) => (
                <tr key={admin.admin_id} className="hover:bg-white/5">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
                        <span className="text-indigo-400 font-medium">
                          {admin.name?.charAt(0)?.toUpperCase() || admin.email?.charAt(0)?.toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="text-white font-medium">{admin.name || 'Unnamed'}</p>
                        <p className="text-white/40 text-sm">{admin.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">{getRoleBadge(admin.role)}</td>
                  <td className="px-6 py-4">{getStatusBadge(admin.status)}</td>
                  <td className="px-6 py-4">
                    {admin.is_2fa_enabled ? (
                      <span className="text-green-400 text-sm">Enabled</span>
                    ) : (
                      <span className="text-white/40 text-sm">Disabled</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-white/70">
                    {admin.created_at ? new Date(admin.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <select
                        value={admin.role}
                        onChange={(e) => updateRole(admin.admin_id, e.target.value)}
                        className="px-2 py-1 bg-white/5 border border-white/10 rounded text-white text-sm"
                      >
                        <option value="viewer">Viewer</option>
                        <option value="support">Support</option>
                        <option value="admin">Admin</option>
                        <option value="super_admin">Super Admin</option>
                      </select>
                      <button
                        onClick={() => toggleStatus(admin.admin_id, admin.status)}
                        className={`px-2 py-1 rounded text-sm ${
                          admin.status === 'active' 
                            ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' 
                            : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                        }`}
                      >
                        {admin.status === 'active' ? 'Disable' : 'Enable'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#1e293b] rounded-xl p-6 w-full max-w-md border border-white/10">
            <h3 className="text-lg font-semibold text-white mb-4">Invite Admin</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-white/70 mb-1">Name</label>
                <input
                  type="text"
                  value={inviteForm.name}
                  onChange={(e) => setInviteForm({ ...inviteForm, name: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  placeholder="Admin name"
                />
              </div>
              <div>
                <label className="block text-sm text-white/70 mb-1">Email</label>
                <input
                  type="email"
                  value={inviteForm.email}
                  onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  placeholder="admin@example.com"
                />
              </div>
              <div>
                <label className="block text-sm text-white/70 mb-1">Role</label>
                <select
                  value={inviteForm.role}
                  onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                >
                  <option value="viewer">Viewer</option>
                  <option value="support">Support</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowInviteModal(false)}
                className="px-4 py-2 text-white/70 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  toast.info('Admin invite feature coming soon');
                  setShowInviteModal(false);
                }}
                className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-lg text-white"
              >
                Send Invite
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamManagementPage;
