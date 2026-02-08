import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Users, DollarSign, BarChart3, Instagram, 
  Shield, Search, Loader2, LogOut, History
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminPage = ({ auth }) => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [updatingUser, setUpdatingUser] = useState(null);
  const [adminUser, setAdminUser] = useState(null);
  const [loginHistory, setLoginHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    verifyAdminSession();
  }, []);

  const verifyAdminSession = async () => {
    try {
      // First check if there's an admin token
      const adminToken = localStorage.getItem("admin_token");
      
      if (adminToken) {
        // Verify admin session with dedicated endpoint
        const response = await fetch(`${API_URL}/api/admin-auth/verify`, {
          credentials: "include",
          headers: {
            "Authorization": `Bearer ${adminToken}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setAdminUser(data.admin);
          fetchStats(adminToken);
          fetchUsers(adminToken);
          return;
        }
      }
      
      // Fallback to checking regular auth for admin role
      if (auth.user?.role === "admin") {
        setAdminUser(auth.user);
        fetchStats();
        fetchUsers();
        return;
      }
      
      // Not authenticated as admin - redirect to admin login
      navigate("/admin-login");
    } catch (error) {
      console.error("Admin verification failed:", error);
      navigate("/admin-login");
    }
  };

  const fetchStats = async (token = null) => {
    try {
      const headers = token ? { "Authorization": `Bearer ${token}` } : {};
      const response = await fetch(`${API_URL}/api/admin/stats`, {
        credentials: "include",
        headers
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    }
  };

  const fetchUsers = async (token = null) => {
    try {
      const headers = token ? { "Authorization": `Bearer ${token}` } : {};
      const response = await fetch(`${API_URL}/api/admin/users`, {
        credentials: "include",
        headers
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || data);
      }
    } catch (error) {
      console.error("Failed to fetch users:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLoginHistory = async () => {
    try {
      const adminToken = localStorage.getItem("admin_token");
      const headers = adminToken ? { "Authorization": `Bearer ${adminToken}` } : {};
      const response = await fetch(`${API_URL}/api/admin-auth/login-history`, {
        credentials: "include",
        headers
      });
      if (response.ok) {
        const data = await response.json();
        setLoginHistory(data.login_history || []);
        setShowHistory(true);
      }
    } catch (error) {
      console.error("Failed to fetch login history:", error);
    }
  };

  const handleAdminLogout = async () => {
    try {
      const adminToken = localStorage.getItem("admin_token");
      await fetch(`${API_URL}/api/admin-auth/logout`, {
        method: "POST",
        credentials: "include",
        headers: adminToken ? { "Authorization": `Bearer ${adminToken}` } : {}
      });
    } catch (error) {
      console.error("Logout error:", error);
    }
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    navigate("/admin-login");
  };

  const updateUserRole = async (userId, newRole) => {
    setUpdatingUser(userId);
    try {
      const adminToken = localStorage.getItem("admin_token");
      const headers = adminToken ? { "Authorization": `Bearer ${adminToken}` } : {};
      const response = await fetch(`${API_URL}/api/admin/users/${userId}/role?role=${newRole}`, {
        method: "PUT",
        credentials: "include",
        headers
      });

      if (!response.ok) {
        throw new Error("Failed to update user role");
      }

      toast.success("User role updated!");
      fetchUsers(adminToken);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setUpdatingUser(null);
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case "admin": return "bg-red-500/20 text-red-400 border-red-500/30";
      case "enterprise": return "bg-teal-500/20 text-teal-400 border-teal-500/30";
      case "agency": return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "pro": return "bg-indigo-500/20 text-indigo-400 border-indigo-500/30";
      default: return "bg-white/10 text-white/60 border-white/10";
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (auth.user?.role !== "admin") {
    return (
      <DashboardLayout auth={auth}>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <Shield className="w-16 h-16 text-white/20 mx-auto mb-4" />
            <h2 className="font-display text-2xl font-bold text-white mb-2">Access Denied</h2>
            <p className="text-white/50">You don't have permission to access this page.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Admin Dashboard</h1>
          <p className="text-white/60 mt-1">Manage users and view platform statistics</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Total Users", value: stats?.total_users || 0, icon: <Users className="w-5 h-5" />, color: "text-indigo-400" },
            { label: "Total Accounts", value: stats?.total_accounts || 0, icon: <Instagram className="w-5 h-5" />, color: "text-pink-400" },
            { label: "Total Audits", value: stats?.total_audits || 0, icon: <BarChart3 className="w-5 h-5" />, color: "text-teal-400" },
            { label: "Total Revenue", value: `$${stats?.total_revenue?.toFixed(2) || '0.00'}`, icon: <DollarSign className="w-5 h-5" />, color: "text-green-400" },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
            >
              <div className="flex items-center gap-2 mb-3">
                <span className={stat.color}>{stat.icon}</span>
                <span className="text-sm text-white/50">{stat.label}</span>
              </div>
              <div className="text-3xl font-display font-bold text-white">{stat.value}</div>
            </motion.div>
          ))}
        </div>

        {/* Users by Plan */}
        <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
          <h3 className="font-display font-semibold text-white mb-4">Users by Plan</h3>
          <div className="flex flex-wrap gap-4">
            {stats?.users_by_plan?.map((item) => (
              <div key={item._id} className="flex items-center gap-2">
                <Badge variant="outline" className={getRoleBadgeColor(item._id)}>
                  {item._id || "starter"}
                </Badge>
                <span className="text-white font-medium">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Users Table */}
        <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <h3 className="font-display font-semibold text-white">All Users</h3>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64 h-11 pl-12 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                data-testid="admin-search-input"
              />
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-white/5 hover:bg-transparent">
                    <TableHead className="text-white/50">Name</TableHead>
                    <TableHead className="text-white/50">Email</TableHead>
                    <TableHead className="text-white/50">Role</TableHead>
                    <TableHead className="text-white/50">Accounts</TableHead>
                    <TableHead className="text-white/50">AI Usage</TableHead>
                    <TableHead className="text-white/50">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsers.map((user) => (
                    <TableRow key={user.user_id} className="border-white/5 hover:bg-white/5">
                      <TableCell className="text-white font-medium">{user.name}</TableCell>
                      <TableCell className="text-white/70">{user.email}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getRoleBadgeColor(user.role)}>
                          {user.role || "starter"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-white/70">
                        {user.account_limit || 1}
                      </TableCell>
                      <TableCell className="text-white/70">
                        {user.ai_usage_current || 0}/{user.ai_usage_limit || 10}
                      </TableCell>
                      <TableCell>
                        <Select
                          value={user.role}
                          onValueChange={(value) => updateUserRole(user.user_id, value)}
                          disabled={updatingUser === user.user_id}
                        >
                          <SelectTrigger className="w-32 h-9 bg-white/5 border-white/10 text-white text-sm">
                            {updatingUser === user.user_id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <SelectValue />
                            )}
                          </SelectTrigger>
                          <SelectContent className="bg-[#0F0F11] border-white/10">
                            <SelectItem value="starter" className="text-white">Starter</SelectItem>
                            <SelectItem value="pro" className="text-white">Pro</SelectItem>
                            <SelectItem value="agency" className="text-white">Agency</SelectItem>
                            <SelectItem value="enterprise" className="text-white">Enterprise</SelectItem>
                            <SelectItem value="admin" className="text-white">Admin</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminPage;
