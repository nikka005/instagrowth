import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Zap, BarChart3, MessageSquare, Calendar, Users, Shield, 
  ChevronRight, Check, Star, ArrowRight, Instagram, TrendingUp,
  Sparkles, Target, FileText, Rocket
} from "lucide-react";
import { Button } from "../components/ui/button";

const LandingPage = () => {
  const [hoveredPlan, setHoveredPlan] = useState(null);

  const features = [
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "AI Account Audit",
      description: "Get instant shadowban checks, engagement diagnosis, and a 30-day recovery roadmap.",
      color: "from-indigo-500 to-purple-500"
    },
    {
      icon: <Sparkles className="w-6 h-6" />,
      title: "AI Content Engine",
      description: "Generate viral reel ideas, scroll-stopping hooks, and optimized hashtag clusters.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "DM & Reply Templates",
      description: "Human-tone auto DM replies with lead qualification and spam-safe delays.",
      color: "from-teal-500 to-cyan-500"
    },
    {
      icon: <Calendar className="w-6 h-6" />,
      title: "Growth Planner",
      description: "7/14/30 day plans with client-ready roadmaps and white-label PDF exports.",
      color: "from-orange-500 to-red-500"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Multi-Account Support",
      description: "Manage 1-50 accounts with separate analytics and performance reports.",
      color: "from-green-500 to-teal-500"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Agency Dashboard",
      description: "Team access, client notes, and branded exports for professional agencies.",
      color: "from-blue-500 to-indigo-500"
    }
  ];

  const plans = [
    {
      name: "Starter",
      price: 19,
      description: "Perfect for individuals",
      features: ["1 Instagram account", "10 AI generations/month", "Basic audit reports", "Email support"],
      popular: false,
      color: "border-white/10"
    },
    {
      name: "Pro",
      price: 49,
      description: "Best for freelancers",
      features: ["5 Instagram accounts", "100 AI generations/month", "PDF export", "Growth planner", "Priority support"],
      popular: true,
      color: "border-indigo-500"
    },
    {
      name: "Agency",
      price: 149,
      description: "For growing agencies",
      features: ["25 Instagram accounts", "500 AI generations/month", "White-label PDFs", "Team access", "Dedicated support"],
      popular: false,
      color: "border-white/10"
    },
    {
      name: "Enterprise",
      price: 299,
      description: "For large agencies",
      features: ["100 Instagram accounts", "2000 AI generations/month", "API access", "Custom branding", "24/7 support"],
      popular: false,
      color: "border-white/10"
    }
  ];

  const testimonials = [
    {
      name: "Sarah M.",
      role: "SMMA Owner",
      text: "InstaGrowth OS cut our client onboarding time in half. The AI audits are incredibly accurate.",
      avatar: "S"
    },
    {
      name: "Mike R.",
      role: "Freelance SMM",
      text: "The content engine saves me 10+ hours per week. My clients' engagement has doubled.",
      avatar: "M"
    },
    {
      name: "Jessica L.",
      role: "Influencer Coach",
      text: "Finally, a tool that actually understands Instagram growth. The roadmaps are game-changing.",
      avatar: "J"
    }
  ];

  return (
    <div className="min-h-screen bg-[#030305] text-white overflow-hidden">
      {/* Navigation */}
      <nav className="fixed top-4 left-1/2 -translate-x-1/2 w-[95%] max-w-5xl z-50 h-14 rounded-full bg-black/50 backdrop-blur-md border border-white/10 px-6 flex items-center justify-between shadow-2xl">
        <Link to="/" className="flex items-center gap-2" data-testid="nav-logo">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
            <Instagram className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-lg">InstaGrowth OS</span>
        </Link>
        <div className="hidden md:flex items-center gap-6">
          <a href="#features" className="text-sm text-white/70 hover:text-white transition-colors">Features</a>
          <a href="#pricing" className="text-sm text-white/70 hover:text-white transition-colors">Pricing</a>
          <a href="#testimonials" className="text-sm text-white/70 hover:text-white transition-colors">Testimonials</a>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" className="text-white/70 hover:text-white" data-testid="nav-login-btn">
              Login
            </Button>
          </Link>
          <Link to="/register">
            <Button className="h-9 px-4 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] transition-all" data-testid="nav-signup-btn">
              Get Started
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        {/* Background gradient */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-radial from-indigo-500/20 via-purple-500/10 to-transparent blur-3xl"></div>
        </div>

        <div className="max-w-6xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
              <Zap className="w-4 h-4 text-indigo-400" />
              <span className="text-sm text-white/70">AI-Powered Instagram Growth Platform</span>
            </div>
            
            <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
              <span className="text-gradient">Scale Your Instagram</span>
              <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
                Growth Agency
              </span>
            </h1>
            
            <p className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto mb-10 leading-relaxed">
              The all-in-one AI engine that runs Instagram growth accounts like a pro. 
              Audits, content, DM automation, and growth planning — all in one place.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register">
                <Button className="h-12 px-8 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-lg shadow-[0_0_30px_rgba(99,102,241,0.4)] hover:shadow-[0_0_50px_rgba(99,102,241,0.6)] transition-all" data-testid="hero-cta-btn">
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <a href="#features">
                <Button variant="outline" className="h-12 px-8 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium" data-testid="hero-features-btn">
                  See Features
                </Button>
              </a>
            </div>

            {/* Stats */}
            <div className="flex flex-wrap justify-center gap-8 mt-16">
              {[
                { value: "10K+", label: "Active Users" },
                { value: "500K+", label: "Audits Generated" },
                { value: "98%", label: "Satisfaction Rate" }
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl font-display font-bold text-white">{stat.value}</div>
                  <div className="text-sm text-white/50">{stat.label}</div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-20 relative"
          >
            <div className="absolute inset-0 bg-gradient-to-t from-[#030305] via-transparent to-transparent z-10 pointer-events-none"></div>
            <div className="rounded-2xl overflow-hidden border border-white/10 shadow-2xl shadow-indigo-500/10">
              <img 
                src="https://images.unsplash.com/photo-1704643770744-154e115d454d?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200"
                alt="Dashboard Preview"
                className="w-full object-cover opacity-80"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Everything You Need to <span className="text-gradient-primary">Dominate Instagram</span>
            </h2>
            <p className="text-lg text-white/60 max-w-2xl mx-auto">
              Powerful AI tools designed specifically for Instagram growth agencies and freelancers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group relative p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5 hover:border-indigo-500/50 transition-all duration-300"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="font-display text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-white/60 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-24 px-6 relative">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/2 left-1/4 w-[600px] h-[600px] bg-gradient-radial from-purple-500/10 to-transparent blur-3xl"></div>
        </div>

        <div className="max-w-6xl mx-auto relative">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Simple, <span className="text-gradient-primary">Transparent Pricing</span>
            </h2>
            <p className="text-lg text-white/60 max-w-2xl mx-auto">
              Choose the plan that fits your agency size. All plans include a 7-day free trial.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {plans.map((plan, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                onMouseEnter={() => setHoveredPlan(index)}
                onMouseLeave={() => setHoveredPlan(null)}
                className={`relative p-6 rounded-2xl bg-[#0F0F11]/80 border ${plan.popular ? 'border-indigo-500' : 'border-white/5'} transition-all duration-300 ${hoveredPlan === index ? 'transform -translate-y-2' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-indigo-600 text-xs font-medium">
                    Most Popular
                  </div>
                )}
                <div className="mb-4">
                  <h3 className="font-display text-xl font-semibold">{plan.name}</h3>
                  <p className="text-sm text-white/50">{plan.description}</p>
                </div>
                <div className="mb-6">
                  <span className="text-4xl font-display font-bold">${plan.price}</span>
                  <span className="text-white/50">/month</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-white/70">
                      <Check className="w-4 h-4 text-indigo-400" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/register" className="block">
                  <Button 
                    className={`w-full h-11 rounded-full font-medium transition-all ${plan.popular ? 'bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_20px_rgba(99,102,241,0.3)]' : 'bg-white/5 hover:bg-white/10 border border-white/10'}`}
                    data-testid={`pricing-${plan.name.toLowerCase()}-btn`}
                  >
                    Get Started
                  </Button>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-display text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Loved by <span className="text-gradient-primary">Growth Agencies</span>
            </h2>
            <p className="text-lg text-white/60 max-w-2xl mx-auto">
              Join thousands of agencies already scaling their Instagram operations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-2xl bg-[#0F0F11]/80 border border-white/5"
              >
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-white/70 mb-6 leading-relaxed">"{testimonial.text}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center font-medium">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-medium">{testimonial.name}</div>
                    <div className="text-sm text-white/50">{testimonial.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="relative p-12 rounded-3xl bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 text-center overflow-hidden">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYgMi42ODYgNiA2cy0yLjY4NiA2LTYgNi02LTIuNjg2LTYtNiAyLjY4Ni02IDYtNiIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiIHN0cm9rZS13aWR0aD0iMiIvPjwvZz48L3N2Zz4=')] opacity-20"></div>
            <div className="relative">
              <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">
                Ready to Scale Your Instagram Agency?
              </h2>
              <p className="text-lg text-white/70 mb-8 max-w-xl mx-auto">
                Start your 7-day free trial today. No credit card required.
              </p>
              <Link to="/register">
                <Button className="h-12 px-8 rounded-full bg-white text-indigo-600 hover:bg-white/90 font-medium text-lg shadow-[0_0_30px_rgba(255,255,255,0.2)] transition-all" data-testid="cta-start-btn">
                  Get Started Free
                  <Rocket className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                <Instagram className="w-5 h-5 text-white" />
              </div>
              <span className="font-display font-bold text-lg">InstaGrowth OS</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-white/50">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
            <div className="text-sm text-white/30">
              © 2024 InstaGrowth OS. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
