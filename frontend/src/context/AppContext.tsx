import React, { createContext, useContext, useState } from 'react';
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

interface AppContextType {
  user: UserProfile;
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
