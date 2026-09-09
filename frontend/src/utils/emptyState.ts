import type { AnalyticsSummary, IdentityTwin, UserProfile } from '../types';

export const emptyUser: UserProfile = {
  id: '', name: '', email: '', avatar: '', title: '', bio: '', dreamRole: '', level: 0,
  experienceLevel: '', location: '', streak: 0, growthScore: 0, identityScore: 0,
  joinedDate: '', achievements: [], certificates: [],
};

export const emptyIdentityTwin: IdentityTwin = {
  currentArchetype: '', dreamArchetype: '', alignmentPercentage: 0, driftScore: 0,
  coreValues: [], dreamValues: [], skills: [], insights: [], timeline: [],
};

export const emptyAnalytics: AnalyticsSummary = {
  growthPredictionScore: 0, burnoutRiskPercentage: 0, consistencyRate: 0,
  learningHoursTotal: 0, weeklyHeatmap: [], monthlyProgress: [], radarSkills: [],
};
