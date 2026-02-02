'use client';

/**
 * Modern Header component with gradient background and premium design
 */

import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getAuthUser, clearAuth, isAuthenticated } from '@/lib/auth';
import type { AuthUser } from '@/lib/auth';
import ThemeToggle from './ThemeToggle';

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [mounted, setMounted] = useState(false);

  // Check authentication status on mount
  useEffect(() => {
    setMounted(true);
    if (isAuthenticated()) {
      setUser(getAuthUser());
    }
  }, []);

  // Listen for authentication changes (login/logout)
  useEffect(() => {
    const handleAuthChange = () => {
      if (isAuthenticated()) {
        setUser(getAuthUser());
      } else {
        setUser(null);
      }
    };

    window.addEventListener('authStateChanged', handleAuthChange);

    return () => {
      window.removeEventListener('authStateChanged', handleAuthChange);
    };
  }, []);

  // Handle sign out
  const handleSignOut = () => {
    clearAuth();
    // Trigger auth state change event
    window.dispatchEvent(new CustomEvent('authStateChanged'));
    router.push('/signin');
  };

  // Don't render on auth pages or before mounting (to avoid hydration mismatch)
  if (!mounted || pathname === '/signin' || pathname === '/signup') {
    return null;
  }

  // Don't render if not authenticated
  if (!user) {
    return null;
  }

  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand with gradient */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
                Todo AI
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">Smart Task Manager</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-2">
            <a
              href="/tasks"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                pathname === '/tasks'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                Tasks
              </div>
            </a>
          </nav>

          {/* User Info and Actions */}
          <div className="flex items-center gap-3">
            {/* User Email with avatar */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-semibold">
                {user.email.charAt(0).toUpperCase()}
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                {user.email}
              </p>
            </div>

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Sign Out Button */}
            <button
              onClick={handleSignOut}
              className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium text-white bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-200 shadow-lg shadow-red-500/30"
              aria-label="Sign out"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
