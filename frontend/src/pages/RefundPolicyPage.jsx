import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { CreditCard, ArrowLeft, CheckCircle2 } from "lucide-react";

const RefundPolicyPage = () => {
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
            <CreditCard className="w-5 h-5 text-indigo-400" />
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
          <h1 className="text-4xl font-bold text-white mb-2">Refund Policy</h1>
          <p className="text-white/50 mb-8">Last updated: February 8, 2025</p>

          {/* Highlight Box */}
          <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-6 mb-8">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-6 h-6 text-indigo-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-semibold text-white m-0">7-Day Money-Back Guarantee</h3>
                <p className="text-white/70 mt-2 mb-0">
                  We offer a 7-day money-back guarantee on all new subscriptions. 
                  If you're not satisfied, request a full refund within 7 days of your first payment.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-8 text-white/80">
            <section>
              <h2 className="text-2xl font-semibold text-white">1. Eligibility for Refunds</h2>
              
              <h3 className="text-xl font-medium text-white/90">1.1 Full Refunds</h3>
              <p>You are eligible for a full refund if:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>You request a refund within 7 days of your first subscription payment</li>
                <li>You experience a technical issue that prevents you from using the Service, and we cannot resolve it within 48 hours</li>
                <li>We discontinue a major feature that was essential to your subscription</li>
              </ul>

              <h3 className="text-xl font-medium text-white/90 mt-4">1.2 Partial Refunds</h3>
              <p>We may offer partial refunds (prorated) for:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Annual subscriptions cancelled after the 7-day period</li>
                <li>Billing errors where you were charged incorrectly</li>
                <li>Extended service outages (more than 24 hours)</li>
              </ul>

              <h3 className="text-xl font-medium text-white/90 mt-4">1.3 No Refunds</h3>
              <p>Refunds are NOT provided for:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Monthly subscriptions after the 7-day guarantee period</li>
                <li>Change of mind after using AI credits or features</li>
                <li>Account termination due to Terms of Service violations</li>
                <li>Failure to cancel before renewal date</li>
                <li>Dissatisfaction with AI-generated content quality</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">2. How to Request a Refund</h2>
              <p>To request a refund:</p>
              <ol className="list-decimal pl-6 space-y-2">
                <li>Email us at <strong>billing@instagrowth.com</strong> with subject line "Refund Request"</li>
                <li>Include your account email address</li>
                <li>Provide the reason for your refund request</li>
                <li>Include any relevant transaction IDs or receipts</li>
              </ol>
              <p className="mt-4">
                We aim to respond to all refund requests within 2 business days.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">3. Refund Processing</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>Approved refunds are processed within 5-10 business days</li>
                <li>Refunds are issued to the original payment method</li>
                <li>Bank processing times may vary (additional 3-5 days)</li>
                <li>Refund amounts are in the original currency of payment</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">4. Subscription Cancellation</h2>
              <p>
                Cancelling your subscription is different from requesting a refund:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>You can cancel your subscription at any time from Settings → Billing</li>
                <li>Upon cancellation, you retain access until the end of your billing period</li>
                <li>No automatic refund is issued for cancellations</li>
                <li>Your data will be retained for 30 days after subscription ends</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">5. Chargebacks</h2>
              <p>
                Before filing a chargeback with your bank, please contact us first. 
                Chargebacks may result in:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Immediate account suspension</li>
                <li>Additional fees that cannot be recovered</li>
                <li>Inability to create new accounts</li>
              </ul>
              <p className="mt-2">
                We're committed to resolving disputes directly and fairly.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">6. Special Circumstances</h2>
              <p>
                We consider refunds on a case-by-case basis for:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Medical emergencies (with documentation)</li>
                <li>Duplicate payments made in error</li>
                <li>Service issues specific to your account</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">7. Contact Us</h2>
              <p>
                For refund inquiries:
              </p>
              <p className="mt-2">
                <strong>Email:</strong> billing@instagrowth.com<br />
                <strong>Response Time:</strong> Within 2 business days
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10">
            <div className="flex gap-4 text-sm">
              <Link to="/privacy" className="text-indigo-400 hover:text-indigo-300">Privacy Policy</Link>
              <Link to="/terms" className="text-indigo-400 hover:text-indigo-300">Terms of Service</Link>
              <Link to="/data-deletion" className="text-indigo-400 hover:text-indigo-300">Data Deletion</Link>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default RefundPolicyPage;
