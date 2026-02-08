import { useState, useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Users, Plus, Mail, Shield, Crown, UserMinus, 
  Loader2, Upload, Palette, Settings, CheckCircle
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";
import DashboardLayout from "../components/DashboardLayout";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TeamPage = ({ auth }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [teams, setTeams] = useState([]);
  const [currentTeam, setCurrentTeam] = useState(null);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  
  const [teamName, setTeamName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("editor");
  const [brandColor, setBrandColor] = useState("#6366F1");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Check for invite token
    const inviteToken = searchParams.get("token");
    if (inviteToken) {
      acceptInvite(inviteToken);
    }
    
    fetchTeams();
  }, [searchParams]);

  useEffect(() => {
    if (currentTeam) {
      fetchMembers(currentTeam.team_id);
    }
  }, [currentTeam]);

  const fetchTeams = async () => {
    try {
      const response = await fetch(`${API_URL}/api/teams`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setTeams(data);
        if (data.length > 0) {
          setCurrentTeam(data[0]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch teams:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async (teamId) => {
    try {
      const response = await fetch(`${API_URL}/api/teams/${teamId}/members`, {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setMembers(data);
      }
    } catch (error) {
      console.error("Failed to fetch members:", error);
    }
  };

  const createTeam = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const response = await fetch(`${API_URL}/api/teams`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ name: teamName }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to create team");
      }
      
      const team = await response.json();
      setTeams([...teams, team]);
      setCurrentTeam(team);
      setCreateDialogOpen(false);
      setTeamName("");
      toast.success("Team created!");
      auth.checkAuth(); // Refresh user data
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const inviteMember = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const response = await fetch(`${API_URL}/api/teams/${currentTeam.team_id}/invite`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to send invite");
      }
      
      toast.success("Invitation sent!");
      setInviteDialogOpen(false);
      setInviteEmail("");
      fetchMembers(currentTeam.team_id);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setSubmitting(false);
    }
  };

  const acceptInvite = async (token) => {
    try {
      const response = await fetch(`${API_URL}/api/teams/accept-invite?token=${token}`, {
        method: "POST",
        credentials: "include",
      });
      
      if (response.ok) {
        toast.success("Invitation accepted!");
        navigate("/team");
        fetchTeams();
        auth.checkAuth();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to accept invite");
      }
    } catch (error) {
      toast.error("Failed to accept invitation");
    }
  };

  const updateMemberRole = async (memberId, newRole) => {
    try {
      const response = await fetch(`${API_URL}/api/teams/${currentTeam.team_id}/members/${memberId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ role: newRole }),
      });
      
      if (response.ok) {
        toast.success("Role updated");
        fetchMembers(currentTeam.team_id);
      }
    } catch (error) {
      toast.error("Failed to update role");
    }
  };

  const removeMember = async (memberId) => {
    if (!window.confirm("Remove this team member?")) return;
    
    try {
      const response = await fetch(`${API_URL}/api/teams/${currentTeam.team_id}/members/${memberId}`, {
        method: "DELETE",
        credentials: "include",
      });
      
      if (response.ok) {
        toast.success("Member removed");
        fetchMembers(currentTeam.team_id);
      }
    } catch (error) {
      toast.error("Failed to remove member");
    }
  };

  const updateTeamSettings = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const response = await fetch(`${API_URL}/api/teams/${currentTeam.team_id}/settings`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ brand_color: brandColor }),
      });
      
      if (response.ok) {
        const updated = await response.json();
        setCurrentTeam(updated);
        toast.success("Settings updated!");
        setSettingsDialogOpen(false);
      }
    } catch (error) {
      toast.error("Failed to update settings");
    } finally {
      setSubmitting(false);
    }
  };

  const uploadLogo = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch(`${API_URL}/api/teams/${currentTeam.team_id}/logo`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentTeam({ ...currentTeam, logo_url: data.logo_url });
        toast.success("Logo uploaded!");
      }
    } catch (error) {
      toast.error("Failed to upload logo");
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case "owner": return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "admin": return "bg-red-500/20 text-red-400 border-red-500/30";
      case "editor": return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      default: return "bg-white/10 text-white/60 border-white/10";
    }
  };

  // Check if user can manage team
  if (auth.user?.role !== "agency" && auth.user?.role !== "enterprise" && auth.user?.role !== "admin") {
    return (
      <DashboardLayout auth={auth}>
        <div className="flex items-center justify-center py-20">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 rounded-2xl bg-purple-500/20 flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-purple-400" />
            </div>
            <h2 className="font-display text-2xl font-bold text-white mb-2">Team Management</h2>
            <p className="text-white/60 mb-6">
              Team features are available on Agency and Enterprise plans. Upgrade to collaborate with your team.
            </p>
            <Button
              onClick={() => navigate("/billing")}
              className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              <Crown className="w-5 h-5 mr-2" />
              Upgrade Plan
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout auth={auth}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Team Management</h1>
            <p className="text-white/60 mt-1">Collaborate with your team and manage white-label settings</p>
          </div>
          <div className="flex items-center gap-3">
            {currentTeam && (
              <>
                <Dialog open={settingsDialogOpen} onOpenChange={setSettingsDialogOpen}>
                  <DialogTrigger asChild>
                    <Button variant="outline" className="h-11 bg-white/5 border-white/10 text-white hover:bg-white/10">
                      <Settings className="w-5 h-5 mr-2" />
                      Settings
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-md">
                    <DialogHeader>
                      <DialogTitle className="font-display text-xl">White-Label Settings</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={updateTeamSettings} className="space-y-5 mt-4">
                      <div>
                        <Label className="text-white/70 mb-2 block">Team Logo</Label>
                        <div className="flex items-center gap-4">
                          <Avatar className="w-16 h-16">
                            <AvatarImage src={currentTeam.logo_url} />
                            <AvatarFallback className="bg-indigo-500 text-white text-xl">
                              {currentTeam.name?.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                          <input
                            type="file"
                            accept="image/*"
                            ref={fileInputRef}
                            onChange={uploadLogo}
                            className="hidden"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => fileInputRef.current?.click()}
                            className="bg-white/5 border-white/10 text-white"
                          >
                            <Upload className="w-4 h-4 mr-2" />
                            Upload Logo
                          </Button>
                        </div>
                      </div>
                      <div>
                        <Label className="text-white/70 mb-2 block">Brand Color</Label>
                        <div className="flex items-center gap-3">
                          <input
                            type="color"
                            value={brandColor}
                            onChange={(e) => setBrandColor(e.target.value)}
                            className="w-12 h-12 rounded-lg cursor-pointer border-0"
                          />
                          <Input
                            value={brandColor}
                            onChange={(e) => setBrandColor(e.target.value)}
                            className="flex-1 h-12 bg-white/5 border-white/10 rounded-xl text-white"
                          />
                        </div>
                      </div>
                      <Button
                        type="submit"
                        disabled={submitting}
                        className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                      >
                        {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : "Save Settings"}
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
                
                <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)]">
                      <Plus className="w-5 h-5 mr-2" />
                      Invite Member
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-md">
                    <DialogHeader>
                      <DialogTitle className="font-display text-xl">Invite Team Member</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={inviteMember} className="space-y-5 mt-4">
                      <div>
                        <Label className="text-white/70 mb-2 block">Email Address</Label>
                        <Input
                          type="email"
                          placeholder="colleague@example.com"
                          value={inviteEmail}
                          onChange={(e) => setInviteEmail(e.target.value)}
                          className="h-12 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                          required
                        />
                      </div>
                      <div>
                        <Label className="text-white/70 mb-2 block">Role</Label>
                        <Select value={inviteRole} onValueChange={setInviteRole}>
                          <SelectTrigger className="h-12 bg-white/5 border-white/10 rounded-xl text-white">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-[#0F0F11] border-white/10">
                            <SelectItem value="viewer" className="text-white">Viewer - Can view only</SelectItem>
                            <SelectItem value="editor" className="text-white">Editor - Can create & edit</SelectItem>
                            <SelectItem value="admin" className="text-white">Admin - Full access</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <Button
                        type="submit"
                        disabled={submitting}
                        className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                      >
                        {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : "Send Invitation"}
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </>
            )}
            
            {teams.length === 0 && (
              <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="h-11 px-6 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium">
                    <Plus className="w-5 h-5 mr-2" />
                    Create Team
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-[#0F0F11] border-white/10 text-white max-w-md">
                  <DialogHeader>
                    <DialogTitle className="font-display text-xl">Create Your Team</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={createTeam} className="space-y-5 mt-4">
                    <div>
                      <Label className="text-white/70 mb-2 block">Team Name</Label>
                      <Input
                        placeholder="My Agency"
                        value={teamName}
                        onChange={(e) => setTeamName(e.target.value)}
                        className="h-12 bg-white/5 border-white/10 rounded-xl text-white placeholder:text-white/30"
                        required
                      />
                    </div>
                    <Button
                      type="submit"
                      disabled={submitting}
                      className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white"
                    >
                      {submitting ? <Loader2 className="w-5 h-5 animate-spin" /> : "Create Team"}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          </div>
        ) : teams.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white/30" />
            </div>
            <h3 className="font-display text-xl font-semibold text-white mb-2">No team yet</h3>
            <p className="text-white/50 mb-6">Create a team to collaborate with others and enable white-label features</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Team Info Card */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/20">
              <div className="flex items-center gap-4 mb-6">
                <Avatar className="w-16 h-16">
                  <AvatarImage src={currentTeam?.logo_url} />
                  <AvatarFallback className="bg-indigo-500 text-white text-2xl">
                    {currentTeam?.name?.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="font-display text-xl font-semibold text-white">{currentTeam?.name}</h3>
                  <p className="text-sm text-white/50">{members.length} team members</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <span className="text-sm text-white/60">Brand Color</span>
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-6 h-6 rounded-md" 
                      style={{ backgroundColor: currentTeam?.brand_color || "#6366F1" }}
                    />
                    <span className="text-sm text-white font-mono">{currentTeam?.brand_color || "#6366F1"}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                  <span className="text-sm text-white/60">White-label PDFs</span>
                  <CheckCircle className="w-5 h-5 text-green-400" />
                </div>
              </div>
            </div>

            {/* Members List */}
            <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5">
              <h3 className="font-display font-semibold text-white mb-4">Team Members</h3>
              <div className="space-y-3">
                {members.map((member) => (
                  <motion.div
                    key={member.member_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar className="w-10 h-10">
                        <AvatarFallback className="bg-indigo-500 text-white">
                          {member.name?.charAt(0) || member.email?.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium text-white">
                          {member.name || member.email}
                          {member.status === "pending" && (
                            <span className="ml-2 text-xs text-yellow-400">(Pending)</span>
                          )}
                        </p>
                        <p className="text-sm text-white/50">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className={getRoleBadgeColor(member.role)}>
                        {member.role}
                      </Badge>
                      {member.role !== "owner" && (
                        <Select
                          value={member.role}
                          onValueChange={(value) => updateMemberRole(member.member_id, value)}
                        >
                          <SelectTrigger className="w-28 h-9 bg-white/5 border-white/10 text-white text-sm">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent className="bg-[#0F0F11] border-white/10">
                            <SelectItem value="viewer" className="text-white">Viewer</SelectItem>
                            <SelectItem value="editor" className="text-white">Editor</SelectItem>
                            <SelectItem value="admin" className="text-white">Admin</SelectItem>
                          </SelectContent>
                        </Select>
                      )}
                      {member.role !== "owner" && (
                        <button
                          onClick={() => removeMember(member.member_id)}
                          className="p-2 text-red-400 hover:text-red-300 rounded-lg hover:bg-red-500/10"
                        >
                          <UserMinus className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default TeamPage;
