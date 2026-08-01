const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

export interface AuthUserResponse {
  id: string;
  name: string;
  email: string;
  created_at?: string;
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
  try {
    return await fetch(url, options);
  } catch (err: any) {
    if (err instanceof TypeError || err.message?.includes('fetch')) {
      throw new Error('Unable to connect to GrowthOS backend server. Please verify the backend API is running on port 8000.');
    }
    throw err;
  }
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
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || 'The AI Copilot could not complete that request.');
  return data;
}