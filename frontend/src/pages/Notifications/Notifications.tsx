import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, Sparkles, Check, Compass, Award, Calendar, ExternalLink } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';

export const Notifications: React.FC = () => {
  const { notifications, markNotificationAsRead } = useApp();
  const [filter, setFilter] = useState<'all' | 'unread'>('all');

  const filtered = notifications.filter((n) => filter === 'all' || !n.isRead);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="purple" icon={<Bell className="w-3.5 h-3.5" />}>
              Notification Hub
            </Badge>
            <Badge variant="cyan">{notifications.filter((n) => !n.isRead).length} Unread Alerts</Badge>
          </div>
          <h1 className="text-3xl font-extrabold text-white mt-2">Notifications Center</h1>
          <p className="text-xs text-slate-400">Real-time alerts from your autonomous multi-agent swarm.</p>
        </div>

        <div className="flex items-center gap-2 p-1 bg-white/5 border border-white/10 rounded-xl">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              filter === 'all' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            All Alerts
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
              filter === 'unread' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Unread
          </button>
        </div>
      </div>

      {/* Notifications Feed */}
      <div className="space-y-3">
        {filtered.map((notif) => (
          <motion.div
            key={notif.id}
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            onClick={() => markNotificationAsRead(notif.id)}
            className={`p-5 rounded-2xl border transition-all cursor-pointer flex items-start justify-between gap-4 ${
              notif.isRead
                ? 'bg-white/5 border-white/5 opacity-70'
                : 'bg-gradient-to-r from-purple-950/30 via-indigo-950/20 to-black border-purple-500/30 shadow-lg shadow-purple-950/30'
            }`}
          >
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0 mt-0.5">
                {notif.type === 'milestone' ? (
                  <Award className="w-5 h-5 text-amber-400" />
                ) : notif.type === 'opportunity' ? (
                  <Compass className="w-5 h-5 text-cyan-400" />
                ) : (
                  <Sparkles className="w-5 h-5 text-purple-400" />
                )}
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-white">{notif.title}</h3>
                  {!notif.isRead && (
                    <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
                  )}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{notif.message}</p>
                <span className="text-[10px] text-slate-500 block pt-1">{notif.timeAgo}</span>
              </div>
            </div>

            {notif.actionUrl && (
              <a
                href={notif.actionUrl}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors shrink-0"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
};
