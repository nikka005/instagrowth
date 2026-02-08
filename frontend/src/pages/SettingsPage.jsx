import { useState } from "react";
import { motion } from "framer-motion";
import { 
  User, Mail, Lock, Bell, Shield, Palette, 
  Save, Loader2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";
import DashboardLayout from "../components/DashboardLayout";
import TwoFactorSettings from "../components/TwoFactorSettings";
import { toast } from "sonner";

const SettingsPage = ({ auth }) => {
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState({
    name: auth.user?.name || "",
    email: auth.user?.email || "",
  });
  const [notifications, setNotifications] = useState({
    email: true,
    marketing: false,
    updates: true,
  });

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      toast.success("Profile updated successfully!");
      setLoading(false);
    }, 1000);
  };

  return (
    <DashboardLayout auth={auth}>
      <div className="max-w-4xl space-y-6">
        {/* Header */}
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-white">Settings</h1>
          <p className="text-white/60 mt-1">Manage your account preferences</p>
        </div>

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="bg-[#0F0F11]/80 border border-white/5 p-1 rounded-xl">
            <TabsTrigger value="profile" className="flex items-center gap-2 data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-400 rounded-lg px-4 py-2">
              <User className="w-4 h-4" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2 data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-400 rounded-lg px-4 py-2">
              <Bell className="w-4 h-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2 data-[state=active]:bg-indigo-500/20 data-[state=active]:text-indigo-400 rounded-lg px-4 py-2">
              <Shield className="w-4 h-4" />
              Security
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
            >
              <h3 className="font-display text-lg font-semibold text-white mb-6">Profile Information</h3>
              
              <div className="flex items-center gap-6 mb-8">
                <Avatar className="w-20 h-20">
                  <AvatarImage src={auth.user?.picture} />
                  <AvatarFallback className="bg-indigo-500 text-white text-2xl">
                    {auth.user?.name?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h4 className="font-medium text-white">{auth.user?.name}</h4>
                  <p className="text-sm text-white/50">{auth.user?.email}</p>
                  <p className="text-sm text-indigo-400 capitalize mt-1">{auth.user?.role} Plan</p>
                </div>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <Label className="text-white/70 mb-2 block">Full Name</Label>
                    <div className="relative">
                      <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                      <Input
                        value={profileData.name}
                        onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                        className="h-12 pl-12 bg-white/5 border-white/10 rounded-xl text-white"
                        data-testid="settings-name-input"
                      />
                    </div>
                  </div>
                  <div>
                    <Label className="text-white/70 mb-2 block">Email Address</Label>
                    <div className="relative">
                      <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                      <Input
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                        className="h-12 pl-12 bg-white/5 border-white/10 rounded-xl text-white"
                        disabled
                        data-testid="settings-email-input"
                      />
                    </div>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="h-11 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium"
                  data-testid="settings-save-btn"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Save className="w-5 h-5 mr-2" />}
                  Save Changes
                </Button>
              </form>
            </motion.div>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
            >
              <h3 className="font-display text-lg font-semibold text-white mb-6">Notification Preferences</h3>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                  <div>
                    <h4 className="font-medium text-white">Email Notifications</h4>
                    <p className="text-sm text-white/50">Receive audit reports and content ideas via email</p>
                  </div>
                  <Switch
                    checked={notifications.email}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, email: checked })}
                  />
                </div>

                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                  <div>
                    <h4 className="font-medium text-white">Marketing Emails</h4>
                    <p className="text-sm text-white/50">Receive tips, tutorials, and promotional content</p>
                  </div>
                  <Switch
                    checked={notifications.marketing}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, marketing: checked })}
                  />
                </div>

                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                  <div>
                    <h4 className="font-medium text-white">Product Updates</h4>
                    <p className="text-sm text-white/50">Be notified about new features and improvements</p>
                  </div>
                  <Switch
                    checked={notifications.updates}
                    onCheckedChange={(checked) => setNotifications({ ...notifications, updates: checked })}
                  />
                </div>
              </div>
            </motion.div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
            >
              <h3 className="font-display text-lg font-semibold text-white mb-6">Security Settings</h3>
              
              <div className="space-y-6">
                <div className="p-4 rounded-xl bg-white/5 border border-white/5">
                  <h4 className="font-medium text-white mb-4">Change Password</h4>
                  <div className="space-y-4">
                    <div>
                      <Label className="text-white/70 mb-2 block">Current Password</Label>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                        <Input
                          type="password"
                          placeholder="••••••••"
                          className="h-12 pl-12 bg-white/5 border-white/10 rounded-xl text-white"
                        />
                      </div>
                    </div>
                    <div>
                      <Label className="text-white/70 mb-2 block">New Password</Label>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                        <Input
                          type="password"
                          placeholder="••••••••"
                          className="h-12 pl-12 bg-white/5 border-white/10 rounded-xl text-white"
                        />
                      </div>
                    </div>
                    <Button className="h-11 px-6 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white">
                      Update Password
                    </Button>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                  <h4 className="font-medium text-red-400 mb-2">Danger Zone</h4>
                  <p className="text-sm text-white/60 mb-4">
                    Once you delete your account, there is no going back. Please be certain.
                  </p>
                  <Button variant="destructive" className="h-11 px-6 rounded-xl">
                    Delete Account
                  </Button>
                </div>
              </div>
            </motion.div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;
