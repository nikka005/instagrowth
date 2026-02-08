import React, { useState, useEffect } from 'react';
import { 
  Gift, Users, DollarSign, TrendingUp, CheckCircle2, 
  Clock, RefreshCw, Loader2, Search
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminReferralsPage = () => {
  const [overview, setOverview] = useState(null);
  const [payouts, setPayouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [payoutFilter, setPayoutFilter] = useState('pending');
  const [processingPayout, setProcessingPayout] = useState(null);

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [overviewRes, payoutsRes] = await Promise.all([
        fetch(`${API_URL}/api/referrals/admin/overview`, { headers }),
        fetch(`${API_URL}/api/referrals/admin/payouts?status=${payoutFilter}`, { headers })
      ]);

      if (overviewRes.ok) setOverview(await overviewRes.json());
      if (payoutsRes.ok) {
        const data = await payoutsRes.json();
        setPayouts(data.payouts);
      }
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const processPayout = async (payoutId, status) => {
    setProcessingPayout(payoutId);
    try {
      const response = await fetch(
        `${API_URL}/api/referrals/admin/payouts/${payoutId}?status=${status}`,
        { method: 'PUT', headers }
      );
      
      if (response.ok) {
        toast.success(`Payout ${status}`);
        fetchData();
      }
    } catch (error) {
      toast.error('Failed to process payout');
    } finally {
      setProcessingPayout(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Referral Program</h1>
          <p className="text-white/50 mt-1">Manage affiliate referrals and payouts</p>
        </div>
        <button
          onClick={fetchData}
          className="p-2 text-white/60 hover:text-white hover:bg-white/5 rounded-lg"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-5 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/20 rounded-xl">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-5 h-5 text-indigo-400" />
            <span className="text-white/60 text-sm">Total Referrals</span>
          </div>
          <p className="text-3xl font-bold text-white">{overview?.total_referrals || 0}</p>
        </div>
        <div className="p-5 bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/20 rounded-xl">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <span className="text-white/60 text-sm">Conversions</span>
          </div>
          <p className="text-3xl font-bold text-white">{overview?.converted || 0}</p>
          <p className="text-green-400 text-sm">{overview?.conversion_rate}% rate</p>
        </div>
        <div className="p-5 bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/20 rounded-xl">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="w-5 h-5 text-yellow-400" />
            <span className="text-white/60 text-sm">Total Paid Out</span>
          </div>
          <p className="text-3xl font-bold text-white">${overview?.total_earnings_paid?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="p-5 bg-gradient-to-br from-red-500/20 to-pink-500/20 border border-red-500/20 rounded-xl">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-red-400" />
            <span className="text-white/60 text-sm">Pending Payouts</span>
          </div>
          <p className="text-3xl font-bold text-white">{overview?.pending_payouts || 0}</p>
        </div>
      </div>

      {/* Configuration */}
      <div className="p-5 bg-[#1e293b] border border-white/10 rounded-xl">
        <h3 className="font-semibold text-white mb-4">Program Configuration</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="p-3 bg-white/5 rounded-lg">
            <p className="text-white/50 text-sm">Referrer Credits</p>
            <p className="text-xl font-bold text-indigo-400">{overview?.config?.referrer_reward_credits}</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg">
            <p className="text-white/50 text-sm">Referee Credits</p>
            <p className="text-xl font-bold text-purple-400">{overview?.config?.referee_reward_credits}</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg">
            <p className="text-white/50 text-sm">Commission</p>
            <p className="text-xl font-bold text-green-400">{overview?.config?.commission_percentage}%</p>
          </div>
          <div className="p-3 bg-white/5 rounded-lg">
            <p className="text-white/50 text-sm">Min Payout</p>
            <p className="text-xl font-bold text-yellow-400">${overview?.config?.min_payout_amount}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Top Referrers */}
        <div className="p-5 bg-[#1e293b] border border-white/10 rounded-xl">
          <h3 className="font-semibold text-white mb-4">Top Referrers</h3>
          <div className="space-y-2">
            {overview?.top_referrers?.length > 0 ? (
              overview.top_referrers.map((referrer, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-white/5 rounded-lg flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 text-sm font-bold">
                      {idx + 1}
                    </span>
                    <div>
                      <p className="text-white text-sm">{referrer.code}</p>
                      <p className="text-white/40 text-xs">{referrer.signups} signups</p>
                    </div>
                  </div>
                  <span className="text-green-400 font-medium">
                    ${referrer.total_earnings?.toFixed(2)}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-white/40 text-center py-8">No referrers yet</p>
            )}
          </div>
        </div>

        {/* Payout Requests */}
        <div className="p-5 bg-[#1e293b] border border-white/10 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">Payout Requests</h3>
            <select
              value={payoutFilter}
              onChange={(e) => {
                setPayoutFilter(e.target.value);
                fetchData();
              }}
              className="px-3 py-1 bg-white/5 border border-white/10 rounded text-white text-sm"
            >
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="paid">Paid</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {payouts.length > 0 ? (
              payouts.map((payout) => (
                <div
                  key={payout.payout_id}
                  className="p-3 bg-white/5 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white/40 text-xs">{payout.payout_id}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      payout.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                      payout.status === 'paid' ? 'bg-green-500/20 text-green-400' :
                      payout.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {payout.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white font-medium">${payout.amount.toFixed(2)}</span>
                    {payout.status === 'pending' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => processPayout(payout.payout_id, 'paid')}
                          disabled={processingPayout === payout.payout_id}
                          className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs hover:bg-green-500/30"
                        >
                          {processingPayout === payout.payout_id ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : 'Pay'}
                        </button>
                        <button
                          onClick={() => processPayout(payout.payout_id, 'rejected')}
                          disabled={processingPayout === payout.payout_id}
                          className="px-3 py-1 bg-red-500/20 text-red-400 rounded text-xs hover:bg-red-500/30"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </div>
                  <p className="text-white/30 text-xs mt-1">
                    {new Date(payout.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-white/40 text-center py-8">No {payoutFilter} payouts</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminReferralsPage;
