import React, { useState, useRef, useEffect } from 'react';
import { useLocation, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Sparkles,
  Bell,
  Sun,
  Moon,
  ChevronRight,
  Flame,
  Award,
  Compass,
  ExternalLink,
  Check,
  X,
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useApp } from '../../context/AppContext';

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, setIsCopilotOpen, setIsCommandPaletteOpen, notifications, markNotificationAsRead } = useApp();
  const location = useLocation();
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setIsNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const pathNames: Record<string, string> = {
    '/': 'Overview',
    '/dashboard': 'Dashboard',
    '/identity-twin': 'Identity Twin',
    '/learning': 'Learning Curation',
    '/opportunities': 'Growth Opportunities',
    '/planner': 'Daily Planner',
    '/reflection': 'Reflection Journal',
    '/notifications': 'Notification Center',
    '/profile': 'Profile & Settings',
    '/onboarding': 'Onboarding Wizard',
  };

  const currentPathLabel = pathNames[location.pathname] || 'GrowthOS';

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between h-16 px-6 border-b border-slate-200 dark:border-white/10 bg-white/80 dark:bg-[#090a0f]/80 backdrop-blur-xl transition-all duration-300">
      {/* Breadcrumb Path */}
      <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
        <NavLink to="/dashboard" className="hover:text-slate-900 dark:hover:text-white transition-colors">
          GrowthOS
        </NavLink>
        <ChevronRight className="w-4 h-4 text-slate-400 dark:text-slate-600" />
        <span className="font-semibold text-slate-900 dark:text-white">{currentPathLabel}</span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Streak Counter */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-300 text-xs font-bold shadow-sm">
          <Flame className="w-4 h-4 text-amber-500 dark:text-amber-400 fill-amber-500 dark:fill-amber-400 animate-pulse" />
          <span>{user.streak} Day Streak</span>
        </div>

        {/* Global Search / Command Palette Trigger */}
        <button
          onClick={() => setIsCommandPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-550 dark:text-slate-400 bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 rounded-xl transition-all"
        >
          <Search className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Search or command...</span>
          <kbd className="hidden md:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-slate-200 dark:bg-white/10 rounded border border-slate-300 dark:border-white/10 text-slate-600 dark:text-slate-300">
            ⌘K
          </kbd>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-550 dark:text-amber-300" /> : <Moon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />}
        </button>

        {/* Notifications Popover Dropdown */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setIsNotifOpen(!isNotifOpen)}
            className="relative p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-xl bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 transition-colors"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white ring-2 ring-white dark:ring-[#090a0f]">
                {unreadCount}
              </span>
            )}
          </button>

          <AnimatePresence>
            {isNotifOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#12141d] shadow-2xl shadow-slate-200/50 dark:shadow-purple-950/60 overflow-hidden z-50 backdrop-blur-2xl"
              >
                <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-purple-650 dark:text-purple-400" />
                    <span className="text-xs font-bold text-slate-900 dark:text-white">Notifications</span>
                    {unreadCount > 0 && (
                      <span className="px-2 py-0.5 text-[9px] font-bold rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-500/30">
                        {unreadCount} New
                      </span>
                    )}
                  </div>
                  <NavLink
                    to="/notifications"
                    onClick={() => setIsNotifOpen(false)}
                    className="text-[11px] font-semibold text-purple-400 hover:underline"
                  >
                    View All
                  </NavLink>
                </div>

                <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-white/5">
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      onClick={() => markNotificationAsRead(notif.id)}
                      className={`p-3.5 hover:bg-slate-50 dark:hover:bg-white/5 cursor-pointer transition-colors flex items-start gap-3 ${
                        notif.isRead ? 'opacity-60' : 'bg-purple-50 dark:bg-purple-950/20'
                      }`}
                    >
                      <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-650 dark:text-purple-400 shrink-0 mt-0.5">
                        {notif.type === 'milestone' ? (
                          <Award className="w-4 h-4 text-amber-500 dark:text-amber-400" />
                        ) : notif.type === 'opportunity' ? (
                          <Compass className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
                        ) : (
                          <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                        )}
                      </div>
                      <div className="flex-1 space-y-0.5">
                        <h4 className="text-xs font-bold text-slate-900 dark:text-white">{notif.title}</h4>
                        <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-snug">{notif.message}</p>
                        <span className="text-[9px] text-slate-400 dark:text-slate-500 block pt-1">{notif.timeAgo}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* AI Copilot Drawer Launcher */}
        <button
          onClick={() => setIsCopilotOpen(true)}
          className="flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 rounded-xl shadow-lg shadow-purple-500/25 border border-purple-400/30 transition-all hover:scale-105"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-300 fill-amber-300 animate-pulse" />
          <span className="hidden sm:inline">AI Copilot</span>
        </button>
      </div>
    </header>
  );
};
