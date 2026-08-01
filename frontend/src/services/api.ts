const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

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
