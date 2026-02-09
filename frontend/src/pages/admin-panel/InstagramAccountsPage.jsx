import React, { useState, useEffect } from 'react';
import { Instagram, Search, RefreshCw, Trash2, ExternalLink, Users, Image, Heart } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const InstagramAccountsPage = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('admin_panel_token');
      const response = await fetch(`${API_URL}/api/admin-panel/instagram-accounts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      connected: 'bg-green-500/20 text-green-400 border-green-500/30',
      disconnected: 'bg-red-500/20 text-red-400 border-red-500/30',
      pending: 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs border ${styles[status] || styles.pending}`}>
        {status?.toUpperCase() || 'PENDING'}
      </span>
    );
  };

  const filteredAccounts = accounts.filter(acc => 
    acc.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    acc.user_email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalFollowers = accounts.reduce((sum, acc) => sum + (acc.follower_count || 0), 0);
  const totalMedia = accounts.reduce((sum, acc) => sum + (acc.media_count || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Instagram Accounts</h1>
          <p className="text-white/50">View all connected Instagram accounts</p>
        </div>
        <button
          onClick={fetchAccounts}
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
            <div className="p-2 bg-pink-500/20 rounded-lg">
              <Instagram className="w-5 h-5 text-pink-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Total Accounts</p>
              <p className="text-xl font-bold text-white">{accounts.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Users className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Connected</p>
              <p className="text-xl font-bold text-white">
                {accounts.filter(a => a.connection_status === 'connected').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Heart className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Total Followers</p>
              <p className="text-xl font-bold text-white">
                {totalFollowers.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-[#1e293b] rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Image className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-white/50 text-sm">Total Posts</p>
              <p className="text-xl font-bold text-white">
                {totalMedia.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by username or email..."
          className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-indigo-500"
        />
      </div>

      {/* Table */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
          </div>
        ) : filteredAccounts.length === 0 ? (
          <div className="text-center py-12">
            <Instagram className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <p className="text-white/50">No Instagram accounts found</p>
            <p className="text-white/30 text-sm mt-1">Accounts will appear here when users connect their Instagram</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Account</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Owner</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Status</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Followers</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Posts</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Connected</th>
                <th className="text-left text-white/50 text-sm font-medium px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredAccounts.map((account) => (
                <tr key={account.account_id} className="hover:bg-white/5">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      {account.profile_picture ? (
                        <img 
                          src={account.profile_picture} 
                          alt={account.username}
                          className="w-10 h-10 rounded-full"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center">
                          <Instagram className="w-5 h-5 text-pink-400" />
                        </div>
                      )}
                      <div>
                        <p className="text-white font-medium">@{account.username}</p>
                        <p className="text-white/40 text-sm">{account.niche || 'Not specified'}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-white">{account.user_email || 'N/A'}</p>
                    <p className="text-white/40 text-xs">{account.user_id}</p>
                  </td>
                  <td className="px-6 py-4">{getStatusBadge(account.connection_status)}</td>
                  <td className="px-6 py-4 text-white">
                    {(account.follower_count || 0).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-white">
                    {(account.media_count || 0).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-white/70">
                    {account.connected_at ? new Date(account.connected_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <a
                        href={`https://instagram.com/${account.username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 hover:bg-white/10 rounded text-white/50 hover:text-white"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
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

export default InstagramAccountsPage;
