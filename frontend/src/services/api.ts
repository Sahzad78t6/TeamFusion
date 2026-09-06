const IS_PROD = (import.meta as any).env?.PROD;
const VITE_API_URL = (import.meta as any).env?.VITE_API_URL;

if (IS_PROD && !VITE_API_URL) {
  console.warn(
    '[GrowthOS Configuration Warning] VITE_API_URL is not set in production build. ' +
    'API calls will default to relative "/api" which requires a production reverse proxy (e.g. Nginx/Vercel rewrites).'
  );
}

const API_BASE_URL = VITE_API_URL || '/api';

export interface AuthUserResponse {
  id: string;
  name: string;
  email: string;
  created_at?: string;
  role?: 'STUDENT' | 'INSTITUTION_ADMIN' | 'PLATFORM_ADMIN';
  institution_id?: string | null;
  cohort_id?: string | null;
  onboarding_completed?: boolean;
}

export interface AuthTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUserResponse;
}

export interface OnboardingPayload {
  goal: string;
  target_role: string;
  current_role?: string;
  skills: string[];
  interests: string[];
  experience?: string;
  learning_style?: string;
  career_stage?: string;
  available_time?: string;
  preferred_content?: string[];
  language?: string;
}

async function safeFetch(url: string, options: RequestInit): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(url, options);
  } catch (err: any) {
    if (err instanceof TypeError || err.message?.includes('fetch')) {
      throw new Error(
        `Unable to connect to GrowthOS backend server at ${url}. Please verify backend server is running and VITE_API_URL is set.`
      );
    }
    throw err;
  }

  if (response.status === 404 && !VITE_API_URL && IS_PROD) {
    throw new Error(
      `GrowthOS API Endpoint 404 Not Found (${url}). Please set VITE_API_URL in your environment or deployment platform.`
    );
  }

  return response;
}

export async function signupApi(name: string, email: string, password: string): Promise<AuthTokenResponse> {
  const response = await safeFetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Signup failed. Please try again.');
  }

  return data;
}

export async function loginApi(email: string, password: string): Promise<AuthTokenResponse> {
  const response = await safeFetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Login failed. Invalid email or password.');
  }

  return data;
}

export async function loginWithGoogleApi(payload: { credential?: string; code?: string; redirect_uri?: string }): Promise<AuthTokenResponse> {
  const response = await safeFetch(`${API_BASE_URL}/auth/google`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Google sign-in failed.');
  }

  return data;
}

export async function getMeApi(token: string): Promise<AuthUserResponse> {
  const response = await safeFetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch current user.');
  }

  return data;
}

export async function logoutApi(token: string): Promise<void> {
  await safeFetch(`${API_BASE_URL}/auth/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
}

// Onboarding & Identity APIs
export async function submitOnboardingApi(token: string, payload: OnboardingPayload): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/onboarding`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to save onboarding data.');
  }
  return data;
}

export async function getIdentityApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/onboarding/identity`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch user identity.');
  }
  return data;
}

// Dashboard Summary API
export async function getDashboardApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/dashboard`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch dashboard summary.');
  }
  return data;
}

// Planner APIs
export async function createPlanApi(token: string, goals: string[]): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/planner`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ date: new Date().toISOString().slice(0, 10), goals }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create learning plan.');
  }
  return data;
}

// Reflection APIs
export async function createReflectionApi(token: string, reflectionData: any): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/reflection`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(reflectionData),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to submit reflection.');
  }
  return data;
}

// Recommendations API
export async function getRecommendationsApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/recommendation`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch recommendations.');
  }
  return data;
}

export async function refreshRecommendationsApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/recommendation/refresh`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to trigger Learning Curator Agent.');
  }
  return data;
}

// Opportunities API
export async function getOpportunitiesApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/opportunity`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch opportunities.');
  }
  return data;
}

// Notifications API
export async function getNotificationsApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/notification`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch notifications.');
  }
  return data;
}

export async function markNotificationReadApi(token: string, notificationId: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/notification/${notificationId}/read`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to mark notification as read.');
  }
  return data;
}

export async function markAllNotificationsReadApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/notification/read-all`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to mark all notifications as read.');
  }
  return data;
}

// Analytics API
export async function getAnalyticsApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/analytics`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch analytics.');
  }
  return data.data || data;
}

// Task Toggle API
export async function toggleTaskApi(token: string, taskId: string, completed: boolean): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/planner/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ completed }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update task completion state.');
  }
  return data;
}

export async function getPlansApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/planner`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch planner entries.');
  }
  return data;
}

export async function getReflectionsApi(token: string): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/reflection`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch reflections.');
  }
  return data;
}

export interface CopilotResponse {
  agent: string;
  message: string;
  data?: unknown;
}

export async function chatWithCopilotApi(token: string, message: string): Promise<CopilotResponse> {
  const response = await safeFetch(`${API_BASE_URL}/copilot/chat`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  const raw = await response.text();
  let data: CopilotResponse | { detail?: string } = {};
  try {
    data = raw ? JSON.parse(raw) : {};
  } catch {
    throw new Error(`The AI Copilot returned an unexpected server response (${response.status}).`);
  }
  const errorDetail = 'detail' in data ? data.detail : undefined;
  if (!response.ok) throw new Error(errorDetail || 'The AI Copilot could not complete that request.');
  return data as CopilotResponse;
}

async function institutionRequest(token: string, path: string, method = 'GET', body?: unknown): Promise<any> {
  const response = await safeFetch(`${API_BASE_URL}/institutions${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'Institution request failed.');
  return data;
}

export async function claimAuthTicketApi(ticket: string): Promise<AuthTokenResponse> {
  const response = await safeFetch(`${API_BASE_URL}/auth/claim-ticket`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ ticket }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Authentication ticket exchange failed.');
  }

  return data;
}

export const getInstitutionAnalyticsApi = (token: string) => institutionRequest(token, '/analytics');
export const getCohortsApi = (token: string) => institutionRequest(token, '/cohorts');
export const createCohortApi = (token: string, payload: { name: string; year: string; branch: string; section?: string }) => institutionRequest(token, '/cohorts', 'POST', payload);
export const createAssessmentApi = (token: string, payload: unknown) => institutionRequest(token, '/assessments', 'POST', payload);
export const getAssessmentsApi = (token: string) => institutionRequest(token, '/assessments');
export const submitAssessmentApi = (token: string, assessmentId: string, answers: Record<string, number>) => institutionRequest(token, `/assessments/${assessmentId}/submissions`, 'POST', { answers });
