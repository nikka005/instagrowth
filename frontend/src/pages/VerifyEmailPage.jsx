import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { CheckCircle, XCircle, Loader2, Instagram } from "lucide-react";
import { Button } from "../components/ui/button";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const VerifyEmailPage = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState("loading"); // loading, success, error
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      verifyEmail(token);
    } else {
      setStatus("error");
      setMessage("Invalid verification link");
    }
  }, [searchParams]);

  const verifyEmail = async (token) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/verify-email?token=${token}`, {
        method: "POST",
      });

      if (response.ok) {
        setStatus("success");
        setMessage("Your email has been verified successfully!");
      } else {
        const error = await response.json();
        setStatus("error");
        setMessage(error.detail || "Verification failed");
      }
    } catch (error) {
      setStatus("error");
      setMessage("Something went wrong. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-[#030305] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full text-center"
      >
        <Link to="/" className="inline-flex items-center gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Instagram className="w-6 h-6 text-white" />
          </div>
          <span className="font-display font-bold text-xl text-white">InstaGrowth OS</span>
        </Link>

        <div className="p-8 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
          {status === "loading" && (
            <>
              <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mx-auto mb-4" />
              <h2 className="font-display text-2xl font-bold text-white mb-2">Verifying Email</h2>
              <p className="text-white/60">Please wait...</p>
            </>
          )}

          {status === "success" && (
            <>
              <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-10 h-10 text-green-400" />
              </div>
              <h2 className="font-display text-2xl font-bold text-white mb-2">Email Verified!</h2>
              <p className="text-white/60 mb-6">{message}</p>
              <Link to="/dashboard">
                <Button className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium">
                  Go to Dashboard
                </Button>
              </Link>
            </>
          )}

          {status === "error" && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
                <XCircle className="w-10 h-10 text-red-400" />
              </div>
              <h2 className="font-display text-2xl font-bold text-white mb-2">Verification Failed</h2>
              <p className="text-white/60 mb-6">{message}</p>
              <Link to="/login">
                <Button className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium">
                  Back to Login
                </Button>
              </Link>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default VerifyEmailPage;
