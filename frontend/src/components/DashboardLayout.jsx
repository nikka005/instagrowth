import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { 
  LayoutDashboard, Instagram, BarChart3, FileText, Calendar,
  CreditCard, Settings, LogOut, Menu, X, ChevronDown, Bell,
  Sparkles, Users
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../components/ui/dropdown-menu";

const DashboardLayout = ({ children, auth }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { icon: <LayoutDashboard className="w-5 h-5" />, label: "Dashboard", path: "/dashboard" },
    { icon: <Instagram className="w-5 h-5" />, label: "Accounts", path: "/accounts" },
    { icon: <BarChart3 className="w-5 h-5" />, label: "AI Audit", path: "/audit" },
    { icon: <Sparkles className="w-5 h-5" />, label: "Content Engine", path: "/content" },
    { icon: <Calendar className="w-5 h-5" />, label: "Growth Planner", path: "/planner" },
    { icon: <CreditCard className="w-5 h-5" />, label: "Billing", path: "/billing" },
    { icon: <Settings className="w-5 h-5" />, label: "Settings", path: "/settings" },
  ];

  // Add team link for agency/enterprise users
  if (auth.user?.role === "agency" || auth.user?.role === "enterprise" || auth.user?.role === "admin") {
    navItems.splice(6, 0, { icon: <Users className="w-5 h-5" />, label: "Team", path: "/team" });
  }

  // Add admin link if user is admin
  if (auth.user?.role === "admin") {
    navItems.push({ icon: <Users className="w-5 h-5" />, label: "Admin", path: "/admin" });
  }

  const handleLogout = async () => {
    await auth.logout();
    navigate("/login");
  };

  const getPlanBadgeColor = (role) => {
    switch (role) {
      case "pro": return "bg-indigo-500/20 text-indigo-400 border-indigo-500/30";
      case "agency": return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "enterprise": return "bg-teal-500/20 text-teal-400 border-teal-500/30";
      case "admin": return "bg-red-500/20 text-red-400 border-red-500/30";
      default: return "bg-white/10 text-white/60 border-white/10";
    }
  };

  return (
    <div className="min-h-screen bg-[#030305] flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#0A0A0B] border-r border-white/5 transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-4 border-b border-white/5">
            <Link to="/dashboard" className="flex items-center gap-3" data-testid="sidebar-logo">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                <Instagram className="w-6 h-6 text-white" />
              </div>
              <span className="font-display font-bold text-lg text-white">InstaGrowth OS</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    isActive 
                      ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' 
                      : 'text-white/60 hover:text-white hover:bg-white/5'
                  }`}
                  data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                >
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-white/5">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/5">
              <Avatar className="w-10 h-10">
                <AvatarImage src={auth.user?.picture} />
                <AvatarFallback className="bg-indigo-500 text-white">
                  {auth.user?.name?.charAt(0) || "U"}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{auth.user?.name}</p>
                <p className={`text-xs px-2 py-0.5 rounded-full border inline-block mt-1 ${getPlanBadgeColor(auth.user?.role)}`}>
                  {auth.user?.role?.charAt(0).toUpperCase() + auth.user?.role?.slice(1) || "Starter"}
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 lg:ml-64">
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-[#030305]/80 backdrop-blur-xl border-b border-white/5 px-4 lg:px-8 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 text-white/70 hover:text-white"
            data-testid="mobile-menu-btn"
          >
            <Menu className="w-6 h-6" />
          </button>

          <div className="hidden lg:block">
            <h1 className="font-display text-lg font-semibold text-white">
              {navItems.find(item => item.path === location.pathname)?.label || "Dashboard"}
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {/* AI Usage indicator */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-sm text-white/70">
                {auth.user?.ai_usage_current || 0}/{auth.user?.ai_usage_limit || 10} AI uses
              </span>
            </div>

            {/* Notifications */}
            <button className="p-2 text-white/70 hover:text-white relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-500 rounded-full"></span>
            </button>

            {/* User dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 p-1 rounded-full hover:bg-white/5 transition-colors" data-testid="user-menu-btn">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={auth.user?.picture} />
                    <AvatarFallback className="bg-indigo-500 text-white text-sm">
                      {auth.user?.name?.charAt(0) || "U"}
                    </AvatarFallback>
                  </Avatar>
                  <ChevronDown className="w-4 h-4 text-white/50 hidden sm:block" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 bg-[#0F0F11] border-white/10">
                <div className="px-3 py-2">
                  <p className="text-sm font-medium text-white">{auth.user?.name}</p>
                  <p className="text-xs text-white/50">{auth.user?.email}</p>
                </div>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem asChild>
                  <Link to="/settings" className="flex items-center gap-2 text-white/70 hover:text-white cursor-pointer">
                    <Settings className="w-4 h-4" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/billing" className="flex items-center gap-2 text-white/70 hover:text-white cursor-pointer">
                    <CreditCard className="w-4 h-4" />
                    Billing
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem 
                  onClick={handleLogout}
                  className="flex items-center gap-2 text-red-400 hover:text-red-300 cursor-pointer"
                  data-testid="logout-btn"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
