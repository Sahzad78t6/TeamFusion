import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Award, Shield, Settings, Moon, Sun, Globe, Bell, CheckCircle2, Trophy, ExternalLink, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { useTheme } from '../../context/ThemeContext';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export const Profile: React.FC = () => {
  const { user } = useApp();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState<'profile' | 'settings'>('profile');

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner & Profile Header */}
      <div className="glass-panel p-6 md:p-8 rounded-3xl border border-white/10 space-y-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div className="flex items-center gap-5">
            <img
              src={user.avatar}
              alt={user.name}
              className="w-20 h-20 rounded-2xl object-cover border-2 border-purple-500/40 shadow-xl shadow-purple-500/20 shrink-0"
            />
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold text-white">{user.name}</h1>
                <Badge variant="purple">Level {user.level}</Badge>
              </div>
              <p className="text-xs font-semibold text-slate-300">{user.title}</p>
              <p className="text-xs text-slate-400 max-w-md">{user.bio}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 p-1 bg-white/5 border border-white/10 rounded-xl">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors ${
                activeTab === 'profile' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Profile & Badges
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors ${
                activeTab === 'settings' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Settings
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'profile' && (
        <div className="space-y-8">
          {/* Achievements Grid */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-400" />
              Unlocked Achievements & Badges
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {user.achievements.map((ach) => (
                <div key={ach.id} className="p-5 rounded-2xl bg-white/5 border border-white/10 space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{ach.title}</h4>
                    <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">{ach.description}</p>
                  </div>
                  <span className="text-[10px] text-purple-400 font-semibold block pt-2">Unlocked {ach.unlockedAt}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Certificates */}
          <div className="space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-5 h-5 text-purple-400" />
              Verified Credentials & Certificates
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {user.certificates.map((cert) => (
                <div key={cert.id} className="p-5 rounded-2xl bg-white/5 border border-white/10 space-y-3 flex flex-col justify-between">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">{cert.issuer}</span>
                    <h4 className="text-sm font-bold text-white">{cert.title}</h4>
                    <span className="text-xs text-slate-400 block">{cert.date}</span>
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {cert.skills.map((s, i) => (
                      <span key={i} className="px-2 py-0.5 text-[9px] rounded bg-white/5 text-slate-300 border border-white/10">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-6 max-w-2xl">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-purple-400" />
            Application Preferences
          </h3>

          <div className="space-y-4 text-xs text-slate-300">
            {/* Theme Toggle Option */}
            <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-3">
                {theme === 'dark' ? <Moon className="w-5 h-5 text-indigo-400" /> : <Sun className="w-5 h-5 text-amber-300" />}
                <div>
                  <h4 className="font-bold text-white">Appearance Theme</h4>
                  <p className="text-[11px] text-slate-400">Current mode: {theme === 'dark' ? 'Dark Mode (Primary)' : 'Light Mode'}</p>
                </div>
              </div>

              <Button size="sm" variant="outline" onClick={toggleTheme}>
                Toggle to {theme === 'dark' ? 'Light' : 'Dark'}
              </Button>
            </div>

            {/* Language Selector */}
            <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/10">
              <div className="flex items-center gap-3">
                <Globe className="w-5 h-5 text-cyan-400" />
                <div>
                  <h4 className="font-bold text-white">Language & Locale</h4>
                  <p className="text-[11px] text-slate-400">English (United States) — UTC -7</p>
                </div>
              </div>
              <Badge variant="cyan">Default</Badge>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
