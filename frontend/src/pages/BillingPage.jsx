import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  CreditCard, Check, Zap, Crown, Rocket, Building2,
  Loader2, ExternalLink
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const BillingPage = ({ auth }) => {
  const [searchParams] = useSearchParams();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingPlan, setProcessingPlan] = useState(null);

  useEffect(() => {
    fetchPlans();
    checkPaymentStatus();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_URL}/api/plans`, {
        credentials: "include",
      });
      const text = await response.text();
      if (response.ok && text) {
        try {
          const data = JSON.parse(text);
          setPlans(data);
        } catch {
          console.error("Failed to parse plans response");
        }
      }
    } catch (error) {
      console.error("Failed to fetch plans:", error);
    } finally {
      setLoading(false);
    }
  };

  const checkPaymentStatus = async () => {
    const sessionId = searchParams.get("session_id");
    if (!sessionId) return;

    // Poll for payment status
    const pollStatus = async (attempts = 0) => {
      if (attempts >= 5) {
        toast.error("Payment verification timed out");
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/checkout/status/${sessionId}`, {
          credentials: "include",
        });
        
        const text = await response.text();
        let data;
        try {
          data = JSON.parse(text);
        } catch {
          setTimeout(() => pollStatus(attempts + 1), 2000);
          return;
        }
        
        if (response.ok) {
          if (data.payment_status === "paid") {
            toast.success("Payment successful! Your plan has been upgraded.");
            await auth.checkAuth();
            window.history.replaceState(null, "", "/billing");
            return;
          } else if (data.status === "expired") {
            toast.error("Payment session expired");
            return;
          }
        }
        
        setTimeout(() => pollStatus(attempts + 1), 2000);
      } catch (error) {
        console.error("Error checking payment status:", error);
      }
    };

    pollStatus();
  };

  const handleUpgrade = async (planId) => {
    setProcessingPlan(planId);
    try {
      const response = await fetch(`${API_URL}/api/checkout/session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          plan_id: planId,
          origin_url: window.location.origin,
        }),
      });

      const text = await response.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error('Server returned invalid response');
      }

      if (!response.ok) {
        throw new Error(data.detail || "Failed to create checkout session");
      }

      window.location.href = data.url;
    } catch (error) {
      toast.error(error.message);
      setProcessingPlan(null);
    }
  };

  const getPlanIcon = (planId) => {
    switch (planId) {
      case "starter": return <Zap className="w-6 h-6" />;
      case "pro": return <Crown className="w-6 h-6" />;
      case "agency": return <Rocket className="w-6 h-6" />;
      case "enterprise": return <Building2 className="w-6 h-6" />;
      default: return <CreditCard className="w-6 h-6" />;
    }
  };

  const getPlanColor = (planId) => {
    switch (planId) {
      case "starter": return "from-gray-500 to-gray-600";
      case "pro": return "from-indigo-500 to-purple-500";
      case "agency": return "from-purple-500 to-pink-500";
      case "enterprise": return "from-teal-500 to-cyan-500";
      default: return "from-gray-500 to-gray-600";
    }
  };

  const isCurrentPlan = (planId) => auth.user?.role === planId;

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Billing & Plans</h1>
          <p className="text-white/60 mt-1">Manage your subscription and upgrade your plan</p>
        </div>

        {/* Current Plan */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${getPlanColor(auth.user?.role)} flex items-center justify-center text-white`}>
                {getPlanIcon(auth.user?.role)}
              </div>
              <div>
                <p className="text-sm text-white/50">Current Plan</p>
                <h2 className="font-display text-2xl font-bold text-white capitalize">
                  {auth.user?.role || "Starter"}
                </h2>
              </div>
            </div>
            <div className="flex flex-col md:items-end gap-1">
              <p className="text-sm text-white/50">
                {auth.user?.account_limit || 1} account{(auth.user?.account_limit || 1) > 1 ? 's' : ''} • 
                {auth.user?.ai_usage_limit || 10} AI generations/month
              </p>
              <p className="text-sm text-white/50">
                AI Usage: {auth.user?.ai_usage_current || 0} / {auth.user?.ai_usage_limit || 10}
              </p>
            </div>
          </div>
        </div>

        {/* Plans Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.plan_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative p-6 rounded-2xl border transition-all ${
                  plan.plan_id === "pro"
                    ? 'bg-indigo-500/10 border-indigo-500/30'
                    : 'bg-[#0F0F11]/80 border-white/5 hover:border-white/10'
                }`}
              >
                {plan.plan_id === "pro" && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white border-0">
                    Most Popular
                  </Badge>
                )}

                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getPlanColor(plan.plan_id)} flex items-center justify-center text-white mb-4`}>
                  {getPlanIcon(plan.plan_id)}
                </div>

                <h3 className="font-display text-xl font-semibold text-white mb-1">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-3xl font-display font-bold text-white">${plan.price}</span>
                  <span className="text-white/50">/month</span>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features?.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                      <Check className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                      {feature}
                    </li>
                  ))}
                </ul>

                {isCurrentPlan(plan.plan_id) ? (
                  <Button
                    disabled
                    className="w-full h-11 rounded-xl bg-white/5 border border-white/10 text-white/50"
                  >
                    Current Plan
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleUpgrade(plan.plan_id)}
                    disabled={processingPlan === plan.plan_id}
                    className={`w-full h-11 rounded-xl font-medium transition-all ${
                      plan.plan_id === "pro"
                        ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_20px_rgba(99,102,241,0.3)]'
                        : 'bg-white/5 hover:bg-white/10 border border-white/10 text-white'
                    }`}
                    data-testid={`upgrade-${plan.plan_id}-btn`}
                  >
                    {processingPlan === plan.plan_id ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        Upgrade
                        <ExternalLink className="w-4 h-4 ml-2" />
                      </>
                    )}
                  </Button>
                )}
              </motion.div>
            ))}
          </div>
        )}

        {/* FAQ */}
        <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
          <h3 className="font-display text-lg font-semibold text-white mb-4">Frequently Asked Questions</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-white mb-1">Can I change plans anytime?</h4>
              <p className="text-sm text-white/60">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-1">What happens to my data if I downgrade?</h4>
              <p className="text-sm text-white/60">Your data is preserved, but you may lose access to features not included in your new plan.</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-1">Do you offer refunds?</h4>
              <p className="text-sm text-white/60">We offer a 7-day money-back guarantee for all plans. Contact support for assistance.</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default BillingPage;
