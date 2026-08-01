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
import { AuthUserResponse, getMeApi, logoutApi } from '../services/api';

interface AppContextType {
  user: UserProfile;
  setUser: React.Dispatch<React.SetStateAction<UserProfile>>;
  authToken: string | null;
  setAuthToken: (token: string | null) => void;
  setAuthSession: (accessToken: string, refreshToken: string, authUser: AuthUserResponse) => void;
  logout: () => void;
  identityTwin: IdentityTwin;
  learningResources: LearningResource[];
  opportunities: Opportunity[];
  tasks: TaskItem[];
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
  const [analytics] = useState<AnalyticsSummary>(mockAnalytics);
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

  // Fetch current user from backend API on mount if token exists
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
        })
        .catch(() => {
          // Token expired
        });
    }
  }, []);

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
        learningResources,
        opportunities,
        tasks,
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
