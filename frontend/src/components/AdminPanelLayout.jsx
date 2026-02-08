import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { 
  LayoutDashboard, Users, CreditCard, Package, Instagram, 
  Cpu, DollarSign, UsersRound, Settings, FileText, LogOut,
  Menu, X, Shield, Bell, ChevronDown, User, TrendingUp, AlertTriangle, Book, MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API_URL.replace('https://', 'wss://').replace('http://', 'ws://');

const AdminPanelLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [admin, setAdmin] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const navItems = [
    { path: '/admin-panel', icon: LayoutDashboard, label: 'Dashboard', permission: '*' },
    { path: '/admin-panel/users', icon: Users, label: 'Users', permission: 'users' },
    { path: '/admin-panel/subscriptions', icon: CreditCard, label: 'Subscriptions', permission: 'subscriptions' },
    { path: '/admin-panel/plans', icon: Package, label: 'Plans', permission: 'plans' },
    { path: '/admin-panel/instagram', icon: Instagram, label: 'Instagram Accounts', permission: 'accounts' },
    { path: '/admin-panel/ai-usage', icon: Cpu, label: 'AI Usage', permission: '*' },
    { path: '/admin-panel/revenue', icon: DollarSign, label: 'Revenue', permission: 'revenue' },
    { path: '/admin-panel/tickets', icon: MessageSquare, label: 'Support Tickets', permission: '*' },
    { path: '/admin-panel/team', icon: UsersRound, label: 'Team Management', permission: '*' },
    { path: '/admin-panel/settings', icon: Settings, label: 'System Settings', permission: '*' },
    { path: '/admin-panel/logs', icon: FileText, label: 'Logs', permission: 'logs' },
    { path: '/admin-panel/docs', icon: Book, label: 'Documentation', permission: '*' },
  ];

  useEffect(() => {
    verifyAdmin();
  }, []);

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    if (!admin || wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const wsUrl = `${WS_URL}/api/admin-ws/${admin.admin_id}?role=${admin.role}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Admin WebSocket connected');
        // Send ping every 30 seconds to keep connection alive
        const pingInterval = setInterval(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
          }
        }, 30000);
        wsRef.current.pingInterval = pingInterval;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'pong' || data.type === 'connection') return;
          
          // Add to notifications
          const notification = {
            id: Date.now(),
            type: data.type,
            title: data.title || 'Notification',
            message: data.message || '',
            priority: data.priority || 'normal',
            timestamp: new Date().toISOString()
          };
          
          setNotifications(prev => [notification, ...prev].slice(0, 50));
          
          // Show toast for high priority
          if (data.priority === 'high') {
            toast(data.title, { description: data.message });
          }
        } catch (e) {
          console.error('WebSocket message error:', e);
        }
      };

      wsRef.current.onclose = () => {
        console.log('Admin WebSocket disconnected');
        if (wsRef.current?.pingInterval) {
          clearInterval(wsRef.current.pingInterval);
        }
        // Reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  }, [admin]);

  useEffect(() => {
    if (admin) {
      connectWebSocket();
    }
    return () => {
      if (wsRef.current) {
        if (wsRef.current.pingInterval) clearInterval(wsRef.current.pingInterval);
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, [admin, connectWebSocket]);

  const verifyAdmin = async () => {
    try {
      const token = localStorage.getItem('admin_panel_token');
      if (!token) {
        navigate('/admin-panel/login');
        return;
      }

      const response = await fetch(`${API_URL}/api/admin-panel/auth/me`, {
        credentials: 'include',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Not authenticated');
      }

      const data = await response.json();
      setAdmin(data);
    } catch (error) {
      localStorage.removeItem('admin_panel_token');
      navigate('/admin-panel/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('admin_panel_token');
      await fetch(`${API_URL}/api/admin-panel/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
    localStorage.removeItem('admin_panel_token');
    navigate('/admin-panel/login');
  };

  const hasPermission = (permission) => {
    if (!admin) return false;
    const perms = admin.permissions || [];
    return perms.includes('*') || perms.includes(permission);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a]">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#1e293b] transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-white">Admin Panel</span>
            </div>
            <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-white/60 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              if (!hasPermission(item.permission)) return null;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-indigo-500/20 text-indigo-400' 
                      : 'text-white/60 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User Info */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
                {admin?.name?.charAt(0) || 'A'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{admin?.name}</p>
                <p className="text-xs text-white/50 capitalize">{admin?.role?.replace('_', ' ')}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 lg:hidden" 
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="lg:ml-64">
        {/* Top Header */}
        <header className="sticky top-0 z-30 h-16 bg-[#0f172a]/80 backdrop-blur-xl border-b border-white/10">
          <div className="flex items-center justify-between h-full px-4 lg:px-6">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 text-white/60 hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>

            <div className="flex items-center gap-3 ml-auto">
              {admin?.is_2fa_enabled && (
                <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-400 rounded-full">
                  2FA Enabled
                </span>
              )}
              
              {/* Notifications Dropdown */}
              <div className="relative">
                <button 
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 text-white/60 hover:text-white relative"
                >
                  <Bell className="w-5 h-5" />
                  {notifications.length > 0 && (
                    <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
                  )}
                </button>
                
                {showNotifications && (
                  <div className="absolute right-0 top-full mt-2 w-80 bg-[#1e293b] border border-white/10 rounded-xl shadow-xl overflow-hidden z-50">
                    <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
                      <span className="font-medium text-white">Notifications</span>
                      {notifications.length > 0 && (
                        <button 
                          onClick={() => setNotifications([])}
                          className="text-xs text-white/50 hover:text-white"
                        >
                          Clear all
                        </button>
                      )}
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                      {notifications.length === 0 ? (
                        <div className="p-4 text-center text-white/50 text-sm">
                          No notifications
                        </div>
                      ) : (
                        notifications.map((notif) => (
                          <div key={notif.id} className="px-4 py-3 border-b border-white/5 hover:bg-white/5">
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded-lg ${
                                notif.type === 'new_user' ? 'bg-green-500/20 text-green-400' :
                                notif.type === 'new_payment' ? 'bg-blue-500/20 text-blue-400' :
                                notif.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                                'bg-indigo-500/20 text-indigo-400'
                              }`}>
                                {notif.type === 'new_user' ? <User className="w-4 h-4" /> :
                                 notif.type === 'new_payment' ? <CreditCard className="w-4 h-4" /> :
                                 notif.type?.includes('upgrade') ? <TrendingUp className="w-4 h-4" /> :
                                 notif.priority === 'high' ? <AlertTriangle className="w-4 h-4" /> :
                                 <Bell className="w-4 h-4" />}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white truncate">{notif.title}</p>
                                <p className="text-xs text-white/50 truncate">{notif.message}</p>
                                <p className="text-xs text-white/30 mt-1">
                                  {new Date(notif.timestamp).toLocaleTimeString()}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-4 lg:p-6">
          {React.cloneElement(children, { admin })}
        </main>
      </div>
    </div>
  );
};

export default AdminPanelLayout;
