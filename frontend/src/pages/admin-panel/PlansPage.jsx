import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X, Loader2, Check, Package } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PlansPage = ({ admin }) => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [formData, setFormData] = useState({
    name: '', price: '', billing_cycle: 'monthly', account_limit: '', ai_limit: '', team_limit: '0', white_label: false, features: ''
  });

  const token = localStorage.getItem('admin_panel_token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin-panel/plans`, { credentials: 'include', headers });
      if (response.ok) {
        const data = await response.json();
        setPlans(data.plans || []);
      }
    } catch (error) {
      toast.error('Failed to fetch plans');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingPlan(null);
    setFormData({ name: '', price: '', billing_cycle: 'monthly', account_limit: '', ai_limit: '', team_limit: '0', white_label: false, features: '' });
    setShowModal(true);
  };

  const openEditModal = (plan) => {
    setEditingPlan(plan);
    setFormData({
      name: plan.name,
      price: plan.price,
      billing_cycle: plan.billing_cycle,
      account_limit: plan.account_limit,
      ai_limit: plan.ai_limit,
      team_limit: plan.team_limit || 0,
      white_label: plan.white_label || false,
      features: plan.features?.join(', ') || ''
    });
    setShowModal(true);
  };

  const savePlan = async () => {
    try {
      const params = new URLSearchParams({
        name: formData.name,
        price: formData.price,
        billing_cycle: formData.billing_cycle,
        account_limit: formData.account_limit,
        ai_limit: formData.ai_limit,
        team_limit: formData.team_limit,
        white_label: formData.white_label,
        features: formData.features
      });

      const url = editingPlan 
        ? `${API_URL}/api/admin-panel/plans/${editingPlan.plan_id}?${params}`
        : `${API_URL}/api/admin-panel/plans?${params}`;

      const response = await fetch(url, {
        method: editingPlan ? 'PUT' : 'POST',
        credentials: 'include',
        headers
      });

      if (response.ok) {
        toast.success(editingPlan ? 'Plan updated' : 'Plan created');
        fetchPlans();
        setShowModal(false);
      } else {
        throw new Error('Failed to save plan');
      }
    } catch (error) {
      toast.error(error.message);
    }
  };

  const togglePlanStatus = async (planId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'disabled' : 'active';
      const response = await fetch(`${API_URL}/api/admin-panel/plans/${planId}?status=${newStatus}`, {
        method: 'PUT',
        credentials: 'include',
        headers
      });
      if (response.ok) {
        toast.success(`Plan ${newStatus}`);
        fetchPlans();
      }
    } catch (error) {
      toast.error('Failed to update plan');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Plans</h1>
          <p className="text-white/50 mt-1">Manage subscription plans and pricing</p>
        </div>
        <button onClick={openCreateModal} className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600">
          <Plus className="w-4 h-4" />
          Create Plan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans.map((plan) => (
          <div key={plan.plan_id} className={`bg-[#1e293b] rounded-xl border ${plan.status === 'active' ? 'border-white/10' : 'border-red-500/30'} p-6`}>
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg">
                <Package className="w-6 h-6 text-white" />
              </div>
              {plan.status !== 'active' && (
                <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded-full">Disabled</span>
              )}
            </div>

            <h3 className="text-lg font-semibold text-white">{plan.name}</h3>
            <div className="mt-2 mb-4">
              <span className="text-3xl font-bold text-white">${plan.price}</span>
              <span className="text-white/50">/{plan.billing_cycle}</span>
            </div>

            <div className="space-y-2 mb-6">
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">Accounts</span>
                <span className="text-white">{plan.account_limit}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">AI Credits</span>
                <span className="text-white">{plan.ai_limit}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">Team Members</span>
                <span className="text-white">{plan.team_limit || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">White Label</span>
                <span className="text-white">{plan.white_label ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-white/50">Subscribers</span>
                <span className="text-indigo-400 font-medium">{plan.subscribers || 0}</span>
              </div>
            </div>

            <div className="flex gap-2">
              <button onClick={() => openEditModal(plan)} className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-white/5 text-white rounded-lg hover:bg-white/10">
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button onClick={() => togglePlanStatus(plan.plan_id, plan.status)} className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg ${plan.status === 'active' ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'}`}>
                {plan.status === 'active' ? 'Disable' : 'Enable'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
          <div className="bg-[#1e293b] rounded-2xl w-full max-w-lg">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">{editingPlan ? 'Edit Plan' : 'Create Plan'}</h2>
                <button onClick={() => setShowModal(false)} className="text-white/50 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                  placeholder="Pro Plan"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-2">Price</label>
                  <input
                    type="number"
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                    placeholder="49"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-2">Billing Cycle</label>
                  <select
                    value={formData.billing_cycle}
                    onChange={(e) => setFormData({ ...formData, billing_cycle: e.target.value })}
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-2">Account Limit</label>
                  <input
                    type="number"
                    value={formData.account_limit}
                    onChange={(e) => setFormData({ ...formData, account_limit: e.target.value })}
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-2">AI Credits</label>
                  <input
                    type="number"
                    value={formData.ai_limit}
                    onChange={(e) => setFormData({ ...formData, ai_limit: e.target.value })}
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-white/70 mb-2">Team Members</label>
                  <input
                    type="number"
                    value={formData.team_limit}
                    onChange={(e) => setFormData({ ...formData, team_limit: e.target.value })}
                    className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.white_label}
                      onChange={(e) => setFormData({ ...formData, white_label: e.target.checked })}
                      className="w-5 h-5 rounded border-white/20 bg-white/5 text-indigo-500 focus:ring-indigo-500"
                    />
                    <span className="text-white">White Label</span>
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Features (comma separated)</label>
                <input
                  type="text"
                  value={formData.features}
                  onChange={(e) => setFormData({ ...formData, features: e.target.value })}
                  className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-white focus:border-indigo-500 focus:outline-none"
                  placeholder="Priority support, Custom reports"
                />
              </div>
            </div>
            <div className="p-6 border-t border-white/10 flex justify-end gap-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 text-white/70 hover:text-white">Cancel</button>
              <button onClick={savePlan} className="px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600">
                {editingPlan ? 'Save Changes' : 'Create Plan'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlansPage;
