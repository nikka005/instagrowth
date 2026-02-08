import { useEffect, useState, useRef } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, Link } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";

// Import pages
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import AuthCallback from "./pages/AuthCallback";
import DashboardPage from "./pages/DashboardPage";
import AccountsPage from "./pages/AccountsPage";
import AuditPage from "./pages/AuditPage";
import ContentPage from "./pages/ContentPage";
import GrowthPlannerPage from "./pages/GrowthPlannerPage";
import BillingPage from "./pages/BillingPage";
import SettingsPage from "./pages/SettingsPage";
import AdminPage from "./pages/AdminPage";
import AdminLoginPage from "./pages/AdminLoginPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import TeamPage from "./pages/TeamPage";
import DMTemplatesPage from "./pages/DMTemplatesPage";
import CompetitorAnalysisPage from "./pages/CompetitorAnalysisPage";
import ABTestingPage from "./pages/ABTestingPage";

// Admin Panel imports
import AdminPanelLayout from "./components/AdminPanelLayout";
import AdminPanelLoginPage from "./pages/admin-panel/LoginPage";
import AdminDashboardPage from "./pages/admin-panel/DashboardPage";
import AdminUsersPage from "./pages/admin-panel/UsersPage";
import AdminPlansPage from "./pages/admin-panel/PlansPage";
import AdminRevenuePage from "./pages/admin-panel/RevenuePage";
import AdminAIUsagePage from "./pages/admin-panel/AIUsagePage";
import AdminLogsPage from "./pages/admin-panel/LogsPage";
import AdminSystemSettingsPage from "./pages/admin-panel/SystemSettingsPage";
import AdminDocumentationPage from "./pages/admin-panel/DocumentationPage";
import AdminTicketsPage from "./pages/admin-panel/TicketsPage";

// Legal Pages
import PrivacyPolicyPage from "./pages/PrivacyPolicyPage";
import TermsOfServicePage from "./pages/TermsOfServicePage";
import RefundPolicyPage from "./pages/RefundPolicyPage";
import DataDeletionPage from "./pages/DataDeletionPage";

// Support & Onboarding
import SupportPage from "./pages/SupportPage";
import OnboardingPage from "./pages/OnboardingPage";

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Auth Context
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password, totpCode = null) => {
    const url = totpCode 
      ? `${API_URL}/api/auth/login?totp_code=${totpCode}`
      : `${API_URL}/api/auth/login`;
    
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || "Login failed");
    }
    
    // Check if 2FA is required
    if (data.requires_2fa) {
      return data;
    }
    
    localStorage.setItem("token", data.token);
    setUser(data.user);
    return data;
  };

  const register = async (name, email, password) => {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name, email, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Registration failed");
    }
    
    const data = await response.json();
    localStorage.setItem("token", data.token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    try {
      await fetch(`${API_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    }
    localStorage.removeItem("token");
    setUser(null);
  };

  const googleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return { user, setUser, loading, login, register, logout, googleLogin, checkAuth };
};

// Protected Route Component
const ProtectedRoute = ({ children, auth }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(location.state?.user ? true : null);

  useEffect(() => {
    if (location.state?.user) {
      auth.setUser(location.state.user);
      setIsAuthenticated(true);
      return;
    }

    const checkAuth = async () => {
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          credentials: "include",
        });
        if (!response.ok) throw new Error("Not authenticated");
        const user = await response.json();
        auth.setUser(user);
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
        navigate("/login");
      }
    };
    checkAuth();
  }, []);

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-[#030305] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-white/60">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return children;
};

// App Router Component
function AppRouter({ auth }) {
  const location = useLocation();

  // Check URL fragment for session_id (Google OAuth callback)
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback auth={auth} />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage auth={auth} />} />
      <Route path="/register" element={<RegisterPage auth={auth} />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/admin-login" element={<AdminLoginPage />} />
      
      {/* Legal Pages */}
      <Route path="/privacy" element={<PrivacyPolicyPage />} />
      <Route path="/terms" element={<TermsOfServicePage />} />
      <Route path="/refund" element={<RefundPolicyPage />} />
      <Route path="/data-deletion" element={<DataDeletionPage />} />
      
      {/* Onboarding */}
      <Route path="/onboarding" element={
        <ProtectedRoute auth={auth}>
          <OnboardingPage auth={auth} />
        </ProtectedRoute>
      } />
      
      {/* Support */}
      <Route path="/support" element={
        <ProtectedRoute auth={auth}>
          <SupportPage auth={auth} />
        </ProtectedRoute>
      } />
      
      <Route path="/accept-invite" element={
        <ProtectedRoute auth={auth}>
          <TeamPage auth={auth} />
        </ProtectedRoute>
      } />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute auth={auth}>
            <DashboardPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/accounts"
        element={
          <ProtectedRoute auth={auth}>
            <AccountsPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit"
        element={
          <ProtectedRoute auth={auth}>
            <AuditPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/content"
        element={
          <ProtectedRoute auth={auth}>
            <ContentPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/planner"
        element={
          <ProtectedRoute auth={auth}>
            <GrowthPlannerPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/billing"
        element={
          <ProtectedRoute auth={auth}>
            <BillingPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute auth={auth}>
            <SettingsPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/team"
        element={
          <ProtectedRoute auth={auth}>
            <TeamPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dm-templates"
        element={
          <ProtectedRoute auth={auth}>
            <DMTemplatesPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/competitors"
        element={
          <ProtectedRoute auth={auth}>
            <CompetitorAnalysisPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/ab-testing"
        element={
          <ProtectedRoute auth={auth}>
            <ABTestingPage auth={auth} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={<AdminPage auth={auth} />}
      />
      
      {/* Admin Panel Routes */}
      <Route path="/admin-panel/login" element={<AdminPanelLoginPage />} />
      <Route path="/admin-panel" element={<AdminPanelLayout><AdminDashboardPage /></AdminPanelLayout>} />
      <Route path="/admin-panel/users" element={<AdminPanelLayout><AdminUsersPage /></AdminPanelLayout>} />
      <Route path="/admin-panel/plans" element={<AdminPanelLayout><AdminPlansPage /></AdminPanelLayout>} />
      <Route path="/admin-panel/revenue" element={<AdminPanelLayout><AdminRevenuePage /></AdminPanelLayout>} />
      <Route path="/admin-panel/ai-usage" element={<AdminPanelLayout><AdminAIUsagePage /></AdminPanelLayout>} />
      <Route path="/admin-panel/logs" element={<AdminPanelLayout><AdminLogsPage /></AdminPanelLayout>} />
      <Route path="/admin-panel/settings" element={<AdminPanelLayout><AdminSystemSettingsPage /></AdminPanelLayout>} />
      <Route path="/admin-panel/docs" element={<AdminPanelLayout><AdminDocumentationPage /></AdminPanelLayout>} />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  const auth = useAuth();

  return (
    <div className="dark">
      <BrowserRouter>
        <AppRouter auth={auth} />
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </div>
  );
}

export default App;
