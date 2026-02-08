import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Gift, Copy, Users, DollarSign, TrendingUp, 
  CheckCircle2, Loader2, ExternalLink, Wallet
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Progress } from "../components/ui/progress";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ReferralsPage = ({ auth }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requestingPayout, setRequestingPayout] = useState(false);

  useEffect(() => {
    fetchReferralStats();
  }, []);

  const fetchReferralStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/referrals/stats`, {
        credentials: "include"
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      toast.error("Failed to load referral data");
    } finally {
      setLoading(false);
    }
  };

  const copyReferralLink = () => {
    const link = `${window.location.origin}/register?ref=${stats?.code}`;
    navigator.clipboard.writeText(link);
    toast.success("Referral link copied!");
  };

  const requestPayout = async () => {
    setRequestingPayout(true);
    try {
      const response = await fetch(`${API_URL}/api/referrals/request-payout`, {
        method: "POST",
        credentials: "include"
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }
      
      const data = await response.json();
      toast.success(`Payout of $${data.amount} requested!`);
      fetchReferralStats();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setRequestingPayout(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout auth={auth}>
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-white">
            Referral Program
          </h1>
          <p className="text-white/60 mt-1">
            Earn credits and cash by referring friends to InstaGrowth OS
          </p>
        </div>

        {/* Referral Link Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 via-purple-600/20 to-pink-600/20 border border-indigo-500/20"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 rounded-2xl bg-indigo-500/20 flex items-center justify-center">
              <Gift className="w-7 h-7 text-indigo-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-white">Your Referral Link</h2>
              <p className="text-white/50">Share this link to earn rewards</p>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Input
                value={`${window.location.origin}/register?ref=${stats?.code || ''}`}
                readOnly
                className="bg-white/5 border-white/10 text-white pr-10"
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 text-xs">
                {stats?.code}
              </span>
            </div>
            <Button
              onClick={copyReferralLink}
              className="bg-indigo-600 hover:bg-indigo-500 px-6"
              data-testid="copy-referral-link"
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy
            </Button>
          </div>

          {/* Rewards Info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-white/10">
            <div className="text-center">
              <p className="text-2xl font-bold text-indigo-400">
                {stats?.rewards?.referrer_reward_credits || 50}
              </p>
              <p className="text-white/50 text-sm">Credits for you</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-400">
                {stats?.rewards?.referee_reward_credits || 25}
              </p>
              <p className="text-white/50 text-sm">Credits for friend</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-pink-400">
                {stats?.rewards?.commission_percentage || 20}%
              </p>
              <p className="text-white/50 text-sm">Commission</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400">
                ${stats?.rewards?.min_payout_amount || 50}
              </p>
              <p className="text-white/50 text-sm">Min payout</p>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { 
              label: "Link Clicks", 
              value: stats?.overview?.clicks || 0, 
              icon: <ExternalLink className="w-5 h-5" />,
              color: "text-blue-400",
              bg: "bg-blue-500/10"
            },
            { 
              label: "Sign Ups", 
              value: stats?.overview?.signups || 0, 
              icon: <Users className="w-5 h-5" />,
              color: "text-green-400",
              bg: "bg-green-500/10"
            },
            { 
              label: "Conversions", 
              value: stats?.overview?.conversions || 0, 
              icon: <CheckCircle2 className="w-5 h-5" />,
              color: "text-purple-400",
              bg: "bg-purple-500/10"
            },
            { 
              label: "Conversion Rate", 
              value: `${stats?.overview?.conversion_rate || 0}%`, 
              icon: <TrendingUp className="w-5 h-5" />,
              color: "text-orange-400",
              bg: "bg-orange-500/10"
            },
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-5 rounded-xl bg-[#0F0F11]/80 border border-white/5"
            >
              <div className={`w-10 h-10 rounded-lg ${stat.bg} flex items-center justify-center mb-3`}>
                <span className={stat.color}>{stat.icon}</span>
              </div>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-white/50 text-sm">{stat.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Earnings Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Earnings Overview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="font-semibold text-white text-lg">Earnings</h3>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                <div>
                  <p className="text-white/50 text-sm">Total Earned</p>
                  <p className="text-2xl font-bold text-white">
                    ${stats?.earnings?.total?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <CheckCircle2 className="w-8 h-8 text-green-500/50" />
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                <div>
                  <p className="text-white/50 text-sm">Pending</p>
                  <p className="text-2xl font-bold text-yellow-400">
                    ${stats?.earnings?.pending?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <Wallet className="w-8 h-8 text-yellow-500/50" />
              </div>

              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                <div>
                  <p className="text-white/50 text-sm">Paid Out</p>
                  <p className="text-2xl font-bold text-indigo-400">
                    ${stats?.earnings?.paid_out?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-indigo-500/50" />
              </div>
            </div>

            <Button
              onClick={requestPayout}
              disabled={requestingPayout || (stats?.earnings?.pending || 0) < (stats?.rewards?.min_payout_amount || 50)}
              className="w-full mt-6 bg-green-600 hover:bg-green-500 disabled:opacity-50"
              data-testid="request-payout-btn"
            >
              {requestingPayout ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <DollarSign className="w-4 h-4 mr-2" />
              )}
              Request Payout
            </Button>
            {(stats?.earnings?.pending || 0) < (stats?.rewards?.min_payout_amount || 50) && (
              <p className="text-center text-white/40 text-xs mt-2">
                Minimum ${stats?.rewards?.min_payout_amount || 50} required for payout
              </p>
            )}
          </motion.div>

          {/* Recent Referrals */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
          >
            <h3 className="font-semibold text-white text-lg mb-6">Recent Referrals</h3>

            {stats?.recent_referrals?.length > 0 ? (
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {stats.recent_referrals.map((referral, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-white/5 flex items-center justify-between"
                  >
                    <div>
                      <p className="text-white font-medium">
                        {referral.referee_email?.replace(/(.{3})(.*)(@.*)/, '$1***$3')}
                      </p>
                      <p className="text-white/40 text-xs">
                        {new Date(referral.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        referral.status === 'converted' 
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {referral.status}
                      </span>
                      {referral.commission_earned > 0 && (
                        <p className="text-green-400 text-sm mt-1">
                          +${referral.commission_earned.toFixed(2)}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-10">
                <Users className="w-12 h-12 text-white/20 mx-auto mb-3" />
                <p className="text-white/50">No referrals yet</p>
                <p className="text-white/30 text-sm mt-1">Share your link to start earning!</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
        >
          <h3 className="font-semibold text-white text-lg mb-6">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                step: "1",
                title: "Share Your Link",
                description: "Copy your unique referral link and share it with friends, on social media, or your website."
              },
              {
                step: "2",
                title: "Friends Sign Up",
                description: "When someone signs up using your link, you both get bonus AI credits instantly."
              },
              {
                step: "3",
                title: "Earn Commission",
                description: `When they upgrade to a paid plan, you earn ${stats?.rewards?.commission_percentage || 20}% commission on their first payment.`
              }
            ].map((item, idx) => (
              <div key={idx} className="text-center">
                <div className="w-12 h-12 mx-auto rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-lg mb-4">
                  {item.step}
                </div>
                <h4 className="font-medium text-white mb-2">{item.title}</h4>
                <p className="text-white/50 text-sm">{item.description}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default ReferralsPage;
