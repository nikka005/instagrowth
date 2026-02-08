import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  FlaskConical, Plus, ThumbsUp, Check, Trophy,
  Loader2, BarChart2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ABTestingPage = ({ auth }) => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState("");
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    content_type: "hooks",
    variant_a: "",
    variant_b: "",
  });
  const [creating, setCreating] = useState(false);
  const [voting, setVoting] = useState(null);

  useEffect(() => {
    fetchAccounts();
    fetchTests();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchTests(selectedAccount);
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

  const fetchTests = async (accountId) => {
    try {
      const url = accountId 
        ? `${API_URL}/api/ab-tests?account_id=${accountId}`
        : `${API_URL}/api/ab-tests`;
      const response = await fetch(url, { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setTests(data);
      }
    } catch (error) {
      console.error("Failed to fetch tests:", error);
    }
  };

  const createTest = async () => {
    if (!selectedAccount || !formData.variant_a || !formData.variant_b) {
      toast.error("Please fill all fields");
      return;
    }

    setCreating(true);
    try {
      const response = await fetch(`${API_URL}/api/ab-tests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          account_id: selectedAccount,
          ...formData,
        }),
      });

      if (!response.ok) throw new Error("Failed to create test");

      const data = await response.json();
      setTests([data, ...tests]);
      setDialogOpen(false);
      setFormData({ content_type: "hooks", variant_a: "", variant_b: "" });
      toast.success("A/B Test created!");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setCreating(false);
    }
  };

  const vote = async (testId, variant) => {
    setVoting(`${testId}-${variant}`);
    try {
      const response = await fetch(`${API_URL}/api/ab-tests/${testId}/vote?variant=${variant}`, {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to vote");
      }

      const data = await response.json();
      
      // Update the test in state
      setTests(tests.map(t => {
        if (t.test_id === testId) {
          return {
            ...t,
            votes_a: data.votes_a,
            votes_b: data.votes_b,
            status: data.votes_a + data.votes_b >= 10 ? "completed" : "active",
            winner: data.votes_a + data.votes_b >= 10 
              ? (data.votes_a > data.votes_b ? "a" : data.votes_b > data.votes_a ? "b" : "tie")
              : null
          };
        }
        return t;
      }));
      
      toast.success("Vote recorded!");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setVoting(null);
    }
  };

  const getWinnerVariant = (test) => {
    if (test.winner === "a") return test.variant_a;
    if (test.winner === "b") return test.variant_b;
    return "Tie";
  };

  const activeTests = tests.filter(t => t.status === "active");
  const completedTests = tests.filter(t => t.status === "completed");

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">A/B Testing</h1>
            <p className="text-white/60 mt-1">Test and optimize your content</p>
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
                  <Plus className="w-5 h-5 mr-2" />
                  New Test
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-lg">
                <DialogHeader>
                  <DialogTitle className="font-display text-xl">Create A/B Test</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <div>
                    <Label className="text-white/70 mb-2 block">Content Type</Label>
                    <Select value={formData.content_type} onValueChange={(v) => setFormData({ ...formData, content_type: v })}>
                      <SelectTrigger className="h-11 bg-white/5 border-white/10 rounded-xl text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#0F0F11] border-white/10">
                        <SelectItem value="hooks" className="text-white">Hooks</SelectItem>
                        <SelectItem value="captions" className="text-white">Captions</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-white/70 mb-2 block">Variant A</Label>
                    <Textarea
                      placeholder="Enter first variant..."
                      value={formData.variant_a}
                      onChange={(e) => setFormData({ ...formData, variant_a: e.target.value })}
                      className="min-h-[100px] bg-white/5 border-white/10 rounded-xl text-white"
                    />
                  </div>
                  <div>
                    <Label className="text-white/70 mb-2 block">Variant B</Label>
                    <Textarea
                      placeholder="Enter second variant..."
                      value={formData.variant_b}
                      onChange={(e) => setFormData({ ...formData, variant_b: e.target.value })}
                      className="min-h-[100px] bg-white/5 border-white/10 rounded-xl text-white"
                    />
                  </div>
                  <Button
                    onClick={createTest}
                    disabled={creating}
                    className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                  >
                    {creating ? <Loader2 className="w-5 h-5 animate-spin" /> : "Create Test"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Active Tests */}
        {activeTests.length > 0 && (
          <div>
            <h2 className="font-display text-lg font-semibold text-white mb-4">Active Tests</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {activeTests.map((test, index) => (
                <motion.div
                  key={test.test_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
                >
                  <div className="flex items-center justify-between mb-4">
                    <Badge variant="outline" className="bg-indigo-500/20 text-indigo-400 border-indigo-500/30">
                      {test.content_type}
                    </Badge>
                    <span className="text-xs text-white/40">
                      {test.votes_a + test.votes_b}/10 votes
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {/* Variant A */}
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-white">Variant A</span>
                        <span className="text-sm text-indigo-400">{test.votes_a} votes</span>
                      </div>
                      <p className="text-sm text-white/70 line-clamp-3 mb-3">{test.variant_a}</p>
                      <Button
                        onClick={() => vote(test.test_id, "a")}
                        disabled={voting === `${test.test_id}-a`}
                        className="w-full h-9 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-400"
                      >
                        {voting === `${test.test_id}-a` ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <ThumbsUp className="w-4 h-4 mr-1" />
                            Vote A
                          </>
                        )}
                      </Button>
                    </div>

                    {/* Variant B */}
                    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-white">Variant B</span>
                        <span className="text-sm text-purple-400">{test.votes_b} votes</span>
                      </div>
                      <p className="text-sm text-white/70 line-clamp-3 mb-3">{test.variant_b}</p>
                      <Button
                        onClick={() => vote(test.test_id, "b")}
                        disabled={voting === `${test.test_id}-b`}
                        className="w-full h-9 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-400"
                      >
                        {voting === `${test.test_id}-b` ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <ThumbsUp className="w-4 h-4 mr-1" />
                            Vote B
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="flex items-center justify-between text-xs text-white/40 mb-1">
                      <span>Progress</span>
                      <span>{Math.round(((test.votes_a + test.votes_b) / 10) * 100)}%</span>
                    </div>
                    <Progress value={((test.votes_a + test.votes_b) / 10) * 100} className="h-1.5" />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Completed Tests */}
        {completedTests.length > 0 && (
          <div>
            <h2 className="font-display text-lg font-semibold text-white mb-4">Completed Tests</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {completedTests.map((test, index) => (
                <motion.div
                  key={test.test_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-green-500/20"
                >
                  <div className="flex items-center justify-between mb-4">
                    <Badge variant="outline" className="bg-green-500/20 text-green-400 border-green-500/30">
                      <Check className="w-3 h-3 mr-1" />
                      Completed
                    </Badge>
                    <Badge variant="outline" className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                      <Trophy className="w-3 h-3 mr-1" />
                      Winner: {test.winner?.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20 mb-4">
                    <span className="text-sm font-medium text-green-400 block mb-2">Winning Content</span>
                    <p className="text-white/80">{getWinnerVariant(test)}</p>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-white/50">Variant A</span>
                        <span className="text-white">{test.votes_a} votes</span>
                      </div>
                      <Progress value={(test.votes_a / (test.votes_a + test.votes_b)) * 100} className="h-2" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-white/50">Variant B</span>
                        <span className="text-white">{test.votes_b} votes</span>
                      </div>
                      <Progress value={(test.votes_b / (test.votes_a + test.votes_b)) * 100} className="h-2 [&>div]:bg-purple-500" />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {tests.length === 0 && !loading && (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <FlaskConical className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No A/B tests yet</h3>
            <p className="text-white/50 mb-6">Create your first test to optimize your content</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ABTestingPage;
