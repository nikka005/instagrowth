import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  MessageSquare, Plus, Edit2, Trash2, Copy, Check,
  Loader2, Send, Sparkles, Tag
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const categories = [
  { value: "welcome", label: "Welcome Messages", color: "bg-green-500/20 text-green-400" },
  { value: "sales", label: "Sales & Promotion", color: "bg-blue-500/20 text-blue-400" },
  { value: "support", label: "Support", color: "bg-yellow-500/20 text-yellow-400" },
  { value: "follow_up", label: "Follow Up", color: "bg-purple-500/20 text-purple-400" },
  { value: "lead_qualify", label: "Lead Qualification", color: "bg-pink-500/20 text-pink-400" },
];

const DMTemplatesPage = ({ auth }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editTemplate, setEditTemplate] = useState(null);
  const [activeCategory, setActiveCategory] = useState("all");
  const [copiedId, setCopiedId] = useState(null);
  
  const [formData, setFormData] = useState({
    name: "",
    category: "welcome",
    message: "",
  });
  const [submitting, setSubmitting] = useState(false);
  
  // AI Reply Generator
  const [replyDialogOpen, setReplyDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [incomingMessage, setIncomingMessage] = useState("");
  const [generatedReply, setGeneratedReply] = useState("");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/api/dm-templates`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error("Failed to fetch templates:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const url = editTemplate 
        ? `${API_URL}/api/dm-templates/${editTemplate.template_id}`
        : `${API_URL}/api/dm-templates`;
      
      const response = await fetch(url, {
        method: editTemplate ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to save template");

      toast.success(editTemplate ? "Template updated!" : "Template created!");
      setDialogOpen(false);
      setEditTemplate(null);
      setFormData({ name: "", category: "welcome", message: "" });
      fetchTemplates();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (templateId) => {
    if (!window.confirm("Delete this template?")) return;

    try {
      const response = await fetch(`${API_URL}/api/dm-templates/${templateId}`, {
        method: "DELETE",
        credentials: "include",
      });
      if (!response.ok) throw new Error("Failed to delete");
      toast.success("Template deleted");
      fetchTemplates();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const openEditDialog = (template) => {
    setEditTemplate(template);
    setFormData({
      name: template.name,
      category: template.category,
      message: template.message,
    });
    setDialogOpen(true);
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success("Copied!");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const generateReply = async () => {
    if (!selectedTemplate || !incomingMessage) return;
    setGenerating(true);

    try {
      const response = await fetch(
        `${API_URL}/api/dm-templates/${selectedTemplate.template_id}/generate-reply`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ message: incomingMessage }),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to generate reply");
      }

      const data = await response.json();
      setGeneratedReply(data.reply);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setGenerating(false);
    }
  };

  const getCategoryColor = (category) => {
    return categories.find(c => c.value === category)?.color || "bg-white/10 text-white/60";
  };

  const filteredTemplates = activeCategory === "all" 
    ? templates 
    : templates.filter(t => t.category === activeCategory);

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">DM Templates</h1>
            <p className="text-white/60 mt-1">Create and manage auto-reply templates</p>
          </div>
          <div className="flex items-center gap-3">
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button 
                  onClick={() => {
                    setEditTemplate(null);
                    setFormData({ name: "", category: "welcome", message: "" });
                  }}
                  className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                  data-testid="create-template-btn"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  New Template
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-lg">
                <DialogHeader>
                  <DialogTitle className="font-display text-xl">
                    {editTemplate ? "Edit Template" : "Create DM Template"}
                  </DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-5 mt-4">
                  <div>
                    <Label className="text-white/70 mb-2 block">Template Name</Label>
                    <Input
                      placeholder="e.g., Welcome New Follower"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="h-12 bg-white/5 border-white/10 rounded-xl text-white"
                      required
                    />
                  </div>
                  <div>
                    <Label className="text-white/70 mb-2 block">Category</Label>
                    <Select value={formData.category} onValueChange={(v) => setFormData({ ...formData, category: v })}>
                      <SelectTrigger className="h-12 bg-white/5 border-white/10 rounded-xl text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#0F0F11] border-white/10">
                        {categories.map(cat => (
                          <SelectItem key={cat.value} value={cat.value} className="text-white">
                            {cat.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-white/70 mb-2 block">Message Template</Label>
                    <Textarea
                      placeholder="Hey {{name}}! Thanks for reaching out..."
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      className="min-h-[150px] bg-white/5 border-white/10 rounded-xl text-white"
                      required
                    />
                    <p className="text-xs text-white/40 mt-2">
                      Use {"{{name}}"}, {"{{product}}"} etc. for variables
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setDialogOpen(false)}
                      className="flex-1 h-11 rounded-xl bg-white/5 border-white/10 text-white"
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={submitting}
                      className="flex-1 h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                    >
                      {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : (editTemplate ? "Update" : "Create")}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Category Tabs */}
        <Tabs value={activeCategory} onValueChange={setActiveCategory}>
          <TabsList className="bg-[#0F0F11]/80 border border-white/5 p-1 rounded-xl flex-wrap h-auto gap-1">
            <TabsTrigger value="all" className="data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-400 rounded-lg px-4 py-2">
              All
            </TabsTrigger>
            {categories.map(cat => (
              <TabsTrigger 
                key={cat.value} 
                value={cat.value}
                className="data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-400 rounded-lg px-4 py-2"
              >
                {cat.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        {/* Templates Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        ) : filteredTemplates.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No templates yet</h3>
            <p className="text-white/50 mb-6">Create your first DM template to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredTemplates.map((template, index) => (
              <motion.div
                key={template.template_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-5 rounded-2xl bg-[#0F0F11]/80 border border-white/5 hover:border-indigo-500/30 transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-white">{template.name}</h3>
                    <Badge variant="outline" className={`mt-1 ${getCategoryColor(template.category)}`}>
                      {categories.find(c => c.value === template.category)?.label}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => copyToClipboard(template.message, template.template_id)}
                      className="p-2 text-white/50 hover:text-white rounded-lg hover:bg-white/5"
                    >
                      {copiedId === template.template_id ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => openEditDialog(template)}
                      className="p-2 text-white/50 hover:text-white rounded-lg hover:bg-white/5"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(template.template_id)}
                      className="p-2 text-red-400/50 hover:text-red-400 rounded-lg hover:bg-red-500/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <p className="text-sm text-white/60 line-clamp-3 mb-3">{template.message}</p>
                {template.variables?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {template.variables.map(v => (
                      <span key={v} className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400">
                        {`{{${v}}}`}
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex items-center justify-between pt-3 border-t border-white/5">
                  <span className="text-xs text-white/40">Used {template.use_count} times</span>
                  <Button
                    size="sm"
                    onClick={() => {
                      setSelectedTemplate(template);
                      setReplyDialogOpen(true);
                      setIncomingMessage("");
                      setGeneratedReply("");
                    }}
                    className="h-8 px-3 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-400 text-xs"
                  >
                    <Sparkles className="w-3 h-3 mr-1" />
                    Generate Reply
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* AI Reply Generator Dialog */}
        <Dialog open={replyDialogOpen} onOpenChange={setReplyDialogOpen}>
          <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-lg">
            <DialogHeader>
              <DialogTitle className="font-display text-xl">AI Reply Generator</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label className="text-white/70 mb-2 block">Incoming Message</Label>
                <Textarea
                  placeholder="Paste the message you received..."
                  value={incomingMessage}
                  onChange={(e) => setIncomingMessage(e.target.value)}
                  className="min-h-[100px] bg-white/5 border-white/10 rounded-xl text-white"
                />
              </div>
              <Button
                onClick={generateReply}
                disabled={generating || !incomingMessage}
                className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
              >
                {generating ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Sparkles className="w-5 h-5 mr-2" />}
                Generate Reply
              </Button>
              {generatedReply && (
                <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-green-400">Generated Reply</span>
                    <button
                      onClick={() => copyToClipboard(generatedReply, "reply")}
                      className="p-1 text-green-400 hover:bg-green-500/20 rounded"
                    >
                      {copiedId === "reply" ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-white/80">{generatedReply}</p>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
};

export default DMTemplatesPage;
