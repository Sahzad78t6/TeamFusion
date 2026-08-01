import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Zap,
  Sparkles,
  ArrowRight,
  Brain,
  Compass,
  CheckCircle2,
  Shield,
  Layers,
  Star,
  Globe,
  Activity,
  Award,
  ChevronRight,
  Play,
  Sun,
  Moon,
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { ParticleCanvas } from '../../components/common/ParticleCanvas';
import { CustomCursor } from '../../components/common/CustomCursor';
import { TiltCard } from '../../components/common/TiltCard';

export const Landing: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [typedText, setTypedText] = useState('');
  const fullText = 'The AI That Curates Your Future.';

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      setTypedText(fullText.slice(0, index + 1));
      index++;
      if (index > fullText.length) clearInterval(timer);
    }, 70);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#090a0f] text-slate-100 selection:bg-purple-500 selection:text-white overflow-x-hidden font-sans relative transition-colors duration-300">
      {/* WebGL / Canvas Particle Mesh Background */}
      <ParticleCanvas />

      {/* Custom Glowing Cursor Follower */}
      <CustomCursor />

      {/* Background Animated Gradient Blobs */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-purple-600/15 rounded-full blur-[140px] animate-pulse-slow" />
        <div className="absolute top-1/3 -right-40 w-[550px] h-[550px] bg-indigo-600/15 rounded-full blur-[140px] animate-pulse-slow" />
        <div className="absolute -bottom-40 left-1/3 w-[650px] h-[650px] bg-pink-600/10 rounded-full blur-[160px]" />
      </div>

      {/* Top Navbar */}
      <nav className="sticky top-0 z-40 flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#090a0f]/80 backdrop-blur-xl max-w-7xl mx-auto rounded-b-2xl mt-2 transition-colors">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
            <Zap className="w-5 h-5 text-white animate-pulse" />
          </div>
          <span className="font-extrabold text-xl tracking-tight text-white">
            Growth<span className="text-gradient">OS</span>
          </span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a>
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
          <a href="#pricing" className="hover:text-white transition-colors">Pricing</a>
        </div>

        <div className="flex items-center gap-3">
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2 text-slate-400 hover:text-white rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-indigo-400" />}
          </button>

          <NavLink to="/login">
            <Button variant="ghost" size="sm">Sign In</Button>
          </NavLink>
          <NavLink to="/onboarding">
            <Button variant="glow" size="sm" rightIcon={<ArrowRight className="w-4 h-4" />}>
              Launch GrowthOS
            </Button>
          </NavLink>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-24 px-6 max-w-6xl mx-auto text-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-6 shadow-glow-purple"
        >
          <Sparkles className="w-4 h-4 text-amber-300 fill-amber-300" />
          <span>Announcing GrowthOS 2.0 Agentic Architecture</span>
        </motion.div>

        <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mx-auto">
          We don't optimize for attention.{' '}
          <span className="text-gradient block mt-2">We optimize for human potential.</span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto font-normal h-8">
          {typedText}
          <span className="animate-pulse">|</span>
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <NavLink to="/onboarding">
            <Button size="lg" variant="glow" rightIcon={<ArrowRight className="w-5 h-5" />}>
              Create Your Identity Twin
            </Button>
          </NavLink>
          <NavLink to="/dashboard">
            <Button size="lg" variant="secondary" leftIcon={<Play className="w-4 h-4 text-purple-400 fill-purple-400" />}>
              Explore Live Demo Dashboard
            </Button>
          </NavLink>
        </div>

        {/* Hero Interactive Mockup Preview */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mt-16 relative rounded-3xl border border-white/15 bg-slate-900/70 p-3 shadow-2xl shadow-purple-950/60 backdrop-blur-2xl overflow-hidden group hover:border-purple-500/40 transition-colors"
        >
          <div className="absolute top-0 left-0 right-0 h-10 bg-white/5 border-b border-white/10 flex items-center px-4 gap-2">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            <span className="mx-auto text-xs text-slate-400 font-mono">app.growthos.ai/dashboard</span>
          </div>

          <div className="pt-10 pb-4 px-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            {/* Widget 1 */}
            <TiltCard className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-purple-400">Identity Alignment</span>
                <Badge variant="purple">88% Match</Badge>
              </div>
              <p className="text-2xl font-extrabold text-white">Founder Archetype</p>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-purple-500 to-indigo-500 h-full w-[88%]" />
              </div>
              <span className="text-[11px] text-slate-400">Identity drift reduced by 12% this week.</span>
            </TiltCard>

            {/* Widget 2 */}
            <TiltCard className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">Growth Score</span>
                <Badge variant="cyan">+14% MoM</Badge>
              </div>
              <p className="text-2xl font-extrabold text-white">92 / 100</p>
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Burnout Risk: 14% (Low)</span>
              </div>
              <span className="text-[11px] text-slate-400">24 consecutive daily learning reflections.</span>
            </TiltCard>

            {/* Widget 3 */}
            <TiltCard className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">AI Curator Pick</span>
                <Badge variant="green">Top Match</Badge>
              </div>
              <p className="text-sm font-bold text-white line-clamp-1">LangGraph Multi-Agent Architecture</p>
              <p className="text-xs text-slate-400">4.5h Course • DeepMind & GrowthOS</p>
              <Button size="sm" variant="outline" className="w-full text-xs py-1">Start Module</Button>
            </TiltCard>
          </div>
        </motion.div>
      </section>

      {/* Features Grid with Tilt Cards */}
      <section id="features" className="py-20 px-6 max-w-6xl mx-auto z-10 relative">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <Badge variant="purple">Core Capabilities</Badge>
          <h2 className="text-3xl sm:text-4xl font-bold text-white mt-3">An Intelligent OS For Your Mind & Career</h2>
          <p className="text-slate-400 text-sm mt-3">GrowthOS merges multi-agent LLM logic, continuous memory vector pools, and machine learning models to curate your future.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'Evolving Identity Twin',
              desc: 'Maps your current skills, values, and habits against your dream role. Calculates real-time identity drift.',
              icon: Brain,
              color: 'text-purple-400',
            },
            {
              title: 'Multi-Agent Curation Engine',
              desc: 'Autonomous LangGraph agents curate books, courses, videos, and papers specific to your skill gap.',
              icon: Sparkles,
              color: 'text-indigo-400',
            },
            {
              title: 'Opportunity Radar',
              desc: 'Scans global hackathons, venture internships, open source projects, and mentors matching your profile.',
              icon: Compass,
              color: 'text-cyan-400',
            },
            {
              title: 'Burnout & Risk Prediction',
              desc: 'Machine learning algorithms monitor study hours and sleep patterns to prevent exhaustion.',
              icon: Activity,
              color: 'text-emerald-400',
            },
            {
              title: 'Mem0 Vector Memory',
              desc: 'Never forgets your reflections, breakthrough insights, or historical learnings.',
              icon: Layers,
              color: 'text-pink-400',
            },
            {
              title: 'Autonomous Reflection Journal',
              desc: 'Extracts cognitive sentiment and actionable growth milestones from daily voice or text entries.',
              icon: Shield,
              color: 'text-amber-400',
            },
          ].map((f, i) => {
            const Icon = f.icon;
            return (
              <TiltCard key={i} className="p-6 space-y-4">
                <div className={`w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center ${f.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white">{f.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
              </TiltCard>
            );
          })}
        </div>
      </section>

      {/* Architecture Preview Section */}
      <section id="architecture" className="py-20 px-6 max-w-6xl mx-auto z-10 relative">
        <div className="glass-panel p-8 md:p-12 rounded-3xl border border-white/10 relative overflow-hidden">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-lg text-left">
              <Badge variant="blue">System Architecture</Badge>
              <h2 className="text-3xl font-extrabold text-white">Built on Frontier Agentic Stack</h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                GrowthOS combines modern React/Vite interfaces with FastAPI backends, LangGraph multi-agent supervisors, Mem0 vector memory pools, and Supabase PostgreSQL schema with Row-Level Security.
              </p>
              <div className="grid grid-cols-2 gap-3 text-xs font-semibold text-slate-300 pt-2">
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> LangGraph Supervisor</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Mem0 Long-term Memory</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Supabase RLS Database</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Scikit-Learn ML Models</div>
              </div>
            </div>

            <div className="w-full md:w-1/2 p-6 rounded-2xl bg-black/60 border border-purple-500/30 font-mono text-xs text-slate-300 space-y-2 shadow-2xl shadow-purple-950/50">
              <div className="text-purple-400 font-bold">// LangGraph Workflow Graph</div>
              <div className="text-slate-400">User Prompt → Supervisor Router</div>
              <div className="pl-4 text-emerald-400">├── Identity Agent (Evaluates Drift)</div>
              <div className="pl-4 text-indigo-400">├── Learning Curator (Fetch Resources)</div>
              <div className="pl-4 text-cyan-400">└── Memory Sync (Mem0 Vector Update)</div>
              <div className="text-amber-400 pt-2">Result: 98% Aligned Output Generated</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-6 max-w-6xl mx-auto z-10 relative text-center">
        <Badge variant="amber">Simple Pricing</Badge>
        <h2 className="text-3xl sm:text-4xl font-bold text-white mt-3">Invest in Your Potential</h2>
        <p className="text-slate-400 text-sm mt-2 max-w-md mx-auto">Choose the tier that accelerates your personal growth trajectory.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 text-left">
          {[
            {
              name: 'Starter',
              price: '$0',
              desc: 'For individuals starting their self-improvement journey.',
              features: ['1 Identity Twin', 'Basic Daily Curation', 'Manual Task Planner', 'Standard Analytics'],
              button: 'Get Started Free',
              variant: 'outline' as const,
            },
            {
              name: 'Pro Growth',
              price: '$19',
              desc: 'For ambitious engineers, founders, and lifelong learners.',
              features: ['Real-time Identity Drift Tracking', 'Full Agentic Curation Engine', 'AI Copilot Assistant', 'Burnout & Risk Models', 'Mem0 Memory Sync'],
              button: 'Start Pro Trial',
              variant: 'glow' as const,
              popular: true,
            },
            {
              name: 'Founders / Enterprise',
              price: '$49',
              desc: 'For executive leaders & high-performance builders.',
              features: ['1-on-1 VC Mentor Matching', 'Priority Opportunity Radar', 'Custom LangGraph Swarm', 'Dedicated Support'],
              button: 'Join Founder Tier',
              variant: 'outline' as const,
            },
          ].map((plan, i) => (
            <TiltCard
              key={i}
              className={`p-6 relative flex flex-col justify-between ${
                plan.popular ? 'border-purple-500/50 shadow-2xl shadow-purple-950/50 scale-105' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 right-6 px-3 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-[10px] font-extrabold text-white rounded-full uppercase tracking-wider shadow-md">
                  Most Popular
                </div>
              )}
              <div>
                <h3 className="text-lg font-bold text-white">{plan.name}</h3>
                <p className="text-xs text-slate-400 mt-1">{plan.desc}</p>
                <div className="my-6">
                  <span className="text-4xl font-extrabold text-white">{plan.price}</span>
                  <span className="text-slate-400 text-xs"> / month</span>
                </div>
                <div className="space-y-2.5 text-xs text-slate-300">
                  {plan.features.map((feat, j) => (
                    <div key={j} className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <NavLink to="/onboarding" className="mt-8 block">
                <Button variant={plan.variant} className="w-full">
                  {plan.button}
                </Button>
              </NavLink>
            </TiltCard>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 px-6 max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-slate-500 relative z-10">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-purple-400" />
          <span className="font-bold text-slate-300">GrowthOS © 2026</span>
          <span>• The AI That Curates Your Future.</span>
        </div>
        <div className="flex items-center gap-6">
          <a href="#" className="hover:text-slate-300">Privacy Policy</a>
          <a href="#" className="hover:text-slate-300">Terms of Service</a>
          <a href="#" className="hover:text-slate-300">GitHub</a>
          <a href="#" className="hover:text-slate-300">Twitter / X</a>
        </div>
      </footer>
    </div>
  );
};
