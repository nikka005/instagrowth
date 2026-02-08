import React, { useState, useEffect } from 'react';
import { 
  Settings, Save, Key, Mail, Globe, Shield, AlertCircle, Loader2, Check, 
  ExternalLink, RefreshCw, CreditCard, Instagram, Cpu, X, CheckCircle2
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SettingsPage = ({ admin }) => {
  const [settings, setSettings] = useState({
    platform_name: 'InstaGrowth OS',
    support_email: '',
    default_ai_model: 'gpt-5.2',
    openai_api_key: '',
    stripe_secret_key: '',
    stripe_publishable_key: '',
    stripe_webhook_secret: '',
    resend_api_key: '',
    meta_app_id: '',
    meta_app_secret: '',
    meta_access_token: '',
    instagram_business_id: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingConnection, setTestingConnection] = useState({});
  const [connectionStatus, setConnectionStatus] = useState({
    openai: null,
    stripe: null,
    resend: null,
    meta: null
  });

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
        toast.success('Settings saved successfully');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (service) => {
    setTestingConnection(prev => ({ ...prev, [service]: true }));
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/settings/test-connection?service=${service}`, {
        method: 'POST',
        credentials: 'include',
        headers
      });
      const data = await response.json();
      setConnectionStatus(prev => ({ ...prev, [service]: data.success }));
      if (data.success) {
        toast.success(`${service} connection successful`);
      } else {
        toast.error(data.message || `${service} connection failed`);
      }
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, [service]: false }));
      toast.error(`Failed to test ${service} connection`);
    } finally {
      setTestingConnection(prev => ({ ...prev, [service]: false }));
    }
  };

  const ConnectionBadge = ({ status }) => {
    if (status === null) return null;
    return status ? (
      <span className="flex items-center gap-1 text-xs text-green-400 bg-green-500/20 px-2 py-1 rounded-full">
        <CheckCircle2 className="w-3 h-3" /> Connected
      </span>
    ) : (
      <span className="flex items-center gap-1 text-xs text-red-400 bg-red-500/20 px-2 py-1 rounded-full">
        <X className="w-3 h-3" /> Failed
      </span>
    );
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
          <p className="text-white/50 mt-1">Configure platform settings and API integrations</p>
        </div>
        <button
          onClick={saveSettings}
          disabled={saving}
          className="flex items-center gap-2 px-5 py-2.5 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:opacity-50 font-medium"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Save All Settings
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
              placeholder="support@yourdomain.com"
            />
          </div>
        </div>
      </div>

      {/* OpenAI / AI Settings */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Cpu className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">OpenAI Integration</h3>
              <p className="text-white/50 text-sm">AI content generation powered by Emergent Universal Key</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ConnectionBadge status={connectionStatus.openai} />
            <button
              onClick={() => testConnection('openai')}
              disabled={testingConnection.openai}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/70 text-sm"
            >
              {testingConnection.openai ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Test Connection
            </button>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Default AI Model</label>
            <select
              value={settings.default_ai_model}
              onChange={(e) => setSettings({ ...settings, default_ai_model: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="gpt-5.2">GPT-5.2 (Recommended)</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini (Faster)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">OpenAI API Key</label>
            <input
              type="password"
              value={settings.openai_api_key}
              onChange={(e) => setSettings({ ...settings, openai_api_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="sk-... or Emergent Universal Key"
            />
            <p className="text-white/40 text-xs mt-2">
              Using <span className="text-green-400">Emergent Universal Key</span> - supports GPT-5.2, GPT-4o, Claude, and Gemini models
            </p>
          </div>
        </div>
      </div>

      {/* Stripe Payment Settings */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <CreditCard className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Stripe Payment Integration</h3>
              <p className="text-white/50 text-sm">Process subscriptions and payments</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ConnectionBadge status={connectionStatus.stripe} />
            <button
              onClick={() => testConnection('stripe')}
              disabled={testingConnection.stripe}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/70 text-sm"
            >
              {testingConnection.stripe ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Test Connection
            </button>
            <a
              href="https://dashboard.stripe.com/apikeys"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 px-3 py-1.5 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-purple-400 text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              Get Keys
            </a>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Stripe Secret Key</label>
            <input
              type="password"
              value={settings.stripe_secret_key}
              onChange={(e) => setSettings({ ...settings, stripe_secret_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="sk_live_... or sk_test_..."
            />
            <p className="text-white/40 text-xs mt-1">Server-side key for processing payments</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Stripe Publishable Key</label>
            <input
              type="text"
              value={settings.stripe_publishable_key}
              onChange={(e) => setSettings({ ...settings, stripe_publishable_key: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="pk_live_... or pk_test_..."
            />
            <p className="text-white/40 text-xs mt-1">Client-side key for checkout forms</p>
          </div>
          
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-white/70 mb-2">Stripe Webhook Secret</label>
            <input
              type="password"
              value={settings.stripe_webhook_secret}
              onChange={(e) => setSettings({ ...settings, stripe_webhook_secret: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="whsec_..."
            />
            <p className="text-white/40 text-xs mt-1">
              For webhook verification. Create webhook at{' '}
              <a href="https://dashboard.stripe.com/webhooks" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:underline">
                Stripe Dashboard → Webhooks
              </a>
              {' '}pointing to: <code className="bg-white/10 px-1 rounded">{API_URL}/api/billing/webhook</code>
            </p>
          </div>
        </div>

        <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
          <h4 className="text-sm font-medium text-purple-400 mb-2">Setup Instructions:</h4>
          <ol className="text-xs text-white/60 space-y-1 list-decimal list-inside">
            <li>Go to <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:underline">Stripe Dashboard → API Keys</a></li>
            <li>Copy your Secret key (sk_live_...) and Publishable key (pk_live_...)</li>
            <li>Create a webhook endpoint at <a href="https://dashboard.stripe.com/webhooks" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:underline">Webhooks</a></li>
            <li>Set webhook URL to: <code className="bg-white/10 px-1 rounded">{API_URL}/api/billing/webhook</code></li>
            <li>Select events: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted</li>
            <li>Copy the Webhook signing secret (whsec_...)</li>
          </ol>
        </div>
      </div>

      {/* Meta/Instagram API Settings */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-pink-500/20 rounded-lg">
              <Instagram className="w-5 h-5 text-pink-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Meta / Instagram API Integration</h3>
              <p className="text-white/50 text-sm">Connect to Instagram for real account data</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ConnectionBadge status={connectionStatus.meta} />
            <button
              onClick={() => testConnection('meta')}
              disabled={testingConnection.meta}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/70 text-sm"
            >
              {testingConnection.meta ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Test Connection
            </button>
            <a
              href="https://developers.facebook.com/apps/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 px-3 py-1.5 bg-pink-500/20 hover:bg-pink-500/30 border border-pink-500/30 rounded-lg text-pink-400 text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              Meta Developer
            </a>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Meta App ID</label>
            <input
              type="text"
              value={settings.meta_app_id}
              onChange={(e) => setSettings({ ...settings, meta_app_id: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="123456789012345"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Meta App Secret</label>
            <input
              type="password"
              value={settings.meta_app_secret}
              onChange={(e) => setSettings({ ...settings, meta_app_secret: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="abc123def456..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Long-Lived Access Token</label>
            <input
              type="password"
              value={settings.meta_access_token}
              onChange={(e) => setSettings({ ...settings, meta_access_token: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="EAAxxxxxxx..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Instagram Business Account ID</label>
            <input
              type="text"
              value={settings.instagram_business_id}
              onChange={(e) => setSettings({ ...settings, instagram_business_id: e.target.value })}
              className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none font-mono"
              placeholder="17841400000000000"
            />
          </div>
        </div>

        <div className="mt-4 p-4 bg-pink-500/10 border border-pink-500/20 rounded-lg">
          <h4 className="text-sm font-medium text-pink-400 mb-2">Setup Instructions:</h4>
          <ol className="text-xs text-white/60 space-y-1 list-decimal list-inside">
            <li>Go to <a href="https://developers.facebook.com/apps/" target="_blank" rel="noopener noreferrer" className="text-pink-400 hover:underline">Meta for Developers</a> and create a new app (Business type)</li>
            <li>Add "Instagram Graph API" product to your app</li>
            <li>Go to Settings → Basic to get your App ID and App Secret</li>
            <li>Generate a User Access Token from Graph API Explorer</li>
            <li>Exchange for a Long-Lived Token (valid 60 days)</li>
            <li>Get your Instagram Business Account ID from the API</li>
            <li>Required permissions: instagram_basic, instagram_content_publish, pages_read_engagement</li>
          </ol>
        </div>

        <div className="mt-4 p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-amber-400 font-medium text-sm">App Review Required</p>
              <p className="text-amber-400/70 text-xs mt-1">
                To access real Instagram data for all users, your Meta app must pass App Review. 
                Until approved, you can only access data from accounts added as testers.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Email Settings */}
      <div className="bg-[#1e293b] rounded-xl border border-white/5 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Mail className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Email Integration (Resend)</h3>
              <p className="text-white/50 text-sm">Transactional emails for verification and notifications</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ConnectionBadge status={connectionStatus.resend} />
            <button
              onClick={() => testConnection('resend')}
              disabled={testingConnection.resend}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-white/70 text-sm"
            >
              {testingConnection.resend ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Test Connection
            </button>
            <a
              href="https://resend.com/api-keys"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 rounded-lg text-blue-400 text-sm"
            >
              <ExternalLink className="w-4 h-4" />
              Get Key
            </a>
          </div>
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
          <p className="text-white/40 text-xs mt-1">
            Get your API key from <a href="https://resend.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">Resend Dashboard</a>
          </p>
        </div>
      </div>

      {/* Security Warning */}
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-start gap-3">
        <Shield className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-red-400 font-medium">Security Warning</p>
          <p className="text-red-400/70 text-sm mt-1">
            API keys are sensitive credentials. Never share them publicly or commit them to version control. 
            All changes to these settings are logged and affect the entire platform immediately.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
