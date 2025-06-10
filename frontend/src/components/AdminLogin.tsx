import React, { useState } from 'react';
import { Shield, Eye, EyeOff, Lock, User, AlertCircle } from 'lucide-react';

interface AdminLoginProps {
  onLogin: (token: string) => void;
}

export const AdminLogin: React.FC<AdminLoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password
        })
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        // Store token in localStorage
        localStorage.setItem('admin_token', data.access_token);
        onLogin(data.access_token);
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <Shield className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Admin Login</h2>
          <p className="mt-2 text-gray-600">
            Access the InsightFlow admin dashboard
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white shadow-xl rounded-lg p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Authentication Error</h3>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  disabled={isLoading}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* Password field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  disabled={isLoading}
                  className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  disabled={isLoading}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading || !username.trim() || !password.trim()}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Default credentials info */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-sm font-medium text-blue-800 mb-2">Default Credentials</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p><strong>Username:</strong> admin</p>
              <p><strong>Password:</strong> admin123</p>
            </div>
            <p className="text-xs text-blue-600 mt-2">
              ⚠️ Please change the default password in production
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>InsightFlow Admin Dashboard v3.0.0</p>
          <p className="mt-1">Secure authentication required</p>
        </div>
      </div>
    </div>
  );
};