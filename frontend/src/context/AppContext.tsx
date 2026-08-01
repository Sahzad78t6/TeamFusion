import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  UserProfile,
  IdentityTwin,
  LearningResource,
  Opportunity,
  TaskItem,
  ReflectionEntry,
  NotificationItem,
  AnalyticsSummary,
} from '../types';
import {
  mockUser,
  mockIdentityTwin,
  mockLearningResources,
  mockOpportunities,
  mockTasks,
  mockReflections,
  mockNotifications,
  mockAnalytics,
} from '../utils/dummyData';
import {
  AuthUserResponse,
  getMeApi,
  logoutApi,
  submitOnboardingApi,
  getDashboardApi,
  OnboardingPayload,
} from '../services/api';

interface AppContextType {
  user: UserProfile;
  setUser: React.Dispatch<React.SetStateAction<UserProfile>>;
  authToken: string | null;
  setAuthToken: (token: string | null) => void;
  setAuthSession: (accessToken: string, refreshToken: string, authUser: AuthUserResponse) => void;
  logout: () => void;
  identityTwin: IdentityTwin;
  setIdentityTwin: React.Dispatch<React.SetStateAction<IdentityTwin>>;
  learningResources: LearningResource[];
  setLearningResources: React.Dispatch<React.SetStateAction<LearningResource[]>>;
  opportunities: Opportunity[];
  setOpportunities: React.Dispatch<React.SetStateAction<Opportunity[]>>;
  tasks: TaskItem[];
  setTasks: React.Dispatch<React.SetStateAction<TaskItem[]>>;
  reflections: ReflectionEntry[];
  notifications: NotificationItem[];
  analytics: AnalyticsSummary;
  isCopilotOpen: boolean;
  setIsCopilotOpen: (open: boolean) => void;
  isCommandPaletteOpen: boolean;
  setIsCommandPaletteOpen: (open: boolean) => void;
  toggleTask: (taskId: string) => void;
  toggleBookmarkResource: (resourceId: string) => void;
  toggleLikeResource: (resourceId: string) => void;
  toggleFavoriteOpportunity: (oppId: string) => void;
  markNotificationAsRead: (notifId: string) => void;
  addReflection: (entry: Omit<ReflectionEntry, 'id' | 'date'>) => void;
  submitOnboarding: (payload: OnboardingPayload) => Promise<any>;
  refreshDashboard: () => Promise<void>;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile>(mockUser);
  const [authToken, setAuthTokenState] = useState<string | null>(() => localStorage.getItem('growthos_access_token'));
  const [identityTwin, setIdentityTwin] = useState<IdentityTwin>(mockIdentityTwin);
  const [learningResources, setLearningResources] = useState<LearningResource[]>(mockLearningResources);
  const [opportunities, setOpportunities] = useState<Opportunity[]>(mockOpportunities);
  const [tasks, setTasks] = useState<TaskItem[]>(mockTasks);
  const [reflections, setReflections] = useState<ReflectionEntry[]>(mockReflections);
  const [notifications, setNotifications] = useState<NotificationItem[]>(mockNotifications);
  const [analytics, setAnalytics] = useState<AnalyticsSummary>(mockAnalytics);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const setAuthToken = (token: string | null) => {
    setAuthTokenState(token);
    if (token) {
      localStorage.setItem('growthos_access_token', token);
    } else {
      localStorage.removeItem('growthos_access_token');
      localStorage.removeItem('growthos_refresh_token');
    }
  };

  const setAuthSession = (accessToken: string, refreshToken: string, authUser: AuthUserResponse) => {
    setAuthTokenState(accessToken);
    localStorage.setItem('growthos_access_token', accessToken);
    localStorage.setItem('growthos_refresh_token', refreshToken);

    setUser((prev) => ({
      ...prev,
      id: authUser.id,
      name: authUser.name || prev.name,
      email: authUser.email || prev.email,
    }));
  };

  const logout = async () => {
    if (authToken) {
      try {
        await logoutApi(authToken);
      } catch (e) {
        // Suppress
      }
    }
    setAuthToken(null);
  };

