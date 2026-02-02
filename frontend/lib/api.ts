/**
 * API client for the Todo application.
 * Provides a fetch wrapper that automatically attaches JWT tokens to requests.
 */

import { getAuthHeader } from './auth';
import type {
  SignupRequest,
  SigninRequest,
  AuthResponse,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskResponse,
  TaskListResponse,
  ApiResponse,
  ChatMessageRequest,
  ChatMessageResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Global callback for handling unauthorized (401) responses
 * This is set by AuthProvider to handle token expiration and invalid tokens
 */
let unauthorizedHandler: (() => void) | null = null;

/**
 * Register a callback to handle 401 unauthorized responses
 * Should be called by AuthProvider on mount
 */
export function setUnauthorizedHandler(handler: () => void): void {
  unauthorizedHandler = handler;
}

/**
 * Clear the unauthorized handler
 * Should be called by AuthProvider on unmount
 */
export function clearUnauthorizedHandler(): void {
  unauthorizedHandler = null;
}

/**
 * Generic fetch wrapper with JWT token attachment and 401 response handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Merge auth headers with any provided headers
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Parse response body
    let data: any;
    const contentType = response.headers.get('content-type');
    const contentLength = response.headers.get('content-length');

    // Check if response has content
    if (contentLength === '0' || response.status === 204) {
      // No content - return empty object
      data = {};
    } else if (contentType && contentType.includes('application/json')) {
      // Try to parse JSON, but handle empty responses
      const text = await response.text();
      data = text ? JSON.parse(text) : {};
    } else {
      data = await response.text();
    }

    // Handle error responses
    if (!response.ok) {
      // Backend returns detail as object: {code, message, details}
      // Extract message from nested structure
      const errorMessage =
        data?.error?.message ||
        data?.detail?.message ||
        (typeof data?.detail === 'string' ? data?.detail : null) ||
        'An error occurred';
      const errorCode = data?.error?.code || data?.detail?.code || 'UNKNOWN_ERROR';
      const errorDetails = data?.error?.details || data?.detail?.details || {};

      // Handle 401 Unauthorized responses
      if (response.status === 401) {
        // Trigger unauthorized handler if registered (from AuthProvider)
        if (unauthorizedHandler) {
          unauthorizedHandler();
        }
      }

      throw new ApiError(
        errorMessage,
        response.status,
        errorCode,
        errorDetails
      );
    }

    return data as T;
  } catch (error) {
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Handle network errors
    if (error instanceof TypeError) {
      throw new ApiError(
        'Network error. Please check your connection.',
        0,
        'NETWORK_ERROR'
      );
    }

    // Handle other errors
    throw new ApiError(
      error instanceof Error ? error.message : 'An unexpected error occurred',
      500,
      'UNEXPECTED_ERROR'
    );
  }
}

/**
 * Authentication API
 */
export const authApi = {
  /**
   * Sign up a new user
   */
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Sign in an existing user
   */
  signin: async (data: SigninRequest): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/signin', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

/**
 * Tasks API
 */
export const tasksApi = {
  /**
   * Get all tasks for the authenticated user
   */
  getTasks: async (): Promise<TaskListResponse> => {
    return apiFetch<TaskListResponse>('/tasks');
  },

  /**
   * Create a new task
   */
  createTask: async (data: CreateTaskRequest): Promise<TaskResponse> => {
    return apiFetch<TaskResponse>('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update an existing task
   */
  updateTask: async (id: string, data: UpdateTaskRequest): Promise<TaskResponse> => {
    return apiFetch<TaskResponse>(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Toggle task completion status
   */
  toggleTask: async (id: string): Promise<TaskResponse> => {
    return apiFetch<TaskResponse>(`/tasks/${id}/toggle`, {
      method: 'PATCH',
    });
  },

  /**
   * Delete a task
   */
  deleteTask: async (id: string): Promise<void> => {
    return apiFetch<void>(`/tasks/${id}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Chat API
 */
export const chatApi = {
  /**
   * Send a chat message to the AI assistant
   */
  sendMessage: async (data: ChatMessageRequest): Promise<ChatMessageResponse> => {
    return apiFetch<ChatMessageResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
