'use client';

/**
 * TaskList component for displaying all user tasks.
 * Fetches tasks from API, handles loading/error states, and shows empty state.
 * Includes search and filter functionality.
 */

import { useState, useEffect, useMemo } from 'react';
import { tasksApi, ApiError } from '@/lib/api';
import type { Task } from '@/lib/types';
import TaskItem from './TaskItem';
import TaskFilters from './TaskFilters';

interface TaskListProps {
  refreshTrigger?: number;
}

export default function TaskList({ refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'completed'>('all');

  /**
   * Fetch tasks from API
   */
  const fetchTasks = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await tasksApi.getTasks();
      setTasks(response.data.tasks);
    } catch (error) {
      if (error instanceof ApiError) {
        setError(error.message);
      } else {
        setError('Failed to load tasks. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle task update
   */
  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  /**
   * Handle task deletion
   */
  const handleTaskDeleted = (taskId: string) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  /**
   * Add new task to the list (for optimistic updates)
   */
  const addTask = (newTask: Task) => {
    setTasks((prevTasks) => [newTask, ...prevTasks]);
  };

  // Fetch tasks on mount and when refreshTrigger changes
  useEffect(() => {
    fetchTasks();
  }, [refreshTrigger]);

  /**
   * Filter and search tasks
   */
  const filteredTasks = useMemo(() => {
    let filtered = tasks;

    // Apply status filter
    if (filterStatus === 'active') {
      filtered = filtered.filter((task) => !task.is_completed);
    } else if (filterStatus === 'completed') {
      filtered = filtered.filter((task) => task.is_completed);
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (task) =>
          task.title.toLowerCase().includes(query) ||
          (task.description && task.description.toLowerCase().includes(query))
      );
    }

    return filtered;
  }, [tasks, filterStatus, searchQuery]);

  /**
   * Calculate task counts for filter buttons
   */
  const taskCounts = useMemo(() => {
    return {
      all: tasks.length,
      active: tasks.filter((task) => !task.is_completed).length,
      completed: tasks.filter((task) => task.is_completed).length,
    };
  }, [tasks]);

  // Loading state with skeleton loaders
  if (isLoading) {
    return (
      <div className="w-full space-y-6">
        {/* Skeleton header */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
            <div className="h-4 w-64 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
          </div>
        </div>

        {/* Skeleton filters */}
        <div className="space-y-4">
          <div className="h-12 w-full bg-gray-200 dark:bg-gray-700 rounded-xl animate-shimmer"></div>
          <div className="h-10 w-80 bg-gray-200 dark:bg-gray-700 rounded-xl animate-shimmer"></div>
        </div>

        {/* Skeleton task cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200/50 dark:border-gray-700/50"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex items-start gap-4">
                {/* Skeleton checkbox */}
                <div className="w-7 h-7 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer flex-shrink-0"></div>

                {/* Skeleton content */}
                <div className="flex-1 space-y-3">
                  <div className="h-6 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
                  <div className="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>
                  <div className="h-4 w-5/6 bg-gray-200 dark:bg-gray-700 rounded animate-shimmer"></div>

                  {/* Skeleton badges */}
                  <div className="flex gap-2">
                    <div className="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
                    <div className="h-6 w-16 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
                  </div>
                </div>

                {/* Skeleton action buttons */}
                <div className="flex gap-1 flex-shrink-0">
                  <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
                  <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="w-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-8 border border-red-200 dark:border-red-800">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 mb-4">
            <svg
              className="w-8 h-8 text-red-600 dark:text-red-400"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Failed to Load Tasks
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">{error}</p>
          <button
            onClick={fetchTasks}
            className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (tasks.length === 0) {
    return (
      <div className="w-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-12 border border-gray-200/50 dark:border-gray-700/50">
        <div className="text-center max-w-md mx-auto">
          {/* Animated icon */}
          <div className="relative inline-flex items-center justify-center w-24 h-24 mb-6">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full opacity-10 animate-pulse"></div>
            <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
              </svg>
            </div>
          </div>

          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Your task list is empty
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
            Start organizing your day by creating your first task. Use the chat below to add tasks with natural language!
          </p>

          {/* Quick tips */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4 border border-blue-100 dark:border-blue-800/50">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">💡 Quick tips:</p>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1 text-left">
              <li>• Try: "Add task to buy groceries tomorrow"</li>
              <li>• Try: "Create urgent task for project deadline"</li>
              <li>• Try: "Show my productivity stats"</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  // Task list with filters
  return (
    <div className="w-full space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            Your Tasks
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Manage your tasks with AI-powered features
          </p>
        </div>
        <button
          onClick={fetchTasks}
          className="p-2.5 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Refresh tasks"
          title="Refresh tasks"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>

      {/* Task Filters */}
      <TaskFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        filterStatus={filterStatus}
        onFilterChange={setFilterStatus}
        taskCounts={taskCounts}
      />

      {/* Filtered results info */}
      {filteredTasks.length === 0 && (searchQuery || filterStatus !== 'all') ? (
        <div className="w-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl p-8 border border-gray-200/50 dark:border-gray-700/50">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
              <svg
                className="w-8 h-8 text-gray-600 dark:text-gray-400"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No tasks found
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Try adjusting your search or filters
            </p>
          </div>
        </div>
      ) : (
        <>
          {/* Results count */}
          <div className="flex items-center gap-2 text-sm">
            <span className="px-3 py-1.5 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg font-medium text-gray-700 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50">
              {filteredTasks.length} of {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
            </span>
          </div>

          {/* Task Grid - Responsive layout with animation */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-fade-in">
            {filteredTasks.map((task, index) => (
              <div
                key={task.id}
                style={{
                  animationDelay: `${index * 50}ms`,
                  animationFillMode: 'backwards'
                }}
                className="animate-slide-up"
              >
                <TaskItem
                  task={task}
                  onTaskUpdated={handleTaskUpdated}
                  onTaskDeleted={handleTaskDeleted}
                />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
