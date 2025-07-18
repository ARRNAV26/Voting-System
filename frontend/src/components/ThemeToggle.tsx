import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`relative w-14 h-8 flex items-center rounded-full transition-colors duration-300 focus:outline-none bg-gray-200 dark:bg-gray-700`}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      style={{ minWidth: 56 }}
    >
      {/* Track background animation */}
      <div
        className={`absolute inset-0 rounded-full transition-colors duration-300 pointer-events-none ${
          isDark ? 'bg-gradient-to-r from-blue-900 via-gray-800 to-gray-700' : 'bg-gradient-to-r from-yellow-200 via-yellow-100 to-gray-200'
        }`}
      />
      {/* Thumb */}
      <span
        className={`absolute left-1 top-1 w-6 h-6 rounded-full shadow-md flex items-center justify-center transition-transform duration-400 bg-white dark:bg-[#0a0a0a] z-10`
          + (isDark ? ' translate-x-6' : ' translate-x-0')}
        style={{ boxShadow: '0 2px 8px rgba(0,0,0,0.10)' }}
      >
        {/* Sun/Moon icon with smooth morph/scale/rotate */}
        <span className="block transition-all duration-500 ease-in-out">
          {isDark ? (
            <svg
              className="w-5 h-5 text-blue-400 transition-all duration-500 rotate-0 scale-100"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          ) : (
            <svg
              className="w-5 h-5 text-yellow-400 transition-all duration-500 rotate-0 scale-100"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </span>
      </span>
      {/* Decorative sun/moon on track for extra delight */}
      {!isDark && (
        <span className="absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg className="w-4 h-4 text-yellow-300 opacity-80" fill="currentColor" viewBox="0 0 20 20">
            <circle cx="10" cy="10" r="4" />
          </svg>
        </span>
      )}
      {isDark && (
        <span className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg className="w-4 h-4 text-blue-500 opacity-80" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        </span>
      )}
    </button>
  );
}; 