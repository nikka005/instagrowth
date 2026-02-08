import React, { useState, useEffect } from 'react';
import { 
  Megaphone, Plus, Edit2, Trash2, Loader2, 
  AlertCircle, Info, CheckCircle2, Clock, RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AnnouncementsPage = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  const [form, setForm] = useState({
    title: '',
    message: '',
    type: 'info',
    target: 'all',
    start_date: '',
    end_date: '',
    link_url: '',
    link_text: ''
  });

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      const response = await fetch(`${API_URL}/api/announcements/admin/all`, { headers });
      if (response.ok) {
        const data = await response.json();
        setAnnouncements(data.announcements);
      }
    } catch (error) {
      toast.error('Failed to fetch announcements');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const params = new URLSearchParams();
      Object.entries(form).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const url = editing 
        ? `${API_URL}/api/announcements/admin/${editing}?${params}`
        : `${API_URL}/api/announcements/admin/create?${params}`;
      
      const response = await fetch(url, {
        method: editing ? 'PUT' : 'POST',
        headers
      });
      
      if (!response.ok) throw new Error('Failed to save');
      
      toast.success(editing ? 'Announcement updated!' : 'Announcement created!');
      resetForm();
      fetchAnnouncements();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const deleteAnnouncement = async (id) => {
    if (!confirm('Delete this announcement?')) return;
    
    try {
      const response = await fetch(`${API_URL}/api/announcements/admin/${id}`, {
        method: 'DELETE',
        headers
      });
      
      if (response.ok) {
        toast.success('Announcement deleted');
        fetchAnnouncements();
      }
    } catch (error) {
      toast.error('Failed to delete');
    }
  };

  const editAnnouncement = (ann) => {
    setForm({
      title: ann.title,
      message: ann.message,
      type: ann.type,
      target: ann.target,
      start_date: ann.start_date?.split('T')[0] || '',
      end_date: ann.end_date?.split('T')[0] || '',
      link_url: ann.link_url || '',
      link_text: ann.link_text || ''
    });
    setEditing(ann.announcement_id);
    setShowForm(true);
  };

  const resetForm = () => {
    setForm({
      title: '',
      message: '',
      type: 'info',
      target: 'all',
      start_date: '',
      end_date: '',
      link_url: '',
      link_text: ''
    });
    setEditing(null);
    setShowForm(false);
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'warning': return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      case 'success': return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'update': return <RefreshCw className="w-5 h-5 text-blue-400" />;
      case 'maintenance': return <Clock className="w-5 h-5 text-orange-400" />;
      default: return <Info className="w-5 h-5 text-indigo-400" />;
    }
  };

  const getTypeBadge = (type) => {
    const styles = {
      info: 'bg-indigo-500/20 text-indigo-400',
      warning: 'bg-yellow-500/20 text-yellow-400',
      success: 'bg-green-500/20 text-green-400',
      update: 'bg-blue-500/20 text-blue-400',
      maintenance: 'bg-orange-500/20 text-orange-400'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs ${styles[type]}`}>
        {type}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Announcements</h1>
          <p className="text-white/50 mt-1">Create in-app announcements for users</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500"
        >
          <Plus className="w-5 h-5" />
          New Announcement
        </button>
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <div className="p-6 bg-[#1e293b] border border-white/10 rounded-xl">
          <h3 className="text-lg font-semibold text-white mb-4">
            {editing ? 'Edit Announcement' : 'Create Announcement'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">Title</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-white/60 text-sm mb-1">Type</label>
                  <select
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="success">Success</option>
                    <option value="update">Update</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white/60 text-sm mb-1">Target</label>
                  <select
                    value={form.target}
                    onChange={(e) => setForm({ ...form, target: e.target.value })}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    <option value="all">All Users</option>
                    <option value="free">Free Users</option>
                    <option value="paid">Paid Users</option>
                    <option value="starter">Starter Plan</option>
                    <option value="pro">Pro Plan</option>
                    <option value="agency">Agency Plan</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-white/60 text-sm mb-1">Message</label>
              <textarea
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white min-h-[100px]"
                required
              />
            </div>

            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">Start Date</label>
                <input
                  type="date"
                  value={form.start_date}
                  onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">End Date</label>
                <input
                  type="date"
                  value={form.end_date}
                  onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">Link URL</label>
                <input
                  type="url"
                  value={form.link_url}
                  onChange={(e) => setForm({ ...form, link_url: e.target.value })}
                  placeholder="https://"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">Link Text</label>
                <input
                  type="text"
                  value={form.link_text}
                  onChange={(e) => setForm({ ...form, link_text: e.target.value })}
                  placeholder="Learn more"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 disabled:opacity-50"
              >
                {submitting ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : editing ? 'Update' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Announcements List */}
      {loading ? (
        <div className="text-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
        </div>
      ) : announcements.length === 0 ? (
        <div className="text-center py-20 bg-[#1e293b] border border-white/10 rounded-xl">
          <Megaphone className="w-16 h-16 text-white/20 mx-auto mb-4" />
          <p className="text-white/50">No announcements yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {announcements.map((ann) => (
            <div
              key={ann.announcement_id}
              className={`p-5 rounded-xl border ${
                ann.status === 'active' 
                  ? 'bg-[#1e293b] border-white/10' 
                  : 'bg-[#1e293b]/50 border-white/5'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  {getTypeIcon(ann.type)}
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-white">{ann.title}</h3>
                      {getTypeBadge(ann.type)}
                      <span className={`px-2 py-0.5 rounded-full text-xs ${
                        ann.status === 'active' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {ann.status}
                      </span>
                    </div>
                    <p className="text-white/60 text-sm">{ann.message}</p>
                    <div className="flex items-center gap-4 mt-2 text-white/40 text-xs">
                      <span>Target: {ann.target}</span>
                      {ann.start_date && <span>Start: {ann.start_date.split('T')[0]}</span>}
                      {ann.end_date && <span>End: {ann.end_date.split('T')[0]}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => editAnnouncement(ann)}
                    className="p-2 text-white/40 hover:text-white hover:bg-white/5 rounded"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deleteAnnouncement(ann.announcement_id)}
                    className="p-2 text-red-400/60 hover:text-red-400 hover:bg-red-500/10 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AnnouncementsPage;
