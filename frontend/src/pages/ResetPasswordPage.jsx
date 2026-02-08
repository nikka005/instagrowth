import { useState } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Instagram, Lock, ArrowRight, Loader2, CheckCircle } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const token = searchParams.get("token");

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast.error("Passwords don't match");
      return;
    }

    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });

      if (response.ok) {
        setSuccess(true);
        toast.success("Password reset successfully!");
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to reset password");
      }
    } catch (error) {
      toast.error("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-[#030305] flex items-center justify-center p-6">
        <div className="text-center">
          <h2 className="font-display text-2xl font-bold text-white mb-4">Invalid Reset Link</h2>
          <Link to="/forgot-password">
            <Button className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white">
              Request New Link
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#030305] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        <Link to="/" className="flex items-center gap-2 mb-8 justify-center">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Instagram className="w-6 h-6 text-white" />
          </div>
          <span className="font-display font-bold text-xl text-white">InstaGrowth OS</span>
        </Link>

        <div className="p-8 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
          {success ? (
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-10 h-10 text-green-400" />
              </div>
              <h2 className="font-display text-2xl font-bold text-white mb-2">Password Reset!</h2>
              <p className="text-white/60 mb-6">Your password has been successfully updated.</p>
              <Link to="/login">
                <Button className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium">
                  Sign In
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <h2 className="font-display text-2xl font-bold text-white mb-2 text-center">Create New Password</h2>
              <p className="text-white/60 mb-6 text-center">Enter your new password below</p>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <Label className="text-white/70 mb-2 block">New Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                    <Input
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="h-12 pl-12 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                      required
                      minLength={6}
                      data-testid="reset-password-input"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-white/70 mb-2 block">Confirm Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                    <Input
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="h-12 pl-12 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                      required
                      data-testid="reset-confirm-input"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl"
                  data-testid="reset-submit-btn"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      Reset Password
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </Button>
              </form>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default ResetPasswordPage;
