import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  BarChart3, AlertTriangle, CheckCircle, TrendingUp, 
  Download, Loader2, Play, Target, Lightbulb, Calendar
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Progress } from "../components/ui/progress";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AuditPage = ({ auth }) => {
  const [searchParams] = useSearchParams();
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(searchParams.get("account") || "");
  const [audits, setAudits] = useState([]);
  const [currentAudit, setCurrentAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchAccounts();
    fetchAudits();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchAudits(selectedAccount);
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
        if (data.length > 0 && !selectedAccount) {
          setSelectedAccount(data[0].account_id);
        }
      }
    } catch (error) {
      console.error("Failed to fetch accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAudits = async (accountId) => {
    try {
      const url = accountId 
        ? `${API_URL}/api/audits?account_id=${accountId}`
        : `${API_URL}/api/audits`;
      const response = await fetch(url, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setAudits(data);
        if (data.length > 0) {
          setCurrentAudit(data[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch audits:", error);
    }
  };

  const generateAudit = async () => {
    if (!selectedAccount) {
      toast.error("Please select an account first");
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(`${API_URL}/api/audits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ account_id: selectedAccount }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to generate audit");
      }

      const audit = await response.json();
      setCurrentAudit(audit);
      setAudits([audit, ...audits]);
      toast.success("Audit generated successfully!");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setGenerating(false);
    }
  };

  const downloadPDF = async (auditId) => {
    try {
      const response = await fetch(`${API_URL}/api/audits/${auditId}/pdf`, {
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
      a.download = `audit_${auditId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case "low": return "text-green-400 bg-green-500/10 border-green-500/20";
      case "medium": return "text-yellow-400 bg-yellow-500/10 border-yellow-500/20";
      case "high": return "text-red-400 bg-red-500/10 border-red-500/20";
      default: return "text-white/50 bg-white/5 border-white/10";
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">AI Account Audit</h1>
            <p className="text-white/60 mt-1">Get detailed analysis and growth recommendations</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={selectedAccount} onValueChange={setSelectedAccount}>
              <SelectTrigger className="w-48 h-11 bg-white/5 border-white/10 rounded-xl text-white" data-testid="audit-account-select">
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
            <Button
              onClick={generateAudit}
              disabled={generating || !selectedAccount}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]"
              data-testid="generate-audit-btn"
            >
              {generating ? (
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
              ) : (
                <Play className="w-5 h-5 mr-2" />
              )}
              Run Audit
            </Button>
          </div>
        </div>

        {accounts.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No accounts to audit</h3>
            <p className="text-white/50 mb-6">Add an Instagram account first to run audits</p>
            <Button
              onClick={() => window.location.href = "/accounts"}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              Add Account
            </Button>
          </div>
        ) : currentAudit ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Audit Results */}
            <div className="lg:col-span-2 space-y-6">
              {/* Score Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-5 h-5 text-indigo-400" />
                    <span className="text-sm text-white/60">Engagement Score</span>
                  </div>
                  <div className={`text-4xl font-display font-bold ${getScoreColor(currentAudit.engagement_score)}`}>
                    {currentAudit.engagement_score}
                  </div>
                  <Progress value={currentAudit.engagement_score} className="mt-3 h-1.5 bg-white/10" />
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5 text-yellow-400" />
                    <span className="text-sm text-white/60">Shadowban Risk</span>
                  </div>
                  <div className={`inline-flex px-4 py-2 rounded-full border text-lg font-medium ${getRiskColor(currentAudit.shadowban_risk)}`}>
                    {currentAudit.shadowban_risk?.toUpperCase()}
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Target className="w-5 h-5 text-teal-400" />
                    <span className="text-sm text-white/60">Content Consistency</span>
                  </div>
                  <div className={`text-4xl font-display font-bold ${getScoreColor(currentAudit.content_consistency)}`}>
                    {currentAudit.content_consistency}
                  </div>
                  <Progress value={currentAudit.content_consistency} className="mt-3 h-1.5 bg-white/10" />
                </motion.div>
              </div>

              {/* Growth Mistakes */}
              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  Growth Mistakes Detected
                </h3>
                <ul className="space-y-3">
                  {currentAudit.growth_mistakes?.map((mistake, index) => (
                    <li key={index} className="flex items-start gap-3 p-3 rounded-xl bg-red-500/5 border border-red-500/10">
                      <span className="w-6 h-6 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center text-sm font-medium shrink-0">
                        {index + 1}
                      </span>
                      <span className="text-white/80">{mistake}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommendations */}
              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  Recommendations
                </h3>
                <ul className="space-y-3">
                  {currentAudit.recommendations?.map((rec, index) => (
                    <li key={index} className="flex items-start gap-3 p-3 rounded-xl bg-green-500/5 border border-green-500/10">
                      <CheckCircle className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
                      <span className="text-white/80">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 30-Day Roadmap */}
              {currentAudit.roadmap && (
                <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                  <h3 className="font-display text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-indigo-400" />
                    30-Day Recovery Roadmap
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {Object.entries(currentAudit.roadmap).map(([week, tasks], index) => (
                      <div key={week} className="p-4 rounded-xl bg-white/5 border border-white/5">
                        <h4 className="font-medium text-white mb-3 capitalize">{week.replace(/(\d)/, ' $1')}</h4>
                        <ul className="space-y-2">
                          {(Array.isArray(tasks) ? tasks : []).map((task, i) => (
                            <li key={i} className="text-sm text-white/60 flex items-start gap-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0"></span>
                              {task}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar - Audit History */}
            <div className="space-y-6">
              {/* Download PDF */}
              {auth.user?.role !== "starter" && (
                <Button
                  onClick={() => downloadPDF(currentAudit.audit_id)}
                  className="w-full h-11 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white"
                  data-testid="download-pdf-btn"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Download PDF Report
                </Button>
              )}

              {/* Previous Audits */}
              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display font-semibold text-white mb-4">Previous Audits</h3>
                <div className="space-y-3">
                  {audits.map((audit) => (
                    <button
                      key={audit.audit_id}
                      onClick={() => setCurrentAudit(audit)}
                      className={`w-full p-4 rounded-xl text-left transition-all ${
                        currentAudit?.audit_id === audit.audit_id
                          ? 'bg-indigo-500/10 border border-indigo-500/30'
                          : 'bg-white/5 border border-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-white">@{audit.username}</span>
                        <span className={`text-sm font-medium ${getScoreColor(audit.engagement_score)}`}>
                          {audit.engagement_score}
                        </span>
                      </div>
                      <span className="text-xs text-white/40">
                        {new Date(audit.created_at).toLocaleDateString()}
                      </span>
                    </button>
                  ))}
                  {audits.length === 0 && (
                    <p className="text-sm text-white/40 text-center py-4">No audits yet</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <BarChart3 className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No audits yet</h3>
            <p className="text-white/50 mb-6">Run your first audit to see detailed analysis</p>
            <Button
              onClick={generateAudit}
              disabled={generating || !selectedAccount}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              {generating ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Play className="w-5 h-5 mr-2" />}
              Run First Audit
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AuditPage;
