import React from 'react';
import { useLocation, NavLink } from 'react-router-dom';
import {
  Search,
  Sparkles,
  Bell,
  Sun,
  Moon,
  ChevronRight,
  Flame,
} from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useApp } from '../../context/AppContext';

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, setIsCopilotOpen, setIsCommandPaletteOpen, notifications } = useApp();
  const location = useLocation();

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  const pathNames: Record<string, string> = {
    '/': 'Overview',
    '/dashboard': 'Dashboard',
    '/identity-twin': 'Identity Twin',
    '/learning': 'Learning Curation',
    '/opportunities': 'Growth Opportunities',
    '/planner': 'Daily Planner',
    '/reflection': 'Reflection Journal',
    '/notifications': 'Notification Center',
    '/analytics': 'Analytics & Risk',
    '/profile': 'Profile & Settings',
    '/onboarding': 'Onboarding Wizard',
  };

  const currentPathLabel = pathNames[location.pathname] || 'GrowthOS';

  return (
    <header className="sticky top-0 z-20 flex items-center justify-between h-16 px-6 border-b border-white/10 bg-[#090a0f]/80 backdrop-blur-xl">
      {/* Breadcrumb Path */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <NavLink to="/dashboard" className="hover:text-white transition-colors">
          GrowthOS
        </NavLink>
        <ChevronRight className="w-4 h-4 text-slate-600" />
        <span className="font-semibold text-white">{currentPathLabel}</span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Streak Counter */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-bold shadow-sm">
          <Flame className="w-4 h-4 text-amber-400 fill-amber-400 animate-pulse" />
          <span>{user.streak} Day Streak</span>
        </div>

        {/* Global Search / Command Palette Trigger */}
        <button
          onClick={() => setIsCommandPaletteOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 text-xs text-slate-400 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-colors"
        >
          <Search className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Search or command...</span>
          <kbd className="hidden md:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-white/10 rounded border border-white/10 text-slate-300">
            ⌘K
          </kbd>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 text-slate-400 hover:text-white rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-indigo-400" />}
        </button>

        {/* Notifications Quick Link */}
        <NavLink
          to="/notifications"
          className="relative p-2 text-slate-400 hover:text-white rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-colors"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white ring-2 ring-[#090a0f]">
              {unreadCount}
            </span>
          )}
        </NavLink>

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
