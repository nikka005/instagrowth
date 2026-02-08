import React, { useState, useEffect } from 'react';
import { 
  Mail, Send, Settings, CheckCircle2, XCircle, 
  RefreshCw, Loader2, Play, Clock, Filter, Eye
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const EmailAutomationPage = () => {
  const [templates, setTemplates] = useState([]);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('templates');
  const [sendingTest, setSendingTest] = useState(null);
  const [runningTasks, setRunningTasks] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [logFilter, setLogFilter] = useState('');

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [templatesRes, logsRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/api/email-automation/templates`, { headers }),
        fetch(`${API_URL}/api/email-automation/logs?limit=50`, { headers }),
        fetch(`${API_URL}/api/email-automation/stats`, { headers })
      ]);

      if (templatesRes.ok) {
        const data = await templatesRes.json();
        setTemplates(data.templates);
      }
      if (logsRes.ok) {
        const data = await logsRes.json();
        setLogs(data.logs);
      }
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const toggleTemplate = async (templateId, enabled) => {
    try {
      const response = await fetch(
        `${API_URL}/api/email-automation/templates/${templateId}/toggle?enabled=${!enabled}`,
        { method: 'PUT', headers }
      );
      if (response.ok) {
        toast.success(`Template ${!enabled ? 'enabled' : 'disabled'}`);
        setTemplates(prev => prev.map(t => 
          t.id === templateId ? { ...t, enabled: !enabled } : t
        ));
      }
    } catch (error) {
      toast.error('Failed to toggle template');
    }
  };

  const sendTestEmail = async (templateId) => {
    if (!testEmail) {
      toast.error('Please enter a test email address');
      return;
    }
    
    setSendingTest(templateId);
    try {
      const response = await fetch(
        `${API_URL}/api/email-automation/send-test?template_id=${templateId}&recipient=${encodeURIComponent(testEmail)}`,
        { method: 'POST', headers }
      );
      
      if (response.ok) {
        toast.success('Test email sent!');
      } else {
        throw new Error('Failed to send');
      }
    } catch (error) {
      toast.error('Failed to send test email');
    } finally {
      setSendingTest(null);
    }
  };

  const runScheduledTasks = async () => {
    setRunningTasks(true);
    try {
      const response = await fetch(
        `${API_URL}/api/email-automation/run-scheduled-tasks`,
        { method: 'POST', headers }
      );
      
      if (response.ok) {
        const data = await response.json();
        toast.success(`Tasks completed: ${JSON.stringify(data)}`);
        fetchData();
      }
    } catch (error) {
      toast.error('Failed to run tasks');
    } finally {
      setRunningTasks(false);
    }
  };

  const fetchTemplatePreview = async (templateId) => {
    try {
      const response = await fetch(
        `${API_URL}/api/email-automation/templates/${templateId}`,
        { headers }
      );
      if (response.ok) {
        const data = await response.json();
        setPreviewTemplate(data);
      }
    } catch (error) {
      toast.error('Failed to load preview');
    }
  };

  const getTriggerBadge = (trigger) => {
    const badges = {
      'user_registration': 'bg-green-500/20 text-green-400',
      'subscription_created': 'bg-blue-500/20 text-blue-400',
      'subscription_cancelled': 'bg-red-500/20 text-red-400',
      'scheduled': 'bg-yellow-500/20 text-yellow-400',
      'scheduled_weekly': 'bg-purple-500/20 text-purple-400',
      'credit_threshold': 'bg-orange-500/20 text-orange-400',
      'referral_signup': 'bg-pink-500/20 text-pink-400'
    };
    return badges[trigger] || 'bg-gray-500/20 text-gray-400';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Email Automation</h1>
          <p className="text-white/50 mt-1">Manage automated email campaigns and templates</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={runScheduledTasks}
            disabled={runningTasks}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 disabled:opacity-50"
          >
            {runningTasks ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Run Scheduled Tasks
          </button>
          <button
            onClick={fetchData}
            className="p-2 text-white/60 hover:text-white hover:bg-white/5 rounded-lg"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="p-5 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/20 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <Mail className="w-5 h-5 text-indigo-400" />
              <span className="text-white/60 text-sm">Templates</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.templates_count}</p>
          </div>
          <div className="p-5 bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/20 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle2 className="w-5 h-5 text-green-400" />
              <span className="text-white/60 text-sm">Sent (7 days)</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.recent_7_days}</p>
          </div>
          <div className="p-5 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/20 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <Send className="w-5 h-5 text-blue-400" />
              <span className="text-white/60 text-sm">Total Sent</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {stats.by_type?.reduce((acc, t) => acc + t.sent, 0) || 0}
            </p>
          </div>
          <div className="p-5 bg-gradient-to-br from-red-500/20 to-pink-500/20 border border-red-500/20 rounded-xl">
            <div className="flex items-center gap-3 mb-2">
              <XCircle className="w-5 h-5 text-red-400" />
              <span className="text-white/60 text-sm">Failed</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {stats.by_type?.reduce((acc, t) => acc + t.failed, 0) || 0}
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10">
        {['templates', 'logs'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              activeTab === tab
                ? 'text-indigo-400 border-b-2 border-indigo-400'
                : 'text-white/50 hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Test Email Input */}
      {activeTab === 'templates' && (
        <div className="flex items-center gap-3 p-4 bg-[#1e293b] border border-white/10 rounded-xl">
          <span className="text-white/60 text-sm">Test Email:</span>
          <input
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="admin@example.com"
            className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/30 text-sm"
          />
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="grid gap-4">
          {templates.map((template) => (
            <div
              key={template.id}
              className={`p-5 rounded-xl border ${
                template.enabled 
                  ? 'bg-[#1e293b] border-white/10' 
                  : 'bg-[#1e293b]/50 border-white/5'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Mail className={`w-5 h-5 ${template.enabled ? 'text-indigo-400' : 'text-white/30'}`} />
                    <h3 className="font-semibold text-white">{template.name}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${getTriggerBadge(template.trigger)}`}>
                      {template.trigger.replace(/_/g, ' ')}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      template.enabled ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {template.enabled ? 'Active' : 'Disabled'}
                    </span>
                  </div>
                  <p className="text-white/50 text-sm">{template.subject}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => fetchTemplatePreview(template.id)}
                    className="p-2 text-white/40 hover:text-white hover:bg-white/5 rounded-lg"
                    title="Preview"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => sendTestEmail(template.id)}
                    disabled={sendingTest === template.id || !testEmail}
                    className="flex items-center gap-1 px-3 py-1.5 bg-indigo-500/20 text-indigo-400 rounded-lg text-sm hover:bg-indigo-500/30 disabled:opacity-50"
                  >
                    {sendingTest === template.id ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <Send className="w-3 h-3" />
                    )}
                    Test
                  </button>
                  <button
                    onClick={() => toggleTemplate(template.id, template.enabled)}
                    className={`px-3 py-1.5 rounded-lg text-sm ${
                      template.enabled 
                        ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                        : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                    }`}
                  >
                    {template.enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Filter className="w-4 h-4 text-white/40" />
            <select
              value={logFilter}
              onChange={(e) => setLogFilter(e.target.value)}
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm"
            >
              <option value="">All Types</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          <div className="bg-[#1e293b] border border-white/10 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left px-4 py-3 text-white/60 text-sm font-medium">Type</th>
                  <th className="text-left px-4 py-3 text-white/60 text-sm font-medium">Recipient</th>
                  <th className="text-left px-4 py-3 text-white/60 text-sm font-medium">Subject</th>
                  <th className="text-left px-4 py-3 text-white/60 text-sm font-medium">Status</th>
                  <th className="text-left px-4 py-3 text-white/60 text-sm font-medium">Time</th>
                </tr>
              </thead>
              <tbody>
                {logs
                  .filter(log => !logFilter || log.type === logFilter)
                  .map((log, idx) => (
                  <tr key={idx} className="border-b border-white/5">
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded text-xs">
                        {log.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-white/70 text-sm">{log.recipient}</td>
                    <td className="px-4 py-3 text-white text-sm max-w-xs truncate">{log.subject}</td>
                    <td className="px-4 py-3">
                      {log.status === 'sent' ? (
                        <span className="flex items-center gap-1 text-green-400 text-sm">
                          <CheckCircle2 className="w-4 h-4" /> Sent
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-400 text-sm">
                          <XCircle className="w-4 h-4" /> Failed
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-white/50 text-sm">
                      {new Date(log.sent_at || log.attempted_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-white/40">
                      No email logs yet
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Template Preview Modal */}
      {previewTemplate && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1e293b] rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h3 className="font-semibold text-white">{previewTemplate.name} - Preview</h3>
              <button
                onClick={() => setPreviewTemplate(null)}
                className="text-white/40 hover:text-white"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[60vh]">
              <div 
                dangerouslySetInnerHTML={{ __html: previewTemplate.template_html }}
                className="bg-white rounded-lg"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailAutomationPage;
