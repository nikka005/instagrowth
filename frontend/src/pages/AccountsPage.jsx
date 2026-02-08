import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Instagram, Plus, MoreVertical, Edit2, Trash2, 
  BarChart3, Calendar, Hash, X, Loader2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "../components/ui/dropdown-menu";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Textarea } from "../components/ui/textarea";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const niches = [
  "Fashion & Beauty", "Fitness & Health", "Food & Cooking", "Travel & Lifestyle",
  "Tech & Gadgets", "Business & Finance", "Education", "Entertainment",
  "Art & Design", "Photography", "Music", "Gaming", "Parenting", "Pets", "Other"
];

const AccountsPage = ({ auth }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editAccount, setEditAccount] = useState(null);
  const [formData, setFormData] = useState({ username: "", niche: "", notes: "" });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/accounts`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
      }
    } catch (error) {
      toast.error("Failed to fetch accounts");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const url = editAccount 
        ? `${API_URL}/api/accounts/${editAccount.account_id}`
        : `${API_URL}/api/accounts`;
      
      const response = await fetch(url, {
        method: editAccount ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to save account");
      }

      toast.success(editAccount ? "Account updated!" : "Account added!");
      setDialogOpen(false);
      setEditAccount(null);
      setFormData({ username: "", niche: "", notes: "" });
      fetchAccounts();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (accountId) => {
    if (!window.confirm("Are you sure you want to delete this account?")) return;

    try {
      const response = await fetch(`${API_URL}/api/accounts/${accountId}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) throw new Error("Failed to delete account");
      
      toast.success("Account deleted");
      fetchAccounts();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const openEditDialog = (account) => {
    setEditAccount(account);
    setFormData({
      username: account.username,
      niche: account.niche,
      notes: account.notes || "",
    });
    setDialogOpen(true);
  };

  const openAddDialog = () => {
    setEditAccount(null);
    setFormData({ username: "", niche: "", notes: "" });
    setDialogOpen(true);
  };

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Instagram Accounts</h1>
            <p className="text-white/60 mt-1">
              Manage your Instagram accounts ({accounts.length}/{auth.user?.account_limit || 1})
            </p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                onClick={openAddDialog}
                className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                disabled={accounts.length >= (auth.user?.account_limit || 1)}
                data-testid="add-account-btn"
              >
                <Plus className="w-5 h-5 mr-2" />
                Add Account
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-md">
              <DialogHeader>
                <DialogTitle className="font-display text-xl">
                  {editAccount ? "Edit Account" : "Add Instagram Account"}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-5 mt-4">
                <div>
                  <Label className="text-white/70 mb-2 block">Username</Label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">@</span>
                    <Input
                      placeholder="username"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="h-12 pl-9 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                      required
                      data-testid="account-username-input"
                    />
                  </div>
                </div>
                <div>
                  <Label className="text-white/70 mb-2 block">Niche</Label>
                  <Select
                    value={formData.niche}
                    onValueChange={(value) => setFormData({ ...formData, niche: value })}
                    required
                  >
                    <SelectTrigger className="h-12 bg-white/5 border-white/10 rounded-xl text-white" data-testid="account-niche-select">
                      <SelectValue placeholder="Select a niche" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0F0F11] border-white/10">
                      {niches.map((niche) => (
                        <SelectItem key={niche} value={niche} className="text-white hover:bg-white/5">
                          {niche}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-white/70 mb-2 block">Notes (optional)</Label>
                  <Textarea
                    placeholder="Add any notes about this account..."
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30 min-h-[100px]"
                    data-testid="account-notes-input"
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setDialogOpen(false)}
                    className="flex-1 h-11 rounded-xl bg-white/5 border-white/10 text-white hover:bg-white/10"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={submitting || !formData.niche}
                    className="flex-1 h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                    data-testid="account-submit-btn"
                  >
                    {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : (editAccount ? "Update" : "Add Account")}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Accounts Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        ) : accounts.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Instagram className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No accounts yet</h3>
            <p className="text-white/50 mb-6">Add your first Instagram account to get started</p>
            <Button
              onClick={openAddDialog}
              className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Your First Account
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
              {accounts.map((account, index) => (
                <motion.div
                  key={account.account_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="group p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5 hover:border-indigo-500/30 transition-all"
                  data-testid={`account-card-${account.username}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center">
                        <Instagram className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-display font-semibold text-white">@{account.username}</h3>
                        <p className="text-sm text-white/50">{account.niche}</p>
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button className="p-2 text-white/50 hover:text-white rounded-lg hover:bg-white/5" data-testid={`account-menu-${account.username}`}>
                          <MoreVertical className="w-5 h-5" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="bg-[#0F0F11] border-white/10">
                        <DropdownMenuItem onClick={() => openEditDialog(account)} className="text-white/70 hover:text-white cursor-pointer">
                          <Edit2 className="w-4 h-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleDelete(account.account_id)} className="text-red-400 hover:text-red-300 cursor-pointer">
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  {account.notes && (
                    <p className="text-sm text-white/50 mb-4 line-clamp-2">{account.notes}</p>
                  )}

                  <div className="flex items-center gap-2 text-xs text-white/40">
                    {account.last_audit_date ? (
                      <span className="flex items-center gap-1">
                        <BarChart3 className="w-3 h-3" />
                        Last audit: {new Date(account.last_audit_date).toLocaleDateString()}
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <BarChart3 className="w-3 h-3" />
                        No audits yet
                      </span>
                    )}
                  </div>

                  <div className="flex gap-2 mt-4 pt-4 border-t border-white/5">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex-1 text-white/60 hover:text-white hover:bg-white/5"
                      onClick={() => window.location.href = `/audit?account=${account.account_id}`}
                    >
                      <BarChart3 className="w-4 h-4 mr-1" />
                      Audit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="flex-1 text-white/60 hover:text-white hover:bg-white/5"
                      onClick={() => window.location.href = `/content?account=${account.account_id}`}
                    >
                      <Hash className="w-4 h-4 mr-1" />
                      Content
                    </Button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default AccountsPage;
