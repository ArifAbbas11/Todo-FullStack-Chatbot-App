'use client';

/**
 * TaskItem component for displaying individual task details.
 * Shows title, description, completion status, and action buttons (edit, delete).
 */

import { useState } from 'react';
import { tasksApi, ApiError } from '@/lib/api';
import type { Task } from '@/lib/types';
import EditTaskModal from './EditTaskModal';
import DeleteConfirmModal from './DeleteConfirmModal';
import { useToast } from '@/lib/toast';

interface TaskItemProps {
  task: Task;
  onTaskUpdated?: (task: Task) => void;
  onTaskDeleted?: (taskId: string) => void;
}

export default function TaskItem({ task, onTaskUpdated, onTaskDeleted }: TaskItemProps) {
  const { success, error: showErrorToast } = useToast();
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string>('');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  /**
   * Handle task completion toggle
   */
  const handleToggle = async () => {
    setError('');
    setIsToggling(true);

    try {
      const response = await tasksApi.toggleTask(task.id);

      // Show success toast
      success(
        response.data.task.is_completed
          ? 'Task marked as completed!'
          : 'Task marked as incomplete!'
      );

      // Notify parent component
      if (onTaskUpdated) {
        onTaskUpdated(response.data.task);
      }
    } catch (error) {
      const errorMsg = error instanceof ApiError
        ? error.message
        : 'Failed to update task. Please try again.';
      setError(errorMsg);
      showErrorToast(errorMsg);
    } finally {
      setIsToggling(false);
    }
  };

  /**
   * Handle task update from EditTaskModal
   */
  const handleTaskUpdatedFromModal = (updatedTask: Task) => {
    if (onTaskUpdated) {
      onTaskUpdated(updatedTask);
    }
  };

  /**
   * Handle task deletion from DeleteConfirmModal
   */
  const handleTaskDeletedFromModal = (taskId: string) => {
    if (onTaskDeleted) {
      onTaskDeleted(taskId);
    }
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString: string): string => {
    // Parse the date string as UTC by adding 'Z' if not present
    const dateStr = dateString.endsWith('Z') ? dateString : `${dateString}Z`;
    const date = new Date(dateStr);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = diffInMs / (1000 * 60 * 60);

    if (diffInHours < 1) {
      const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
      return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes} minutes ago`;
    } else if (diffInHours < 24) {
      const hours = Math.floor(diffInHours);
      return hours === 1 ? '1 hour ago' : `${hours} hours ago`;
    } else if (diffInHours < 48) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
      });
    }
  };

  /**
   * Format due date and determine status
   */
  const getDueDateInfo = (dueDateString: string | null) => {
    if (!dueDateString) return null;

    const dueDate = new Date(dueDateString);
    const now = new Date();
    const diffInMs = dueDate.getTime() - now.getTime();
    const diffInDays = Math.ceil(diffInMs / (1000 * 60 * 60 * 24));

    let status: 'overdue' | 'soon' | 'future' = 'future';
    let color = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';

    if (diffInDays < 0) {
      status = 'overdue';
      color = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
    } else if (diffInDays <= 3) {
      status = 'soon';
      color = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
    }

    const formattedDate = dueDate.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: dueDate.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });

    return { status, color, formattedDate, diffInDays };
  };

  /**
   * Get priority color and emoji
   */
  const getPriorityInfo = (priority: string | null) => {
    if (!priority) return null;

    const priorityMap = {
      urgent: { emoji: '🔴', color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' },
      high: { emoji: '🟠', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' },
      medium: { emoji: '🟡', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' },
      low: { emoji: '🟢', color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' },
    };

    return priorityMap[priority as keyof typeof priorityMap] || null;
  };

  const dueDateInfo = getDueDateInfo(task.due_date);
  const priorityInfo = getPriorityInfo(task.priority);

  return (
    <>
      <div className="group relative bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-4 sm:p-6 border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-500/50">
        {/* Gradient overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 dark:from-blue-500/10 dark:to-purple-500/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

        <div className="relative flex items-start gap-3 sm:gap-4">
        {/* Completion Checkbox with animation */}
        <div className="flex-shrink-0 pt-1">
          <button
            type="button"
            onClick={handleToggle}
            disabled={isToggling}
            className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed min-w-[28px] min-h-[28px] ${
              task.is_completed
                ? 'bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg shadow-green-500/30 animate-bounce-scale'
                : 'border-2 border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 hover:scale-110'
            }`}
            aria-label={task.is_completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            {task.is_completed && (
              <svg
                className="w-5 h-5 text-white animate-checkmark"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2.5"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M5 13l4 4L19 7"></path>
              </svg>
            )}
          </button>
        </div>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-semibold mb-1 break-words transition-colors ${
              task.is_completed
                ? 'text-gray-500 dark:text-gray-400 line-through'
                : 'text-gray-900 dark:text-white'
            }`}
          >
            {task.title}
          </h3>

          {task.description && (
            <p
              className={`text-sm mb-3 break-words whitespace-pre-wrap ${
                task.is_completed
                  ? 'text-gray-400 dark:text-gray-500'
                  : 'text-gray-600 dark:text-gray-300'
              }`}
            >
              {task.description}
            </p>
          )}

          {/* AI Enhancement Badges with modern design */}
          {(dueDateInfo || priorityInfo || task.category || (task.tags && task.tags.length > 0)) && (
            <div className="flex flex-wrap gap-2 mb-3">
              {/* Due Date Badge */}
              {dueDateInfo && (
                <span className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm ${dueDateInfo.color}`}>
                  <svg className="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {dueDateInfo.formattedDate}
                  {dueDateInfo.status === 'overdue' && ' (Overdue)'}
                  {dueDateInfo.status === 'soon' && dueDateInfo.diffInDays === 0 && ' (Today)'}
                  {dueDateInfo.status === 'soon' && dueDateInfo.diffInDays === 1 && ' (Tomorrow)'}
                </span>
              )}

              {/* Priority Badge */}
              {priorityInfo && (
                <span className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold shadow-sm ${priorityInfo.color}`}>
                  <span className="mr-1.5">{priorityInfo.emoji}</span>
                  {task.priority?.charAt(0).toUpperCase()}{task.priority?.slice(1)}
                </span>
              )}

              {/* Category Badge */}
              {task.category && (
                <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-blue-700 dark:text-blue-300 border border-blue-500/20 dark:border-blue-400/20">
                  <svg className="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  {task.category.charAt(0).toUpperCase()}{task.category.slice(1)}
                </span>
              )}

              {/* Tags */}
              {task.tags && task.tags.length > 0 && task.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-700/50 dark:text-gray-300 border border-gray-200 dark:border-gray-600"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <time dateTime={task.created_at}>
              {formatDate(task.created_at)}
            </time>
            {task.updated_at !== task.created_at && (
              <>
                <span>•</span>
                <time dateTime={task.updated_at}>
                  Updated {formatDate(task.updated_at)}
                </time>
              </>
            )}
          </div>
        </div>

        {/* Action Buttons with modern design */}
        <div className="flex-shrink-0 flex gap-1">
          {/* Edit Button */}
          <button
            type="button"
            onClick={() => setIsEditModalOpen(true)}
            disabled={isToggling}
            className="p-2.5 text-gray-600 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed min-w-[40px] min-h-[40px] flex items-center justify-center"
            aria-label="Edit task"
            title="Edit task"
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
              <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
          </button>

          {/* Delete Button */}
          <button
            type="button"
            onClick={() => setIsDeleteModalOpen(true)}
            disabled={isToggling}
            className="p-2.5 text-gray-600 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed min-w-[40px] min-h-[40px] flex items-center justify-center"
            aria-label="Delete task"
            title="Delete task"
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
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg backdrop-blur-sm">
          <p className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </p>
        </div>
      )}
      </div>

      {/* Edit Task Modal */}
      <EditTaskModal
        task={task}
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onTaskUpdated={handleTaskUpdatedFromModal}
      />

      {/* Delete Confirm Modal */}
      <DeleteConfirmModal
        taskId={task.id}
        taskTitle={task.title}
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onTaskDeleted={handleTaskDeletedFromModal}
      />
    </>
  );
}
