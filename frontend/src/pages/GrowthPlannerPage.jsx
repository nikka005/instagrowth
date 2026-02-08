import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Calendar, Plus, Download, Loader2, CheckCircle2, 
  Circle, Clock, Target, Lightbulb
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const GrowthPlannerPage = ({ auth }) => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [duration, setDuration] = useState("7");
  const [generating, setGenerating] = useState(false);
  const [completedTasks, setCompletedTasks] = useState(new Set());

  useEffect(() => {
    fetchAccounts();
    fetchPlans();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchPlans(selectedAccount);
    }
  }, [selectedAccount]);

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/accounts`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
        if (data.length > 0) {
          setSelectedAccount(data[0].account_id);
        }
      }
    } catch (error) {
      console.error("Failed to fetch accounts:", error);
    }
  };

  const fetchPlans = async (accountId) => {
    try {
      const url = accountId 
        ? `${API_URL}/api/growth-plans?account_id=${accountId}`
        : `${API_URL}/api/growth-plans`;
      const response = await fetch(url, { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setPlans(data);
        if (data.length > 0) {
          setCurrentPlan(data[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch plans:", error);
    }
  };

  const generatePlan = async () => {
    if (!selectedAccount) {
      toast.error("Please select an account first");
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(`${API_URL}/api/growth-plans`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          account_id: selectedAccount,
          duration: parseInt(duration),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to generate plan");
      }

      const plan = await response.json();
      setCurrentPlan(plan);
      setPlans([plan, ...plans]);
      setCompletedTasks(new Set());
      toast.success(`${duration}-day growth plan created!`);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setGenerating(false);
    }
  };

  const downloadPDF = async (planId) => {
    try {
      const response = await fetch(`${API_URL}/api/growth-plans/${planId}/pdf`, {
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to download PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `growth_plan_${planId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const toggleTask = (taskIndex) => {
    const newCompleted = new Set(completedTasks);
    if (newCompleted.has(taskIndex)) {
      newCompleted.delete(taskIndex);
    } else {
      newCompleted.add(taskIndex);
    }
    setCompletedTasks(newCompleted);
  };

  const getTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case "post": return "bg-pink-500/20 text-pink-400 border-pink-500/30";
      case "engage": return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "analyze": return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "learn": return "bg-teal-500/20 text-teal-400 border-teal-500/30";
      default: return "bg-white/10 text-white/60 border-white/10";
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case "high": return "text-red-400";
      case "medium": return "text-yellow-400";
      case "low": return "text-green-400";
      default: return "text-white/50";
    }
  };

  const progress = currentPlan?.daily_tasks?.length 
    ? (completedTasks.size / currentPlan.daily_tasks.length) * 100 
    : 0;

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Growth Planner</h1>
            <p className="text-white/60 mt-1">AI-generated daily action plans for Instagram growth</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={selectedAccount} onValueChange={setSelectedAccount}>
              <SelectTrigger className="w-40 h-11 bg-white/5 border-white/10 rounded-xl text-white" data-testid="planner-account-select">
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent className="bg-[#0F0F11] border-white/10">
                {accounts.map((account) => (
                  <SelectItem key={account.account_id} value={account.account_id} className="text-white hover:bg-white/5">
                    @{account.username}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={duration} onValueChange={setDuration}>
              <SelectTrigger className="w-32 h-11 bg-white/5 border-white/10 rounded-xl text-white" data-testid="planner-duration-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#0F0F11] border-white/10">
                <SelectItem value="7" className="text-white hover:bg-white/5">7 Days</SelectItem>
                <SelectItem value="14" className="text-white hover:bg-white/5">14 Days</SelectItem>
                <SelectItem value="30" className="text-white hover:bg-white/5">30 Days</SelectItem>
              </SelectContent>
            </Select>
            <Button
              onClick={generatePlan}
              disabled={generating || !selectedAccount}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]"
              data-testid="generate-plan-btn"
            >
              {generating ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <Plus className="w-5 h-5 mr-2" />
              )}
              Create Plan
            </Button>
          </div>
        </div>

        {accounts.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No accounts yet</h3>
            <p className="text-white/50 mb-6">Add an Instagram account first to create growth plans</p>
            <Button
              onClick={() => window.location.href = "/accounts"}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              Add Account
            </Button>
          </div>
        ) : currentPlan ? (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Main Plan View */}
            <div className="lg:col-span-3 space-y-6">
              {/* Progress Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-display text-lg font-semibold text-white">
                      {currentPlan.duration}-Day Growth Plan
                    </h3>
                    <p className="text-sm text-white/50">
                      Created {new Date(currentPlan.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {auth.user?.role !== "starter" && (
                    <Button
                      onClick={() => downloadPDF(currentPlan.plan_id)}
                      variant="outline"
                      className="bg-white/5 border-white/10 text-white hover:bg-white/10"
                      data-testid="download-plan-pdf-btn"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export PDF
                    </Button>
                  )}
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-white/60">Progress</span>
                    <span className="text-white font-medium">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    />
                  </div>
                  <p className="text-xs text-white/40">
                    {completedTasks.size} of {currentPlan.daily_tasks?.length || 0} tasks completed
                  </p>
                </div>
              </div>

              {/* Daily Tasks */}
              <div className="space-y-3">
                {currentPlan.daily_tasks?.map((task, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.03 }}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      completedTasks.has(index)
                        ? 'bg-green-500/5 border-green-500/20'
                        : 'bg-[#0F0F11]/80 border-white/5 hover:border-indigo-500/30'
                    }`}
                    onClick={() => toggleTask(index)}
                  >
                    <div className="flex items-start gap-4">
                      <button className="mt-1 shrink-0">
                        {completedTasks.has(index) ? (
                          <CheckCircle2 className="w-5 h-5 text-green-400" />
                        ) : (
                          <Circle className="w-5 h-5 text-white/30" />
                        )}
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm text-indigo-400 font-medium">Day {task.day}</span>
                          <Badge variant="outline" className={getTypeColor(task.type)}>
                            {task.type}
                          </Badge>
                          <span className={`text-xs ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                        </div>
                        <h4 className={`font-medium mb-1 ${completedTasks.has(index) ? 'text-white/50 line-through' : 'text-white'}`}>
                          {task.title}
                        </h4>
                        <p className={`text-sm ${completedTasks.has(index) ? 'text-white/30' : 'text-white/60'}`}>
                          {task.description}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Stats */}
              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display font-semibold text-white mb-4">Plan Overview</h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-pink-500/20 flex items-center justify-center">
                      <Target className="w-5 h-5 text-pink-400" />
                    </div>
                    <div>
                      <p className="text-sm text-white/50">Post Tasks</p>
                      <p className="font-medium text-white">
                        {currentPlan.daily_tasks?.filter(t => t.type === "post").length || 0}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
                      <Clock className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-sm text-white/50">Engage Tasks</p>
                      <p className="font-medium text-white">
                        {currentPlan.daily_tasks?.filter(t => t.type === "engage").length || 0}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                      <Lightbulb className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <p className="text-sm text-white/50">Learn Tasks</p>
                      <p className="font-medium text-white">
                        {currentPlan.daily_tasks?.filter(t => t.type === "learn").length || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Previous Plans */}
              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display font-semibold text-white mb-4">Previous Plans</h3>
                <div className="space-y-3">
                  {plans.map((plan) => (
                    <button
                      key={plan.plan_id}
                      onClick={() => {
                        setCurrentPlan(plan);
                        setCompletedTasks(new Set());
                      }}
                      className={`w-full p-4 rounded-xl text-left transition-all ${
                        currentPlan?.plan_id === plan.plan_id
                          ? 'bg-indigo-500/10 border border-indigo-500/30'
                          : 'bg-white/5 border border-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-white">{plan.duration}-Day Plan</span>
                        <Badge variant="outline" className="text-xs bg-white/5 border-white/10 text-white/60">
                          {plan.daily_tasks?.length || 0} tasks
                        </Badge>
                      </div>
                      <span className="text-xs text-white/40">
                        {new Date(plan.created_at).toLocaleDateString()}
                      </span>
                    </button>
                  ))}
                  {plans.length === 0 && (
                    <p className="text-sm text-white/40 text-center py-4">No plans yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No growth plans yet</h3>
            <p className="text-white/50 mb-6">Create your first AI-powered growth plan</p>
            <Button
              onClick={generatePlan}
              disabled={generating || !selectedAccount}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              {generating ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Plus className="w-5 h-5 mr-2" />}
              Create First Plan
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default GrowthPlannerPage;
