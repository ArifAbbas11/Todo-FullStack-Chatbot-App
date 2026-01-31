'use client';

/**
 * TaskFilters component for searching and filtering tasks
 * Modern design with segmented control and debounced search
 */

import { useState, useEffect } from 'react';

interface TaskFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  filterStatus: 'all' | 'active' | 'completed';
  onFilterChange: (status: 'all' | 'active' | 'completed') => void;
  taskCounts: {
    all: number;
    active: number;
    completed: number;
  };
}

export default function TaskFilters({
  searchQuery,
  onSearchChange,
  filterStatus,
  onFilterChange,
  taskCounts
}: TaskFiltersProps) {
  const [localSearch, setLocalSearch] = useState(searchQuery);

  // Debounced search - wait 300ms after user stops typing
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(localSearch);
    }, 300);

    return () => clearTimeout(timer);
  }, [localSearch, onSearchChange]);

  // Sync with external changes
  useEffect(() => {
    setLocalSearch(searchQuery);
  }, [searchQuery]);

  return (
    <div className="space-y-4">
      {/* Modern Search Bar with smooth animation */}
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg
            className="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <input
          type="text"
          placeholder="Search tasks by title or description..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="w-full pl-10 pr-10 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200 hover:border-gray-400 dark:hover:border-gray-500"
        />
        {localSearch && (
          <button
            onClick={() => setLocalSearch('')}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            aria-label="Clear search"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Modern Segmented Control (iOS-style) */}
      <div className="relative inline-flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 w-full sm:w-auto">
        {/* Sliding background indicator */}
        <div
          className="absolute top-1 bottom-1 bg-white dark:bg-gray-700 rounded-lg shadow-sm transition-all duration-300 ease-out"
          style={{
            left: filterStatus === 'all' ? '0.25rem' : filterStatus === 'active' ? 'calc(33.333% + 0.125rem)' : 'calc(66.666% + 0.125rem)',
            width: 'calc(33.333% - 0.25rem)'
          }}
        />

        {/* Buttons */}
        <button
          onClick={() => onFilterChange('all')}
          className={`relative z-10 flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
            filterStatus === 'all'
              ? 'text-gray-900 dark:text-white'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          All
          <span className={`ml-1.5 inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-semibold ${
            filterStatus === 'all'
              ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
              : 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
          }`}>
            {taskCounts.all}
          </span>
        </button>

        <button
          onClick={() => onFilterChange('active')}
          className={`relative z-10 flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
            filterStatus === 'active'
              ? 'text-gray-900 dark:text-white'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          Active
          <span className={`ml-1.5 inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-semibold ${
            filterStatus === 'active'
              ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
              : 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
          }`}>
            {taskCounts.active}
          </span>
        </button>

        <button
          onClick={() => onFilterChange('completed')}
          className={`relative z-10 flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
            filterStatus === 'completed'
              ? 'text-gray-900 dark:text-white'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          Completed
          <span className={`ml-1.5 inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-semibold ${
            filterStatus === 'completed'
              ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
              : 'bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
          }`}>
            {taskCounts.completed}
          </span>
        </button>
      </div>

      {/* Active Filters Chips */}
      {(searchQuery || filterStatus !== 'all') && (
        <div className="flex flex-wrap items-center gap-2 animate-slide-in">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Active filters:</span>
          {searchQuery && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium border border-blue-200 dark:border-blue-800">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              "{searchQuery}"
              <button
                onClick={() => setLocalSearch('')}
                className="ml-1 hover:bg-blue-100 dark:hover:bg-blue-800 rounded-full p-0.5 transition-colors"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          {filterStatus !== 'all' && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs font-medium border border-purple-200 dark:border-purple-800">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              {filterStatus}
              <button
                onClick={() => onFilterChange('all')}
                className="ml-1 hover:bg-purple-100 dark:hover:bg-purple-800 rounded-full p-0.5 transition-colors"
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </span>
          )}
          <button
            onClick={() => {
              setLocalSearch('');
              onFilterChange('all');
            }}
            className="text-xs font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 underline decoration-dotted underline-offset-2 transition-colors"
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