  const refreshDashboard = async () => {
    if (!authToken) return;
    try {
      const data = await getDashboardApi(authToken);
      if (data.identity_twin) {
        setIdentityTwin((prev) => ({
          ...prev,
          dreamArchetype: data.identity_twin.target_role || data.identity_twin.goal || prev.dreamArchetype,
          alignmentPercentage: Math.round(data.identity_twin.identity_score || prev.alignmentPercentage),
          driftScore: Math.round(data.identity_twin.identity_drift_percentage || prev.driftScore),
        }));
      }
      if (data.analytics) {
        setAnalytics((prev) => ({
          ...prev,
          growthPredictionScore: Math.round(data.analytics.growth_score || prev.growthPredictionScore),
          learningHoursTotal: data.analytics.weekly_hours_logged || prev.learningHoursTotal,
        }));
      }
      if (data.roadmap && data.roadmap.tasks) {
        setTasks(
          data.roadmap.tasks.map((t: any) => ({
            id: t.id,
            title: t.title,
            isCompleted: t.completed || false,
            estimatedMins: t.duration_mins || 30,
            category: t.category || 'Roadmap',
            priority: t.priority || 'medium',
            time: '09:00 AM',
            duration: `${t.duration_mins || 30} mins`,
            date: 'Today',
            type: 'learning',
          }))
        );
      }
      if (data.recommendations && data.recommendations.length > 0) {
        setLearningResources(
          data.recommendations.map((r: any) => ({
            id: r.id,
            title: r.title,
            type: r.type || 'course',
            author: r.provider || 'GrowthOS',
            platform: r.provider || 'GrowthOS',
            duration: '2 Hours',
            difficulty: 'Intermediate',
            category: 'AI Architecture',
            rating: 4.9,
            imageUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80',
            link: r.url || '#',
            tags: r.tags || ['AI'],
            isBookmarked: false,
            isLiked: false,
            progressPercentage: 0,
          }))
        );
      }
      if (data.notifications && data.notifications.length > 0) {
        setNotifications(
          data.notifications.map((n: any) => ({
            id: n.id,
            title: n.title,
            message: n.message,
            timeAgo: 'Just now',
            isRead: n.read || false,
            type: n.type || 'milestone',
          }))
        );
      }
    } catch (e) {
      console.warn('Dashboard refresh failed:', e);
    }
  };

  const submitOnboarding = async (payload: OnboardingPayload) => {
    setIdentityTwin((prev) => ({
      ...prev,
      dreamArchetype: payload.target_role || payload.goal,
    }));
    setUser((prev) => ({
      ...prev,
      dreamRole: payload.target_role || payload.goal,
    }));

    if (authToken) {
      const res = await submitOnboardingApi(authToken, payload);
      await refreshDashboard();
      return res;
    }
  };

  useEffect(() => {
    if (authToken) {
      getMeApi(authToken)
        .then((me) => {
          setUser((prev) => ({
            ...prev,
            id: me.id,
            name: me.name || prev.name,
            email: me.email || prev.email,
          }));
          refreshDashboard();
        })
        .catch(() => {
          // Token expired
        });
    }
  }, [authToken]);

  const toggleTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, isCompleted: !t.isCompleted } : t))
    );
  };

  const toggleBookmarkResource = (resourceId: string) => {
    setLearningResources((prev) =>
      prev.map((r) => (r.id === resourceId ? { ...r, isBookmarked: !r.isBookmarked } : r))
    );
  };

  const toggleLikeResource = (resourceId: string) => {
    setLearningResources((prev) =>
      prev.map((r) => (r.id === resourceId ? { ...r, isLiked: !r.isLiked } : r))
    );
  };

  const toggleFavoriteOpportunity = (oppId: string) => {
    setOpportunities((prev) =>
      prev.map((o) => (o.id === oppId ? { ...o, isFavorite: !o.isFavorite } : o))
    );
  };

  const markNotificationAsRead = (notifId: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === notifId ? { ...n, isRead: true } : n))
    );
  };

  const addReflection = (newRef: Omit<ReflectionEntry, 'id' | 'date'>) => {
    const entry: ReflectionEntry = {
      ...newRef,
      id: `ref-${Date.now()}`,
      date: new Date().toLocaleDateString('en-US', { month: 'long', day: '2-digit', year: 'numeric' }),
    };
    setReflections((prev) => [entry, ...prev]);
  };

  return (
    <AppContext.Provider
      value={{
        user,
        setUser,
        authToken,
        setAuthToken,
        setAuthSession,
        logout,
        identityTwin,
        setIdentityTwin,
        learningResources,
        setLearningResources,
        opportunities,
        setOpportunities,
        tasks,
        setTasks,
        reflections,
        notifications,
        analytics,
        isCopilotOpen,
        setIsCopilotOpen,
        isCommandPaletteOpen,
        setIsCommandPaletteOpen,
        toggleTask,
        toggleBookmarkResource,
        toggleLikeResource,
        toggleFavoriteOpportunity,
        markNotificationAsRead,
        addReflection,
        submitOnboarding,
        refreshDashboard,
        searchQuery,
        setSearchQuery,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
