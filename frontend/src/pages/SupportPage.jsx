import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  HelpCircle, Plus, MessageSquare, Clock, CheckCircle2, 
  AlertCircle, Loader2, Send, ArrowLeft, Filter
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const categories = [
  { value: "general", label: "General Question" },
  { value: "billing", label: "Billing & Subscription" },
  { value: "technical", label: "Technical Issue" },
  { value: "feature", label: "Feature Request" },
  { value: "bug", label: "Bug Report" }
];

const priorities = [
  { value: "low", label: "Low", color: "text-gray-400" },
  { value: "normal", label: "Normal", color: "text-blue-400" },
  { value: "high", label: "High", color: "text-orange-400" },
  { value: "urgent", label: "Urgent", color: "text-red-400" }
];

const SupportPage = ({ auth }) => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [filter, setFilter] = useState("all");
  
  const [newTicket, setNewTicket] = useState({
    subject: "",
    message: "",
    category: "general",
    priority: "normal"
  });

  useEffect(() => {
    fetchTickets();
  }, [filter]);

  const fetchTickets = async () => {
    try {
      const url = filter === "all" 
        ? `${API_URL}/api/support/tickets`
        : `${API_URL}/api/support/tickets?status=${filter}`;
      
      const response = await fetch(url, { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setTickets(data.tickets);
      }
    } catch (error) {
      toast.error("Failed to fetch tickets");
    } finally {
      setLoading(false);
    }
  };

  const createTicket = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const params = new URLSearchParams({
        subject: newTicket.subject,
        message: newTicket.message,
        category: newTicket.category,
        priority: newTicket.priority
      });
      
      const response = await fetch(`${API_URL}/api/support/tickets?${params}`, {
        method: "POST",
        credentials: "include"
      });
      
      if (!response.ok) throw new Error("Failed to create ticket");
      
      toast.success("Support ticket created!");
      setDialogOpen(false);
      setNewTicket({ subject: "", message: "", category: "general", priority: "normal" });
      fetchTickets();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const viewTicket = async (ticketId) => {
    try {
      const response = await fetch(`${API_URL}/api/support/tickets/${ticketId}`, {
        credentials: "include"
      });
      if (response.ok) {
        const ticket = await response.json();
        setSelectedTicket(ticket);
      }
    } catch (error) {
      toast.error("Failed to load ticket");
    }
  };

  const sendReply = async () => {
    if (!replyText.trim()) return;
    setSubmitting(true);
    
    try {
      const response = await fetch(
        `${API_URL}/api/support/tickets/${selectedTicket.ticket_id}/reply?message=${encodeURIComponent(replyText)}`,
        { method: "POST", credentials: "include" }
      );
      
      if (!response.ok) throw new Error("Failed to send reply");
      
      toast.success("Reply sent!");
      setReplyText("");
      viewTicket(selectedTicket.ticket_id);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const closeTicket = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/support/tickets/${selectedTicket.ticket_id}/close`,
        { method: "POST", credentials: "include" }
      );
      
      if (!response.ok) throw new Error("Failed to close ticket");
      
      toast.success("Ticket closed");
      setSelectedTicket(null);
      fetchTickets();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      open: "bg-green-500/20 text-green-400",
      pending: "bg-yellow-500/20 text-yellow-400",
      closed: "bg-gray-500/20 text-gray-400"
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getPriorityBadge = (priority) => {
    const p = priorities.find(pr => pr.value === priority);
    return <span className={`text-xs ${p?.color}`}>{p?.label}</span>;
  };

  if (selectedTicket) {
    return (
      <DashboardLayout auth={auth}>
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => setSelectedTicket(null)}
            className="flex items-center gap-2 text-white/60 hover:text-white mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Tickets
          </button>

          <div className="bg-[#0F0F11]/80 border border-white/5 rounded-2xl overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-white/40 text-sm">{selectedTicket.ticket_id}</span>
                    {getStatusBadge(selectedTicket.status)}
                    {getPriorityBadge(selectedTicket.priority)}
                  </div>
                  <h2 className="text-xl font-bold text-white">{selectedTicket.subject}</h2>
                  <p className="text-white/50 text-sm mt-1">
                    {selectedTicket.category} • Created {new Date(selectedTicket.created_at).toLocaleDateString()}
                  </p>
                </div>
                {selectedTicket.status !== "closed" && (
                  <Button
                    onClick={closeTicket}
                    variant="outline"
                    className="bg-white/5 border-white/10 text-white/70 hover:bg-white/10"
                  >
                    Close Ticket
                  </Button>
                )}
              </div>
            </div>

            <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
              {selectedTicket.messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-xl ${
                    msg.sender_type === "admin"
                      ? "bg-indigo-500/10 border border-indigo-500/20 ml-8"
                      : "bg-white/5 mr-8"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`font-medium ${msg.sender_type === "admin" ? "text-indigo-400" : "text-white"}`}>
                      {msg.sender_name}
                    </span>
                    <span className="text-white/30 text-xs">
                      {new Date(msg.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-white/80 whitespace-pre-wrap">{msg.message}</p>
                </div>
              ))}
            </div>

            {selectedTicket.status !== "closed" && (
              <div className="p-6 border-t border-white/5">
                <div className="flex gap-3">
                  <Textarea
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Type your reply..."
                    className="flex-1 bg-white/5 border-white/10 text-white min-h-[80px]"
                  />
                  <Button
                    onClick={sendReply}
                    disabled={submitting || !replyText.trim()}
                    className="bg-indigo-600 hover:bg-indigo-500 px-6"
                  >
                    {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Support</h1>
            <p className="text-white/60 mt-1">Get help from our team</p>
          </div>
          
          <div className="flex gap-3">
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-32 bg-white/5 border-white/10 text-white">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#0F0F11] border-white/10">
                <SelectItem value="all" className="text-white">All</SelectItem>
                <SelectItem value="open" className="text-white">Open</SelectItem>
                <SelectItem value="pending" className="text-white">Pending</SelectItem>
                <SelectItem value="closed" className="text-white">Closed</SelectItem>
              </SelectContent>
            </Select>
            
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white">
                  <Plus className="w-5 h-5 mr-2" />
                  New Ticket
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-lg">
                <DialogHeader>
                  <DialogTitle>Create Support Ticket</DialogTitle>
                </DialogHeader>
                <form onSubmit={createTicket} className="space-y-4 mt-4">
                  <div>
                    <Label className="text-white/70">Subject</Label>
                    <Input
                      value={newTicket.subject}
                      onChange={(e) => setNewTicket({ ...newTicket, subject: e.target.value })}
                      placeholder="Brief description of your issue"
                      className="bg-white/5 border-white/10 text-white mt-1"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-white/70">Category</Label>
                      <Select value={newTicket.category} onValueChange={(v) => setNewTicket({ ...newTicket, category: v })}>
                        <SelectTrigger className="bg-white/5 border-white/10 text-white mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0F0F11] border-white/10">
                          {categories.map(cat => (
                            <SelectItem key={cat.value} value={cat.value} className="text-white">{cat.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label className="text-white/70">Priority</Label>
                      <Select value={newTicket.priority} onValueChange={(v) => setNewTicket({ ...newTicket, priority: v })}>
                        <SelectTrigger className="bg-white/5 border-white/10 text-white mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0F0F11] border-white/10">
                          {priorities.map(p => (
                            <SelectItem key={p.value} value={p.value} className="text-white">{p.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label className="text-white/70">Message</Label>
                    <Textarea
                      value={newTicket.message}
                      onChange={(e) => setNewTicket({ ...newTicket, message: e.target.value })}
                      placeholder="Describe your issue in detail..."
                      className="bg-white/5 border-white/10 text-white mt-1 min-h-[120px]"
                      required
                    />
                  </div>
                  <div className="flex gap-3 pt-2">
                    <Button type="button" variant="outline" onClick={() => setDialogOpen(false)} className="flex-1 bg-white/5 border-white/10 text-white">
                      Cancel
                    </Button>
                    <Button type="submit" disabled={submitting} className="flex-1 bg-indigo-600 hover:bg-indigo-500">
                      {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Ticket"}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        ) : tickets.length === 0 ? (
          <div className="text-center py-20">
            <HelpCircle className="w-16 h-16 text-white/20 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">No support tickets</h3>
            <p className="text-white/50 mb-6">Create a ticket to get help from our team</p>
            <Button onClick={() => setDialogOpen(true)} className="bg-indigo-600 hover:bg-indigo-500">
              <Plus className="w-5 h-5 mr-2" />
              Create Ticket
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {tickets.map((ticket) => (
              <motion.div
                key={ticket.ticket_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-5 rounded-xl bg-[#0F0F11]/80 border border-white/5 hover:border-indigo-500/30 cursor-pointer transition-all"
                onClick={() => viewTicket(ticket.ticket_id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-white/40 text-sm">{ticket.ticket_id}</span>
                      {getStatusBadge(ticket.status)}
                      {getPriorityBadge(ticket.priority)}
                    </div>
                    <h3 className="font-semibold text-white">{ticket.subject}</h3>
                    <p className="text-white/50 text-sm mt-1">
                      {ticket.category} • {ticket.messages?.length || 1} messages
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-white/40 text-xs">
                      {new Date(ticket.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default SupportPage;
