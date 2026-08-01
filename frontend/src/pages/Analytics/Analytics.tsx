import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Activity, Flame, ShieldAlert, Zap, Clock } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { Badge } from '../../components/common/Badge';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';

export const Analytics: React.FC = () => {
  const { analytics } = useApp();

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Badge variant="purple" icon={<BarChart3 className="w-3.5 h-3.5" />}>
              Analytics Engine
            </Badge>
            <Badge variant="green">Burnout Risk: {analytics.burnoutRiskPercentage}% (Low)</Badge>
          </div>
          <h1 className="text-3xl font-extrabold text-white mt-2">Analytics & Growth Prediction</h1>
          <p className="text-xs text-slate-400">Deep telemetry on your habit regularity, skill growth, and cognitive endurance.</p>
        </div>
      </div>

      {/* 4 Stat Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Growth Prediction</span>
          <p className="text-3xl font-extrabold text-white">{analytics.growthPredictionScore} / 100</p>
          <span className="text-xs font-bold text-emerald-400">+6% Projected Next Month</span>
        </div>

        <div className="glass-card p-5 rounded-2xl space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Burnout Risk Gauge</span>
          <p className="text-3xl font-extrabold text-emerald-400">{analytics.burnoutRiskPercentage}%</p>
          <span className="text-xs font-bold text-emerald-300">Optimal Work-Rest Cadence</span>
        </div>

        <div className="glass-card p-5 rounded-2xl space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Consistency Rate</span>
          <p className="text-3xl font-extrabold text-indigo-400">{analytics.consistencyRate}%</p>
          <span className="text-xs font-bold text-slate-400">24-Day Active Streak</span>
        </div>

        <div className="glass-card p-5 rounded-2xl space-y-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Deep Work Hours</span>
          <p className="text-3xl font-extrabold text-cyan-400">{analytics.learningHoursTotal}h</p>
          <span className="text-xs font-bold text-slate-400">Logged since Jan 2026</span>
        </div>
      </div>

      {/* Charts Grid 1: Radar Chart + Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skill Matrix Radar Chart */}
        <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-purple-400" />
              Skill Mastery Radar (Current vs Target)
            </h3>
            <Badge variant="purple">6 Core Dimensions</Badge>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={analytics.radarSkills}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748b" fontSize={10} />
                <Radar name="Current Mastery" dataKey="current" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.5} />
                <Radar name="Target Archetype" dataKey="target" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.2} />
                <Tooltip contentStyle={{ backgroundColor: '#12141d', borderRadius: '12px', fontSize: '12px', color: '#fff' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weekly Heatmap Bar Chart */}
        <div className="glass-panel p-6 rounded-3xl border border-white/10 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              Weekly Deep Learning Heatmap (Hours)
            </h3>
            <Badge variant="cyan">Avg 5.3h / Day</Badge>
          </div>

          <div className="h-72 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.weeklyHeatmap}>
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#12141d', borderRadius: '12px', fontSize: '12px', color: '#fff' }} />
                <Bar dataKey="hours" fill="#6366f1" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
