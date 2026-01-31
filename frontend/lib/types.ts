/**
 * TypeScript type definitions for the Todo application.
 * Defines interfaces for API requests and responses.
 */

// User Types
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

// Task Types
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  // AI Enhancement Fields
  due_date: string | null;
  priority: 'low' | 'medium' | 'high' | 'urgent' | null;
  category: string | null;
  tags: string[] | null;
  parent_task_id: string | null;
}

// Authentication Types
export interface SignupRequest {
  email: string;
  password: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  data: {
    user: User;
    token: string;
  };
  message: string;
  error: null;
}

// Task Types
export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title: string;
  description?: string;
}

export interface TaskResponse {
  data: {
    task: Task;
  };
  message: string;
  error: null;
}

export interface TaskListResponse {
  data: {
    tasks: Task[];
    count: number;
  };
  message: string;
  error: null;
}

// Error Types
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
}

// Chat Types
export interface ChatMessageRequest {
  message: string;
  conversation_id?: string;
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
  result?: any;
}

export interface ChatMessageResponse {
  response: string;
  conversation_id: string;
  tool_calls?: ToolCall[];
}
