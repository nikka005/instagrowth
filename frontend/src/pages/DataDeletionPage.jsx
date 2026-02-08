import { useState } from "react";
import { motion } from "framer-motion";
import { Link, useSearchParams } from "react-router-dom";
import { Trash2, ArrowLeft, Instagram, AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { toast } from "sonner";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DataDeletionPage = () => {
  const [searchParams] = useSearchParams();
  const confirmationId = searchParams.get("id");
  
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [deletionId, setDeletionId] = useState(confirmationId);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/data-deletion-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to submit request");
      }

      const data = await response.json();
      setDeletionId(data.deletion_id);
      setSubmitted(true);
      toast.success("Data deletion request submitted");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030305]">
      {/* Header */}
      <header className="border-b border-white/5 bg-[#030305]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-white/60 hover:text-white">
            <ArrowLeft className="w-5 h-5" />
            Back to Home
          </Link>
          <div className="flex items-center gap-2">
            <Trash2 className="w-5 h-5 text-red-400" />
            <span className="text-white font-semibold">InstaGrowth OS</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="prose prose-invert max-w-none"
        >
          <h1 className="text-4xl font-bold text-white mb-2">Data Deletion</h1>
          <p className="text-white/50 mb-8">Instagram Data Deletion Callback & User Data Removal</p>

          {/* Meta/Instagram Required Notice */}
          <div className="bg-gradient-to-r from-pink-500/10 to-purple-500/10 border border-pink-500/30 rounded-xl p-6 mb-8">
            <div className="flex items-start gap-3">
              <Instagram className="w-6 h-6 text-pink-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-semibold text-white m-0">Instagram Data Deletion Callback</h3>
                <p className="text-white/70 mt-2 mb-0">
                  This page serves as the Data Deletion Callback URL required by Meta/Facebook for apps 
                  using Instagram API. When you disconnect your Instagram account or request data deletion 
                  from Facebook, we receive a callback and process your data deletion request.
                </p>
              </div>
            </div>
          </div>

          {/* Request Form or Confirmation */}
          {submitted || deletionId ? (
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-8 text-center mb-8">
              <CheckCircle2 className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-white mb-2">Request Received</h2>
              <p className="text-white/70 mb-4">
                Your data deletion request has been submitted successfully.
              </p>
              <div className="bg-black/20 rounded-lg p-4 inline-block">
                <p className="text-white/50 text-sm mb-1">Confirmation ID:</p>
                <p className="text-xl font-mono text-green-400">{deletionId}</p>
              </div>
              <p className="text-white/50 text-sm mt-4">
                Please save this ID for your records. Your data will be deleted within 30 days.
              </p>
            </div>
          ) : (
            <div className="bg-[#0F0F11] border border-white/10 rounded-xl p-8 mb-8">
              <h2 className="text-2xl font-semibold text-white mb-4">Request Data Deletion</h2>
              <p className="text-white/60 mb-6">
                Enter your email address to request deletion of all your data from InstaGrowth OS.
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  type="email"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-12 bg-white/5 border-white/10 rounded-xl text-white"
                  required
                />
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 bg-red-500 hover:bg-red-600 text-white rounded-xl"
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Trash2 className="w-5 h-5 mr-2" />
                      Request Data Deletion
                    </>
                  )}
                </Button>
              </form>
            </div>
          )}

          <div className="space-y-8 text-white/80">
            <section>
              <h2 className="text-2xl font-semibold text-white">What Data We Delete</h2>
              <p>When you request data deletion, we remove:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Account Information:</strong> Email, name, profile settings</li>
                <li><strong>Instagram Data:</strong> Connected accounts, access tokens, analytics data</li>
                <li><strong>Content:</strong> AI-generated audits, content suggestions, growth plans</li>
                <li><strong>Usage History:</strong> Feature usage, AI request logs</li>
                <li><strong>Team Data:</strong> Team memberships and associated permissions</li>
                <li><strong>Payment History:</strong> Subscription records (anonymized for legal compliance)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">Deletion Process</h2>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Submit a data deletion request using the form above</li>
                <li>Receive a confirmation ID for your records</li>
                <li>We verify the request and begin processing</li>
                <li>All data is permanently deleted within 30 days</li>
                <li>You will receive a confirmation email once complete</li>
              </ol>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">Data We Retain</h2>
              <p>For legal and compliance purposes, we may retain:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Anonymized analytics (cannot be linked back to you)</li>
                <li>Transaction records required for tax compliance (7 years)</li>
                <li>Legal correspondence and dispute records</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">Instagram Data Callback</h2>
              <p>
                As required by Meta Platform Policy, we support automated data deletion callbacks. 
                When you remove our app from your Facebook/Instagram settings:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Meta sends us a signed deletion request</li>
                <li>We verify the request authenticity</li>
                <li>Your Instagram-related data is queued for deletion</li>
                <li>Data is permanently removed within 30 days</li>
                <li>A confirmation URL is provided to Meta</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">How to Disconnect Instagram</h2>
              <p>You can disconnect your Instagram account at any time:</p>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Log in to InstaGrowth OS</li>
                <li>Go to Settings → Accounts</li>
                <li>Click "Disconnect" on the Instagram account</li>
                <li>Your Instagram access token is immediately revoked</li>
              </ol>
              <p className="mt-4">
                Alternatively, you can revoke access from Facebook:
              </p>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Go to Facebook Settings → Security & Login → Apps and Websites</li>
                <li>Find InstaGrowth OS and click "Remove"</li>
                <li>This triggers our data deletion callback automatically</li>
              </ol>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">Verification</h2>
              <p>
                To check the status of your data deletion request, use your Confirmation ID 
                and contact us at:
              </p>
              <p className="mt-2">
                <strong>Email:</strong> privacy@instagrowth.com<br />
                <strong>Subject:</strong> Data Deletion Status - [Your Confirmation ID]
              </p>
            </section>

            {/* Warning Box */}
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-amber-400 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-semibold text-amber-400 m-0">Important Notice</h3>
                  <p className="text-amber-400/80 mt-2 mb-0">
                    Data deletion is permanent and cannot be undone. Make sure to export any data 
                    you wish to keep before submitting a deletion request. If you have an active 
                    subscription, please cancel it first to avoid being charged after data deletion.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10">
            <div className="flex gap-4 text-sm">
              <Link to="/privacy" className="text-indigo-400 hover:text-indigo-300">Privacy Policy</Link>
              <Link to="/terms" className="text-indigo-400 hover:text-indigo-300">Terms of Service</Link>
              <Link to="/refund" className="text-indigo-400 hover:text-indigo-300">Refund Policy</Link>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default DataDeletionPage;
