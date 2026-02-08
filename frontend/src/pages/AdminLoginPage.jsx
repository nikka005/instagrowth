import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, Lock, Mail, Key, AlertCircle } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminLoginPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    adminCode: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showAdminCode, setShowAdminCode] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/admin-auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          admin_code: formData.adminCode
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Admin login failed');
      }

      localStorage.setItem('admin_token', data.token);
      localStorage.setItem('admin_user', JSON.stringify(data.admin));
      navigate('/admin');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        {/* Admin Badge */}
        <div className="flex justify-center mb-6">
          <div className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-full">
            <Shield className="w-5 h-5 text-red-400" />
            <span className="text-red-400 font-semibold text-sm">ADMIN ACCESS</span>
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-[#12121A] border border-red-500/20 rounded-2xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto bg-gradient-to-br from-red-500 to-orange-500 rounded-2xl flex items-center justify-center mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Admin Portal</h1>
            <p className="text-gray-400 text-sm">Restricted access - Authorized personnel only</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Admin Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full pl-11 pr-4 py-3 bg-[#1A1A24] border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors"
                  placeholder="admin@instagrowth.com"
                  required
                  data-testid="admin-email-input"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-11 pr-11 py-3 bg-[#1A1A24] border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors"
                  placeholder="••••••••"
                  required
                  data-testid="admin-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Admin Code Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Admin Security Code
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type={showAdminCode ? 'text' : 'password'}
                  value={formData.adminCode}
                  onChange={(e) => setFormData({ ...formData, adminCode: e.target.value })}
                  className="w-full pl-11 pr-11 py-3 bg-[#1A1A24] border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-red-500 focus:ring-1 focus:ring-red-500 transition-colors"
                  placeholder="Enter admin code"
                  required
                  data-testid="admin-code-input"
                />
                <button
                  type="button"
                  onClick={() => setShowAdminCode(!showAdminCode)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showAdminCode ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Contact system administrator for the security code
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-red-500 to-orange-500 text-white font-semibold rounded-lg hover:from-red-600 hover:to-orange-600 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-[#12121A] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="admin-login-btn"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Authenticating...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Shield className="w-5 h-5" />
                  Access Admin Portal
                </span>
              )}
            </button>
          </form>

          {/* Back to User Login */}
          <div className="mt-6 pt-6 border-t border-gray-800">
            <p className="text-center text-sm text-gray-400">
              Not an admin?{' '}
              <a href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
                Go to User Login
              </a>
            </p>
          </div>
        </div>

        {/* Security Notice */}
        <p className="mt-6 text-center text-xs text-gray-500">
          All admin access attempts are logged and monitored.
          <br />
          Unauthorized access is prohibited.
        </p>
      </div>
    </div>
  );
};

export default AdminLoginPage;
