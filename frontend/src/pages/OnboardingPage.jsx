import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Instagram, Users, Target, TrendingUp, Sparkles, 
  ArrowRight, ArrowLeft, CheckCircle2, Loader2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const goals = [
  {
    id: "followers",
    icon: Users,
    title: "Grow Followers",
    description: "Increase your follower count organically",
    color: "from-pink-500 to-rose-500"
  },
  {
    id: "leads",
    icon: Target,
    title: "Generate Leads",
    description: "Convert followers into customers",
    color: "from-blue-500 to-cyan-500"
  },
  {
    id: "brand",
    icon: Sparkles,
    title: "Build Brand",
    description: "Establish a strong brand presence",
    color: "from-purple-500 to-indigo-500"
  },
  {
    id: "engagement",
    icon: TrendingUp,
    title: "Boost Engagement",
    description: "Increase likes, comments, and shares",
    color: "from-orange-500 to-amber-500"
  }
];

const OnboardingPage = ({ auth, onComplete }) => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [connecting, setConnecting] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [auditResult, setAuditResult] = useState(null);

  const totalSteps = 4;

  const handleConnectInstagram = async () => {
    setConnecting(true);
    try {
      const response = await fetch(`${API_URL}/api/instagram/auth/url`, {
        credentials: "include"
      });
      
      if (!response.ok) {
        // If Instagram API not configured, skip to manual
        toast.info("Instagram API not configured. You can add accounts manually.");
        setStep(4);
        return;
      }
      
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      toast.info("You can connect Instagram later from your dashboard");
      setStep(4);
    } finally {
      setConnecting(false);
    }
  };

  const handleSkipInstagram = () => {
    setStep(4);
  };

  const handleGenerateAudit = async () => {
    setGenerating(true);
    try {
      // Get first account
      const accountsRes = await fetch(`${API_URL}/api/accounts`, { credentials: "include" });
      const accounts = await accountsRes.json();
      
      if (accounts.length > 0) {
        // Generate audit for first account
        const auditRes = await fetch(
          `${API_URL}/api/audits?account_id=${accounts[0].account_id}`,
          { method: "POST", credentials: "include" }
        );
        
        if (auditRes.ok) {
          const audit = await auditRes.json();
          setAuditResult(audit);
        }
      }
    } catch (error) {
      console.error("Audit generation failed:", error);
    } finally {
      setGenerating(false);
    }
  };

  const completeOnboarding = async () => {
    try {
      // Save onboarding completion
      await fetch(`${API_URL}/api/auth/complete-onboarding?goal=${selectedGoal}`, {
        method: "POST",
        credentials: "include"
      });
    } catch (error) {
      // Continue anyway
    }
    
    if (onComplete) {
      onComplete();
    } else {
      navigate("/dashboard");
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Instagram className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-3">
              Welcome to InstaGrowth OS! 🎉
            </h2>
            <p className="text-white/60 text-lg mb-8 max-w-md mx-auto">
              Let's set up your account in just a few steps. This will help us personalize your experience.
            </p>
            <Button
              onClick={() => setStep(2)}
              className="h-12 px-8 rounded-full bg-indigo-600 hover:bg-indigo-500 text-lg"
            >
              Get Started
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <h2 className="text-2xl font-bold text-white mb-2 text-center">
              What's your main goal?
            </h2>
            <p className="text-white/60 text-center mb-8">
              This helps us tailor recommendations for you
            </p>
            
            <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto">
              {goals.map((goal) => {
                const Icon = goal.icon;
                return (
                  <button
                    key={goal.id}
                    onClick={() => setSelectedGoal(goal.id)}
                    className={`p-6 rounded-2xl border-2 transition-all text-left ${
                      selectedGoal === goal.id
                        ? "border-indigo-500 bg-indigo-500/10"
                        : "border-white/10 bg-white/5 hover:border-white/20"
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${goal.color} flex items-center justify-center mb-4`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="font-semibold text-white mb-1">{goal.title}</h3>
                    <p className="text-white/50 text-sm">{goal.description}</p>
                    {selectedGoal === goal.id && (
                      <CheckCircle2 className="w-5 h-5 text-indigo-400 absolute top-4 right-4" />
                    )}
                  </button>
                );
              })}
            </div>

            <div className="flex justify-center gap-3 mt-8">
              <Button
                onClick={() => setStep(1)}
                variant="outline"
                className="bg-white/5 border-white/10 text-white"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <Button
                onClick={() => setStep(3)}
                disabled={!selectedGoal}
                className="bg-indigo-600 hover:bg-indigo-500"
              >
                Continue
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center">
              <Instagram className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">
              Connect Your Instagram
            </h2>
            <p className="text-white/60 mb-8 max-w-md mx-auto">
              Connect your Instagram Business account to unlock real analytics and AI-powered insights.
            </p>
            
            <div className="flex flex-col gap-3 max-w-sm mx-auto">
              <Button
                onClick={handleConnectInstagram}
                disabled={connecting}
                className="h-12 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600"
              >
                {connecting ? (
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                ) : (
                  <Instagram className="w-5 h-5 mr-2" />
                )}
                Connect Instagram
              </Button>
              <Button
                onClick={handleSkipInstagram}
                variant="ghost"
                className="text-white/50 hover:text-white"
              >
                Skip for now
              </Button>
            </div>

            <Button
              onClick={() => setStep(2)}
              variant="ghost"
              className="mt-6 text-white/50"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </motion.div>
        );

      case 4:
        return (
          <motion.div
            key="step4"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">
              You're All Set! 🚀
            </h2>
            <p className="text-white/60 mb-8 max-w-md mx-auto">
              Your account is ready. Start exploring AI-powered audits, content generation, and growth planning.
            </p>

            <div className="bg-white/5 rounded-2xl p-6 max-w-md mx-auto mb-8 text-left">
              <h3 className="font-semibold text-white mb-4">Quick Start Guide:</h3>
              <ul className="space-y-3 text-white/70">
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-sm flex-shrink-0">1</span>
                  <span>Add your Instagram account (if not connected)</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-sm flex-shrink-0">2</span>
                  <span>Generate your first AI audit to get insights</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-sm flex-shrink-0">3</span>
                  <span>Create content using AI-powered suggestions</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-sm flex-shrink-0">4</span>
                  <span>Build a growth plan tailored to your goals</span>
                </li>
              </ul>
            </div>
            
            <Button
              onClick={completeOnboarding}
              className="h-12 px-8 rounded-full bg-indigo-600 hover:bg-indigo-500 text-lg"
            >
              Go to Dashboard
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#030305] flex items-center justify-center p-6">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-3xl">
        {/* Progress */}
        <div className="flex justify-center gap-2 mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={`h-2 rounded-full transition-all ${
                s <= step ? "w-12 bg-indigo-500" : "w-8 bg-white/10"
              }`}
            />
          ))}
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {renderStep()}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default OnboardingPage;
