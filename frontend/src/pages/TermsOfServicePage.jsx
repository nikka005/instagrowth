import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { FileText, ArrowLeft } from "lucide-react";

const TermsOfServicePage = () => {
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
            <FileText className="w-5 h-5 text-indigo-400" />
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
          <h1 className="text-4xl font-bold text-white mb-2">Terms of Service</h1>
          <p className="text-white/50 mb-8">Last updated: February 8, 2025</p>

          <div className="space-y-8 text-white/80">
            <section>
              <h2 className="text-2xl font-semibold text-white">1. Acceptance of Terms</h2>
              <p>
                By accessing or using InstaGrowth OS ("Service"), you agree to be bound by these Terms of Service. 
                If you do not agree to these terms, please do not use our Service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">2. Description of Service</h2>
              <p>
                InstaGrowth OS is an AI-powered Instagram growth and management platform that provides:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Instagram account analytics and audits</li>
                <li>AI-generated content suggestions</li>
                <li>Growth planning and strategy recommendations</li>
                <li>DM templates and competitor analysis</li>
                <li>A/B testing tools</li>
                <li>Team collaboration features</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">3. Account Registration</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>You must be at least 13 years old to use this Service</li>
                <li>You must provide accurate and complete information</li>
                <li>You are responsible for maintaining account security</li>
                <li>You must not share your account credentials</li>
                <li>One person may not maintain multiple free accounts</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">4. Instagram Integration</h2>
              <p>
                When connecting your Instagram account:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>You authorize us to access your Instagram data via Meta's official API</li>
                <li>You must comply with Instagram's Terms of Use</li>
                <li>We are not responsible for Instagram's service availability</li>
                <li>You may disconnect your Instagram account at any time</li>
                <li>We do not store your Instagram password</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">5. Subscription Plans</h2>
              <h3 className="text-xl font-medium text-white/90">5.1 Billing</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Subscriptions are billed monthly or annually in advance</li>
                <li>Prices are in USD unless otherwise stated</li>
                <li>You authorize us to charge your payment method automatically</li>
              </ul>
              
              <h3 className="text-xl font-medium text-white/90 mt-4">5.2 Plan Limits</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Each plan has specific limits on accounts, AI usage, and team members</li>
                <li>Exceeding limits may result in service restrictions</li>
                <li>Unused credits do not roll over to the next billing period</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">6. Acceptable Use</h2>
              <p>You agree NOT to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Violate Instagram's Terms of Service or Community Guidelines</li>
                <li>Use the Service for spam, harassment, or illegal activities</li>
                <li>Attempt to reverse engineer or exploit the Service</li>
                <li>Share or resell access to your account</li>
                <li>Use automated tools to access the Service (except our official API)</li>
                <li>Upload malicious content or code</li>
                <li>Impersonate others or misrepresent your affiliation</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">7. AI-Generated Content</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>AI suggestions are for guidance only; you are responsible for content you post</li>
                <li>We do not guarantee accuracy or effectiveness of AI recommendations</li>
                <li>You retain rights to content you create using our tools</li>
                <li>We may use anonymized data to improve our AI models</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">8. Intellectual Property</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>The Service, including all software and content, is owned by InstaGrowth OS</li>
                <li>You are granted a limited, non-exclusive license to use the Service</li>
                <li>Our trademarks and branding may not be used without permission</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">9. Limitation of Liability</h2>
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>The Service is provided "AS IS" without warranties</li>
                <li>We are not liable for indirect, incidental, or consequential damages</li>
                <li>Our total liability shall not exceed the amount you paid in the last 12 months</li>
                <li>We are not responsible for third-party services (Instagram, Stripe, etc.)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">10. Termination</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>You may cancel your subscription at any time</li>
                <li>We may suspend or terminate accounts that violate these terms</li>
                <li>Upon termination, your access ends immediately</li>
                <li>Data deletion follows our Privacy Policy</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">11. Changes to Terms</h2>
              <p>
                We may modify these terms at any time. Continued use of the Service after 
                changes constitutes acceptance. Material changes will be notified via email.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">12. Governing Law</h2>
              <p>
                These terms are governed by applicable laws. Disputes shall be resolved 
                through binding arbitration, except where prohibited by law.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">13. Contact</h2>
              <p>
                For questions about these terms, contact us at:
              </p>
              <p className="mt-2">
                <strong>Email:</strong> legal@instagrowth.com
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10">
            <div className="flex gap-4 text-sm">
              <Link to="/privacy" className="text-indigo-400 hover:text-indigo-300">Privacy Policy</Link>
              <Link to="/refund" className="text-indigo-400 hover:text-indigo-300">Refund Policy</Link>
              <Link to="/data-deletion" className="text-indigo-400 hover:text-indigo-300">Data Deletion</Link>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default TermsOfServicePage;
