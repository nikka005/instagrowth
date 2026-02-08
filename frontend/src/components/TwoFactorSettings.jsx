import React, { useState, useEffect } from 'react';
import { Shield, Smartphone, Key, AlertCircle, Check, Copy, Eye, EyeOff, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TwoFactorSettings = () => {
  const [status, setStatus] = useState({ is_enabled: false, has_backup_codes: false });
  const [loading, setLoading] = useState(true);
  const [setupData, setSetupData] = useState(null);
  const [verifyCode, setVerifyCode] = useState('');
  const [disableData, setDisableData] = useState({ password: '', code: '' });
  const [showSetup, setShowSetup] = useState(false);
  const [showDisable, setShowDisable] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/2fa/status`, { credentials: 'include' });
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch 2FA status:', error);
    } finally {
      setLoading(false);
    }
  };

  const startSetup = async () => {
    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/2fa/setup`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setSetupData(data);
        setShowSetup(true);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start setup');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setActionLoading(false);
    }
  };

  const verifyAndEnable = async () => {
    if (!verifyCode || verifyCode.length !== 6) {
      toast.error('Please enter a 6-digit code');
      return;
    }

    setActionLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/auth/2fa/verify?code=${verifyCode}`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        toast.success('2FA enabled successfully!');
        setShowSetup(false);
        setSetupData(null);
        setVerifyCode('');
        fetchStatus();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Invalid code');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setActionLoading(false);
    }
  };

  const disable2FA = async () => {
    if (!disableData.password || !disableData.code) {
      toast.error('Please fill all fields');
      return;
    }

    setActionLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/api/auth/2fa/disable?password=${encodeURIComponent(disableData.password)}&code=${disableData.code}`,
        { method: 'POST', credentials: 'include' }
      );

      if (response.ok) {
        toast.success('2FA disabled');
        setShowDisable(false);
        setDisableData({ password: '', code: '' });
        fetchStatus();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to disable 2FA');
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setActionLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <div className="bg-[#12121A] rounded-xl border border-white/10 p-6">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-xl ${status.is_enabled ? 'bg-green-500/20' : 'bg-white/5'}`}>
            <Shield className={`w-6 h-6 ${status.is_enabled ? 'text-green-400' : 'text-white/40'}`} />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white">Two-Factor Authentication</h3>
            <p className="text-white/50 text-sm mt-1">
              {status.is_enabled 
                ? 'Your account is protected with 2FA'
                : 'Add an extra layer of security to your account'
              }
            </p>
            
            <div className="flex items-center gap-3 mt-4">
              {status.is_enabled ? (
                <>
                  <span className="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 text-green-400 rounded-full text-sm">
                    <Check className="w-4 h-4" />
                    Enabled
                  </span>
                  <Button
                    onClick={() => setShowDisable(true)}
                    variant="outline"
                    className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                  >
                    Disable 2FA
                  </Button>
                </>
              ) : (
                <Button
                  onClick={startSetup}
                  disabled={actionLoading}
                  className="bg-indigo-500 hover:bg-indigo-600"
                >
                  {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Smartphone className="w-4 h-4 mr-2" />}
                  Enable 2FA
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Setup Modal */}
      {showSetup && setupData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-[#12121A] rounded-2xl w-full max-w-md border border-white/10">
            <div className="p-6 border-b border-white/10">
              <h2 className="text-xl font-bold text-white">Set Up Two-Factor Authentication</h2>
            </div>
            
            <div className="p-6 space-y-6">
              {/* QR Code */}
              <div className="text-center">
                <p className="text-white/70 text-sm mb-4">
                  Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                </p>
                <div className="inline-block p-4 bg-white rounded-xl">
                  <img src={setupData.qr_code} alt="QR Code" className="w-48 h-48" />
                </div>
              </div>

              {/* Manual Entry */}
              <div className="text-center">
                <p className="text-white/50 text-xs mb-2">Or enter this code manually:</p>
                <div className="flex items-center justify-center gap-2">
                  <code className="px-3 py-2 bg-white/5 rounded-lg text-indigo-400 font-mono text-sm">
                    {setupData.secret}
                  </code>
                  <button onClick={() => copyToClipboard(setupData.secret)} className="p-2 text-white/50 hover:text-white">
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Verify */}
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">
                  Enter the 6-digit code from your app
                </label>
                <Input
                  type="text"
                  value={verifyCode}
                  onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="000000"
                  className="text-center text-2xl tracking-widest bg-white/5 border-white/10"
                  maxLength={6}
                />
              </div>

              {/* Backup Codes */}
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-amber-400 font-medium text-sm">Backup Codes</span>
                  <button 
                    onClick={() => setShowBackupCodes(!showBackupCodes)}
                    className="text-amber-400/70 hover:text-amber-400"
                  >
                    {showBackupCodes ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-amber-400/70 text-xs mb-3">
                  Save these codes in a safe place. You can use them if you lose access to your authenticator app.
                </p>
                {showBackupCodes && (
                  <div className="grid grid-cols-2 gap-2">
                    {setupData.backup_codes.map((code, idx) => (
                      <code key={idx} className="px-2 py-1 bg-black/30 rounded text-amber-400 text-xs font-mono text-center">
                        {code}
                      </code>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="p-6 border-t border-white/10 flex justify-end gap-3">
              <Button
                onClick={() => { setShowSetup(false); setSetupData(null); setVerifyCode(''); }}
                variant="ghost"
              >
                Cancel
              </Button>
              <Button
                onClick={verifyAndEnable}
                disabled={actionLoading || verifyCode.length !== 6}
                className="bg-indigo-500 hover:bg-indigo-600"
              >
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Enable 2FA
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Disable Modal */}
      {showDisable && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-[#12121A] rounded-2xl w-full max-w-md border border-white/10">
            <div className="p-6 border-b border-white/10">
              <h2 className="text-xl font-bold text-white">Disable Two-Factor Authentication</h2>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-400/70 text-sm">
                  Disabling 2FA will make your account less secure. Make sure you have other security measures in place.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Password</label>
                <Input
                  type="password"
                  value={disableData.password}
                  onChange={(e) => setDisableData({ ...disableData, password: e.target.value })}
                  placeholder="Enter your password"
                  className="bg-white/5 border-white/10"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">2FA Code</label>
                <Input
                  type="text"
                  value={disableData.code}
                  onChange={(e) => setDisableData({ ...disableData, code: e.target.value.replace(/\D/g, '').slice(0, 6) })}
                  placeholder="000000"
                  className="text-center bg-white/5 border-white/10"
                  maxLength={6}
                />
              </div>
            </div>

            <div className="p-6 border-t border-white/10 flex justify-end gap-3">
              <Button onClick={() => setShowDisable(false)} variant="ghost">Cancel</Button>
              <Button
                onClick={disable2FA}
                disabled={actionLoading}
                className="bg-red-500 hover:bg-red-600"
              >
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Disable 2FA
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Info Card */}
      <div className="bg-[#12121A] rounded-xl border border-white/10 p-6">
        <h4 className="text-white font-medium mb-3">What is Two-Factor Authentication?</h4>
        <p className="text-white/50 text-sm leading-relaxed">
          Two-factor authentication (2FA) adds an extra layer of security to your account by requiring 
          both your password and a time-based code from your authenticator app to sign in. 
          Even if someone knows your password, they won't be able to access your account without your phone.
        </p>
        
        <div className="mt-4 flex flex-wrap gap-4">
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <Key className="w-4 h-4" />
            <span>Works with Google Authenticator</span>
          </div>
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <Smartphone className="w-4 h-4" />
            <span>Works with Authy</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoFactorSettings;
