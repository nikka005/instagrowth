import React, { useState, useEffect } from 'react';
import { Settings, Save, Key, Mail, Globe, Shield, AlertCircle, Loader2, Check } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SettingsPage = ({ admin }) => {
  const [settings, setSettings] = useState({
    platform_name: 'InstaGrowth OS',
    support_email: '',
    default_ai_model: 'gpt-5.2',
    openai_api_key: '',
    stripe_api_key: '',
    resend_api_key: '',
    meta_api_key: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/settings`, { credentials: 'include', headers });
      if (response.ok) {
        const data = await response.json();
        setSettings(prev => ({ ...prev, ...data }));
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const params = new URLSearchParams();
      Object.entries(settings).forEach(([key, value]) => {
        if (value && key !== 'setting_id') {
          params.append(key, value);
        }
      });

      const response = await fetch(`${API_URL}/api/admin-panel/settings?${params}`, {
        method: 'PUT',
        credentials: 'include',
        headers
      });

      if (response.ok) {
        toast.success('Settings saved');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  if (admin?.role !== 'super_admin') {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <Shield className="w-16 h-16 text-white/20 mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">Access Denied</h2>
        <p className="text-white/50">Only Super Admins can access system settings</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Settings</h1>
          <p className="text-white/50 mt-1">Configure platform settings and integrations</p>
        </div>
        <button
          onClick={saveSettings}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:opacity-50"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Save Changes
        </button>
      </div>

      {/* General Settings */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-indigo-500/20 rounded-lg">
            <Globe className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">General Settings</h3>
            <p className="text-white/50 text-sm">Basic platform configuration</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Platform Name</label>
            <input
              type="text"
              value={settings.platform_name}
              onChange={(e) => setSettings({ ...settings, platform_name: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Support Email</label>
            <input
              type="email"
              value={settings.support_email}
              onChange={(e) => setSettings({ ...settings, support_email: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Default AI Model</label>
            <select
              value={settings.default_ai_model}
              onChange={(e) => setSettings({ ...settings, default_ai_model: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="gpt-5.2">GPT-5.2</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="claude-sonnet">Claude Sonnet</option>
            </select>
          </div>
        </div>
      </div>

      {/* Integration Keys */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Key className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">API Integrations</h3>
            <p className="text-white/50 text-sm">Configure third-party API keys</p>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">OpenAI API Key</label>
            <input
              type="password"
              value={settings.openai_api_key}
              onChange={(e) => setSettings({ ...settings, openai_api_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="sk-..."
            />
            <p className="text-white/40 text-xs mt-1">Used for AI content generation and audits</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Stripe API Key</label>
            <input
              type="password"
              value={settings.stripe_api_key}
              onChange={(e) => setSettings({ ...settings, stripe_api_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="sk_..."
            />
            <p className="text-white/40 text-xs mt-1">Used for payment processing</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Resend API Key</label>
            <input
              type="password"
              value={settings.resend_api_key}
              onChange={(e) => setSettings({ ...settings, resend_api_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="re_..."
            />
            <p className="text-white/40 text-xs mt-1">Used for transactional emails</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Meta API Key (Instagram)</label>
            <input
              type="password"
              value={settings.meta_api_key}
              onChange={(e) => setSettings({ ...settings, meta_api_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="EAA..."
            />
            <p className="text-white/40 text-xs mt-1">Used for real Instagram data (requires Meta approval)</p>
          </div>
        </div>
      </div>

      {/* Warning */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-amber-400 font-medium">Security Notice</p>
          <p className="text-amber-400/70 text-sm mt-1">
            API keys are sensitive credentials. Never share them publicly. Changes to these settings affect the entire platform.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
