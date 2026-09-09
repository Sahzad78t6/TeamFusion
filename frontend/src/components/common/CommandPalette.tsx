import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sparkles, LayoutDashboard, BookOpen, Compass, Calendar, PenTool, User, X, ArrowRight } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const CommandPalette: React.FC = () => {
  const { isCommandPaletteOpen, setIsCommandPaletteOpen, learningResources, opportunities } = useApp();
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen(!isCommandPaletteOpen);
      }
      if (e.key === 'Escape') {
        setIsCommandPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandPaletteOpen, setIsCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  const quickNav = [
    { label: 'Dashboard Overview', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Identity Twin Analysis', path: '/identity-twin', icon: Sparkles },
    { label: 'Browse Learning Resources', path: '/learning', icon: BookOpen },
    { label: 'Explore Growth Opportunities', path: '/opportunities', icon: Compass },
    { label: 'Daily Planner & Timeline', path: '/planner', icon: Calendar },
    { label: 'Reflection Journal', path: '/reflection', icon: PenTool },
    { label: 'User Profile & Settings', path: '/profile', icon: User },
  ];

  const filteredNav = quickNav.filter((n) => n.label.toLowerCase().includes(query.toLowerCase()));
  const filteredResources = learningResources.filter((r) =>
    r.title.toLowerCase().includes(query.toLowerCase()) || r.tags.some((t) => t.toLowerCase().includes(query.toLowerCase()))
  );
  const filteredOpp = opportunities.filter((o) =>
    o.title.toLowerCase().includes(query.toLowerCase()) || o.skillsRequired.some((s) => s.toLowerCase().includes(query.toLowerCase()))
  );

  const handleNavigate = (path: string) => {
    setIsCommandPaletteOpen(false);
    navigate(path);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/70 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-2xl overflow-hidden rounded-2xl border border-white/10 bg-[#12141d] shadow-2xl shadow-purple-950/50"
        >
          {/* Input Header */}
          <div className="flex items-center gap-3 px-4 py-3.5 border-b border-white/10 bg-white/5">
            <Search className="w-5 h-5 text-purple-400" />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command, page, skill or search keyword..."
              className="w-full bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none"
            />
            <button
              onClick={() => setIsCommandPaletteOpen(false)}
              className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-white/10"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Results List */}
          <div className="max-h-96 overflow-y-auto p-3 space-y-4">
            {/* Navigation Commands */}
            {filteredNav.length > 0 && (
              <div>
                <span className="px-3 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Pages & Tools</span>
                <div className="mt-1 space-y-1">
                  {filteredNav.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.path}
                        onClick={() => handleNavigate(item.path)}
                        className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-indigo-600/20 hover:border hover:border-indigo-500/30 transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-4 h-4 text-slate-400 group-hover:text-indigo-400" />
                          <span>{item.label}</span>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-indigo-400 transition-opacity" />
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Learning Matches */}
            {filteredResources.length > 0 && (
              <div>
                <span className="px-3 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Curated Learning</span>
                <div className="mt-1 space-y-1">
                  {filteredResources.slice(0, 3).map((res) => (
                    <button
                      key={res.id}
                      onClick={() => handleNavigate('/learning')}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-white/5 group"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <BookOpen className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                        <span className="truncate">{res.title}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 uppercase shrink-0">{res.type}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Opportunities */}
            {filteredOpp.length > 0 && (
              <div>
                <span className="px-3 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Growth Opportunities</span>
                <div className="mt-1 space-y-1">
                  {filteredOpp.slice(0, 3).map((opp) => (
                    <button
                      key={opp.id}
                      onClick={() => handleNavigate('/opportunities')}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-white/5 group"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <Compass className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span className="truncate">{opp.title}</span>
                      </div>
                      <span className="text-[10px] text-emerald-400 font-bold shrink-0">{opp.matchScore}% Match</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer Shortcuts */}
          <div className="flex items-center justify-between px-4 py-2.5 border-t border-white/10 bg-white/5 text-[10px] text-slate-400">
            <div className="flex items-center gap-3">
              <span>Use <kbd className="px-1 py-0.5 bg-white/10 rounded font-mono text-slate-300">↑</kbd> <kbd className="px-1 py-0.5 bg-white/10 rounded font-mono text-slate-300">↓</kbd> to navigate</span>
              <span><kbd className="px-1 py-0.5 bg-white/10 rounded font-mono text-slate-300">↵</kbd> to select</span>
            </div>
            <span>GrowthOS Intelligence</span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
