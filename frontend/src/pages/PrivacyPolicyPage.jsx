import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Shield, ArrowLeft } from "lucide-react";

const PrivacyPolicyPage = () => {
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
            <Shield className="w-5 h-5 text-indigo-400" />
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
          <h1 className="text-4xl font-bold text-white mb-2">Privacy Policy</h1>
          <p className="text-white/50 mb-8">Last updated: February 8, 2025</p>

          <div className="space-y-8 text-white/80">
            <section>
              <h2 className="text-2xl font-semibold text-white">1. Introduction</h2>
              <p>
                InstaGrowth OS ("we", "our", or "us") respects your privacy and is committed to protecting your personal data. 
                This privacy policy explains how we collect, use, and safeguard your information when you use our Instagram growth 
                and management platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">2. Information We Collect</h2>
              <h3 className="text-xl font-medium text-white/90">2.1 Personal Information</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Name and email address (required for account creation)</li>
                <li>Payment information (processed securely via Stripe)</li>
                <li>Profile information you provide</li>
              </ul>
              
              <h3 className="text-xl font-medium text-white/90 mt-4">2.2 Instagram Data</h3>
              <p>When you connect your Instagram account, we access:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Public profile information (username, profile picture, bio)</li>
                <li>Follower and following counts</li>
                <li>Media content and engagement metrics</li>
                <li>Insights data (for Business/Creator accounts)</li>
              </ul>

              <h3 className="text-xl font-medium text-white/90 mt-4">2.3 Usage Data</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Log data (IP address, browser type, pages visited)</li>
                <li>Feature usage patterns</li>
                <li>AI-generated content history</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">3. How We Use Your Information</h2>
              <ul className="list-disc pl-6 space-y-2">
                <li>Provide and maintain our services</li>
                <li>Generate AI-powered audits, content suggestions, and growth plans</li>
                <li>Process payments and manage subscriptions</li>
                <li>Send transactional emails (verification, receipts, updates)</li>
                <li>Improve our services and develop new features</li>
                <li>Detect and prevent fraud or abuse</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">4. Data Sharing</h2>
              <p>We do not sell your personal data. We may share data with:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li><strong>Service Providers:</strong> Stripe (payments), Resend (emails), OpenAI (AI processing)</li>
                <li><strong>Meta/Instagram:</strong> Only to facilitate features you request</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">5. Data Security</h2>
              <p>
                We implement industry-standard security measures including:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>SSL/TLS encryption for all data transmission</li>
                <li>Encrypted storage for sensitive data</li>
                <li>Regular security audits</li>
                <li>Two-factor authentication option</li>
                <li>Access controls and monitoring</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">6. Data Retention</h2>
              <p>
                We retain your data for as long as your account is active. Upon account deletion:
              </p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Personal data is deleted within 30 days</li>
                <li>Anonymized analytics may be retained</li>
                <li>Legal/compliance records retained as required by law</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">7. Your Rights</h2>
              <p>You have the right to:</p>
              <ul className="list-disc pl-6 space-y-2">
                <li>Access your personal data</li>
                <li>Correct inaccurate data</li>
                <li>Delete your account and data</li>
                <li>Export your data</li>
                <li>Withdraw consent for data processing</li>
                <li>Disconnect your Instagram account at any time</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">8. Cookies</h2>
              <p>
                We use essential cookies for authentication and session management. 
                No third-party tracking cookies are used without consent.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">9. Children's Privacy</h2>
              <p>
                Our service is not intended for users under 13 years of age. 
                We do not knowingly collect data from children.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">10. Changes to This Policy</h2>
              <p>
                We may update this policy periodically. We will notify you of significant 
                changes via email or in-app notification.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-white">11. Contact Us</h2>
              <p>
                For privacy-related inquiries, contact us at:
              </p>
              <p className="mt-2">
                <strong>Email:</strong> privacy@instagrowth.com<br />
                <strong>Address:</strong> InstaGrowth OS Privacy Team
              </p>
            </section>
          </div>

          <div className="mt-12 pt-8 border-t border-white/10">
            <div className="flex gap-4 text-sm">
              <Link to="/terms" className="text-indigo-400 hover:text-indigo-300">Terms of Service</Link>
              <Link to="/refund" className="text-indigo-400 hover:text-indigo-300">Refund Policy</Link>
              <Link to="/data-deletion" className="text-indigo-400 hover:text-indigo-300">Data Deletion</Link>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default PrivacyPolicyPage;
