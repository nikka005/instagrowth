import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
const AuthCallback = ({ auth }) => {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      // Extract session_id from URL hash
      const hash = window.location.hash;
      const params = new URLSearchParams(hash.slice(1));
      const sessionId = params.get("session_id");

      if (!sessionId) {
        toast.error("Authentication failed - no session ID");
        navigate("/login");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/auth/session`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Session-ID": sessionId,
          },
          credentials: "include",
        });

        if (!response.ok) {
          throw new Error("Session validation failed");
        }

        const data = await response.json();
        auth.setUser(data.user);
        toast.success("Welcome back!");
        
        // Clear the hash and navigate to dashboard
        window.history.replaceState(null, "", window.location.pathname);
        navigate("/dashboard", { state: { user: data.user } });
      } catch (error) {
        console.error("Auth callback error:", error);
        toast.error("Authentication failed");
        navigate("/login");
      }
    };

    processAuth();
  }, []);

  return (
    <div className="min-h-screen bg-[#030305] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-white/60">Completing authentication...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
