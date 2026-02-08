import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Sparkles, Film, MessageSquare, Hash, Copy, Check,
  Loader2, RefreshCw, Bookmark, Clock
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ContentPage = ({ auth }) => {
  const [searchParams] = useSearchParams();
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(searchParams.get("account") || "");
  const [activeTab, setActiveTab] = useState("reels");
  const [topic, setTopic] = useState("");
  const [content, setContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchHistory();
    }
  }, [selectedAccount, activeTab]);

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
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/content?account_id=${selectedAccount}&content_type=${activeTab}`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  const generateContent = async () => {
    if (!selectedAccount) {
      toast.error("Please select an account first");
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch(`${API_URL}/api/content/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          account_id: selectedAccount,
          content_type: activeTab,
          topic: topic || undefined,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to generate content");
      }

      const data = await response.json();
      setContent(data.content);
      fetchHistory();
      toast.success("Content generated!");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const getTabIcon = (tab) => {
    switch (tab) {
      case "reels": return <Film className="w-4 h-4" />;
      case "hooks": return <Sparkles className="w-4 h-4" />;
      case "captions": return <MessageSquare className="w-4 h-4" />;
      case "hashtags": return <Hash className="w-4 h-4" />;
      default: return null;
    }
  };

  const getTabDescription = (tab) => {
    switch (tab) {
      case "reels": return "Viral Reel Ideas";
      case "hooks": return "Scroll-Stopping Hooks";
      case "captions": return "Engaging Captions";
      case "hashtags": return "Optimized Hashtags";
      default: return "";
    }
  };

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">AI Content Engine</h1>
            <p className="text-white/60 mt-1">Generate viral content ideas powered by AI</p>
          </div>
          <Select value={selectedAccount} onValueChange={setSelectedAccount}>
            <SelectTrigger className="w-48 h-11 bg-white/5 border-white/10 rounded-xl text-white" data-testid="content-account-select">
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
        </div>

        {accounts.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No accounts yet</h3>
            <p className="text-white/50 mb-6">Add an Instagram account first to generate content</p>
            <Button
              onClick={() => window.location.href = "/accounts"}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              Add Account
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content Area */}
            <div className="lg:col-span-2">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="bg-[#0F0F11]/80 border border-white/5 p-1 rounded-xl">
                  {["reels", "hooks", "captions", "hashtags"].map((tab) => (
                    <TabsTrigger
                      key={tab}
                      value={tab}
                      className="flex items-center gap-2 data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-400 rounded-lg px-4 py-2"
                      data-testid={`tab-${tab}`}
                    >
                      {getTabIcon(tab)}
                      <span className="capitalize hidden sm:inline">{tab}</span>
                    </TabsTrigger>
                  ))}
                </TabsList>

                {/* Generate Section */}
                <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                  <h3 className="font-display text-lg font-semibold text-white mb-4">
                    Generate {getTabDescription(activeTab)}
                  </h3>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Input
                      placeholder="Optional: Enter a topic or theme..."
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="flex-1 h-11 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                      data-testid="content-topic-input"
                    />
                    <Button
                      onClick={generateContent}
                      disabled={generating || !selectedAccount}
                      className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                      data-testid="generate-content-btn"
                    >
                      {generating ? (
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                      ) : (
                        <Sparkles className="w-5 h-5 mr-2" />
                      )}
                      Generate
                    </Button>
                  </div>
                </div>

                {/* Generated Content */}
                <TabsContent value={activeTab} className="space-y-4 mt-0">
                  {content && content.length > 0 ? (
                    <div className="space-y-3">
                      {content.map((item, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="group p-4 rounded-xl bg-[#0F0F11]/80 border border-white/5 hover:border-indigo-500/30 transition-all"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <p className="text-white/80 flex-1 whitespace-pre-wrap">
                              {typeof item === "string" ? item : JSON.stringify(item, null, 2)}
                            </p>
                            <button
                              onClick={() => copyToClipboard(typeof item === "string" ? item : JSON.stringify(item), index)}
                              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/50 hover:text-white transition-all shrink-0"
                              data-testid={`copy-btn-${index}`}
                            >
                              {copiedIndex === index ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 px-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
                      <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mx-auto mb-4">
                        {getTabIcon(activeTab)}
                      </div>
                      <p className="text-white/50">
                        Click generate to create {getTabDescription(activeTab).toLowerCase()}
                      </p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>

            {/* Sidebar - History */}
            <div className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
              <h3 className="font-display font-semibold text-white mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-white/50" />
                Recent Generations
              </h3>
              <div className="space-y-3">
                {history.slice(0, 5).map((item) => (
                  <button
                    key={item.content_id}
                    onClick={() => setContent(item.content)}
                    className="w-full p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 text-left transition-all"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {getTabIcon(item.content_type)}
                      <span className="text-sm font-medium text-white capitalize">{item.content_type}</span>
                    </div>
                    <p className="text-xs text-white/40 line-clamp-2">
                      {Array.isArray(item.content) ? item.content[0]?.substring(0, 60) + "..." : ""}
                    </p>
                    <span className="text-xs text-white/30 mt-2 block">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </button>
                ))}
                {history.length === 0 && (
                  <p className="text-sm text-white/40 text-center py-4">No history yet</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default ContentPage;
