import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Mail, Lock, User, ArrowRight, CheckCircle2, Sun, Moon } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { useTheme } from '../../context/ThemeContext';

export const Signup: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      navigate('/onboarding');
    }, 1000);
  };

  return (
    <div className="min-h-screen w-screen bg-white dark:bg-[#090a0f] flex items-center justify-center p-4 selection:bg-purple-500 selection:text-white relative overflow-hidden transition-colors duration-300">
      {/* Absolute Theme Toggle Button */}
      <button
        onClick={toggleTheme}
        className="absolute top-6 right-6 p-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors z-50 shadow-sm"
        title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
      >
        {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-550 dark:text-amber-300" /> : <Moon className="w-4 h-4 text-indigo-650 dark:text-indigo-400" />}
      </button>

      {/* Background Glow */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-purple-600/10 dark:bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-600/10 dark:bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 rounded-3xl border border-slate-200 dark:border-white/10 bg-slate-50/90 dark:bg-[#12141d]/90 backdrop-blur-2xl shadow-2xl shadow-slate-200/50 dark:shadow-purple-950/50 overflow-hidden transition-colors duration-300"
      >
        {/* Left Form */}
        <div className="p-8 md:p-10 flex flex-col justify-between space-y-6">
          <div>
            <NavLink to="/" className="inline-flex items-center gap-2 mb-6">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="font-extrabold text-lg text-slate-900 dark:text-white">Growth<span className="text-gradient">OS</span></span>
            </NavLink>

            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Create Your Account</h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Start curating your future self in under 2 minutes.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-xs text-slate-900 dark:text-white placeholder-slate-455 dark:placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
                  placeholder="Alex Rivera"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-xs text-slate-900 dark:text-white placeholder-slate-455 dark:placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
                  placeholder="alex@example.com"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl text-xs text-slate-900 dark:text-white placeholder-slate-455 dark:placeholder-slate-500 focus:outline-none focus:border-purple-500/50"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="glow"
              className="w-full mt-2"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Continue to Onboarding Wizard
            </Button>
          </form>

          <p className="text-center text-xs text-slate-600 dark:text-slate-400">
            Already have an account?{' '}
            <NavLink to="/login" className="text-purple-600 dark:text-purple-400 font-bold hover:underline">
              Sign In
            </NavLink>
          </p>
        </div>

        {/* Right Info */}
        <div className="hidden md:flex flex-col justify-between p-8 bg-gradient-to-br from-indigo-100/50 dark:from-indigo-900/30 via-purple-50/30 dark:via-purple-900/20 to-slate-50 dark:to-black border-l border-slate-200 dark:border-white/10 transition-colors duration-300">
          <div className="space-y-4">
            <span className="px-3 py-1 bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-650 dark:text-indigo-300 text-[10px] font-extrabold rounded-full uppercase border border-indigo-300 dark:border-indigo-500/30">
              Why GrowthOS?
            </span>
            <h3 className="text-2xl font-extrabold text-slate-900 dark:text-white">Your Personal AI Growth Strategist</h3>

            <div className="space-y-3 pt-4 text-xs text-slate-700 dark:text-slate-300">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 dark:text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Identity Twin Engine</strong> maps your current vs dream self in real time.</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 dark:text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>Multi-Agent Curation</strong> recommends high-ROI courses, books & papers.</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 dark:text-emerald-400 shrink-0 mt-0.5" />
                <span><strong>ML Risk Guard</strong> protects you against burnout & cognitive fatigue.</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
