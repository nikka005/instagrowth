import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  Users, Search, TrendingUp, Target, Lightbulb,
  Loader2, Plus, BarChart3, Eye
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CompetitorAnalysisPage = ({ auth }) => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [analyses, setAnalyses] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [competitors, setCompetitors] = useState([""]);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchAccounts();
    fetchAnalyses();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchAnalyses(selectedAccount);
    }
  }, [selectedAccount]);

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/accounts`, { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
        if (data.length > 0) {
          setSelectedAccount(data[0].account_id);
        }
      }
    } catch (error) {
      console.error("Failed to fetch accounts:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalyses = async (accountId) => {
    try {
      const url = accountId 
        ? `${API_URL}/api/competitor-analysis?account_id=${accountId}`
        : `${API_URL}/api/competitor-analysis`;
      const response = await fetch(url, { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setAnalyses(data);
        if (data.length > 0) {
          setCurrentAnalysis(data[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch analyses:", error);
    }
  };

  const runAnalysis = async () => {
    if (!selectedAccount || competitors.filter(c => c.trim()).length === 0) {
      toast.error("Please select an account and add at least one competitor");
      return;
    }

    setAnalyzing(true);
    try {
      const response = await fetch(`${API_URL}/api/competitor-analysis`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          account_id: selectedAccount,
          competitor_usernames: competitors.filter(c => c.trim()),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Analysis failed");
      }

      const data = await response.json();
      setCurrentAnalysis(data);
      setAnalyses([data, ...analyses]);
      setDialogOpen(false);
      setCompetitors([""]);
      toast.success("Analysis complete!");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const addCompetitorField = () => {
    if (competitors.length < 5) {
      setCompetitors([...competitors, ""]);
    }
  };

  const updateCompetitor = (index, value) => {
    const newCompetitors = [...competitors];
    newCompetitors[index] = value;
    setCompetitors(newCompetitors);
  };

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Competitor Analysis</h1>
            <p className="text-white/60 mt-1">AI-powered competitor insights and opportunities</p>
          </div>
          <div className="flex items-center gap-3">
            <Select value={selectedAccount} onValueChange={setSelectedAccount}>
              <SelectTrigger className="w-48 h-11 bg-white/5 border-white/10 rounded-xl text-white">
                <SelectValue placeholder="Select account" />
              </SelectTrigger>
              <SelectContent className="bg-[#0F0F11] border-white/10">
                {accounts.map((account) => (
                  <SelectItem key={account.account_id} value={account.account_id} className="text-white">
                    @{account.username}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]">
                  <Search className="w-5 h-5 mr-2" />
                  Analyze Competitors
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-md">
                <DialogHeader>
                  <DialogTitle className="font-display text-xl">Analyze Competitors</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div>
                    <Label className="text-white/70 mb-2 block">Competitor Usernames (up to 5)</Label>
                    {competitors.map((comp, index) => (
                      <div key={index} className="flex items-center gap-2 mb-2">
                        <span className="text-white/40">@</span>
                        <Input
                          placeholder="competitor_username"
                          value={comp}
                          onChange={(e) => updateCompetitor(index, e.target.value)}
                          className="h-10 bg-white/5 border-white/10 rounded-xl text-white"
                        />
                      </div>
                    ))}
                    {competitors.length < 5 && (
                      <Button
                        type="button"
                        variant="ghost"
                        onClick={addCompetitorField}
                        className="text-indigo-400 hover:text-indigo-300"
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Another
                      </Button>
                    )}
                  </div>
                  <Button
                    onClick={runAnalysis}
                    disabled={analyzing}
                    className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                  >
                    {analyzing ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Search className="w-5 h-5 mr-2" />}
                    Run Analysis
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {accounts.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No accounts yet</h3>
            <p className="text-white/50 mb-6">Add an Instagram account first</p>
          </div>
        ) : currentAnalysis ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Competitors */}
            <div className="lg:col-span-2 space-y-4">
              <h3 className="font-display font-semibold text-white">Competitor Breakdown</h3>
              {currentAnalysis.competitors?.map((comp, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-display font-semibold text-white">@{comp.username}</h4>
                    <Badge variant="outline" className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30">
                      {comp.estimated_followers?.toLocaleString()} followers
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <span className="text-sm text-white/50">Engagement Rate</span>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xl font-bold text-white">{comp.estimated_engagement_rate}%</span>
                        <Progress value={comp.estimated_engagement_rate * 10} className="flex-1 h-2" />
                      </div>
                    </div>
                    <div>
                      <span className="text-sm text-white/50">Posting Frequency</span>
                      <p className="text-white font-medium mt-1">{comp.posting_frequency}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-white/50 flex items-center gap-1">
                        <TrendingUp className="w-4 h-4 text-green-400" />
                        Strengths
                      </span>
                      <ul className="mt-2 space-y-1">
                        {comp.strengths?.slice(0, 3).map((s, i) => (
                          <li key={i} className="text-sm text-white/70">• {s}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="text-sm text-white/50 flex items-center gap-1">
                        <Target className="w-4 h-4 text-red-400" />
                        Weaknesses
                      </span>
                      <ul className="mt-2 space-y-1">
                        {comp.weaknesses?.slice(0, 3).map((w, i) => (
                          <li key={i} className="text-sm text-white/70">• {w}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Insights & Opportunities */}
            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20">
                <h3 className="font-display font-semibold text-white mb-4 flex items-center gap-2">
                  <Eye className="w-5 h-5 text-indigo-400" />
                  Key Insights
                </h3>
                <ul className="space-y-3">
                  {currentAnalysis.insights?.map((insight, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                      <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display font-semibold text-white mb-4 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  Opportunities
                </h3>
                <ul className="space-y-3">
                  {currentAnalysis.opportunities?.map((opp, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                      <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 mt-2 shrink-0"></span>
                      {opp}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Previous Analyses */}
              <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                <h3 className="font-display font-semibold text-white mb-4">Previous Analyses</h3>
                <div className="space-y-2">
                  {analyses.slice(0, 5).map((analysis) => (
                    <button
                      key={analysis.analysis_id}
                      onClick={() => setCurrentAnalysis(analysis)}
                      className={`w-full p-3 rounded-xl text-left transition-all ${
                        currentAnalysis?.analysis_id === analysis.analysis_id
                          ? 'bg-indigo-500/10 border border-indigo-500/30'
                          : 'bg-white/5 border border-white/5 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-white">
                          {analysis.competitors?.length} competitors
                        </span>
                        <span className="text-xs text-white/40">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No analyses yet</h3>
            <p className="text-white/50 mb-6">Run your first competitor analysis</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default CompetitorAnalysisPage;
