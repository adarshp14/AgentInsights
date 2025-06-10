import React, { useState } from 'react';
import { AuthLayout, Button, PasswordInput } from './AuthLayout';
import { 
  Mail, 
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  CheckCircle
} from 'lucide-react';

interface LoginFlowProps {
  onLogin: (userData: any) => void;
  onShowOnboarding: () => void;
}

type LoginStep = 'email' | 'password';

export const LoginFlow: React.FC<LoginFlowProps> = ({ onLogin, onShowOnboarding }) => {
  const [currentStep, setCurrentStep] = useState<LoginStep>('email');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailSubmit = async () => {
    if (!email.trim()) return;
    
    // Simply move to password step - our backend will handle user validation
    setCurrentStep('password');
  };

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://localhost:8001/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password
        }),
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        // Store auth token
        localStorage.setItem('auth_token', result.token.access_token);
        localStorage.setItem('user_data', JSON.stringify(result.user));
        
        onLogin(result.user);
      } else {
        setError(result.message || 'Invalid credentials');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderEmailStep = () => (
    <AuthLayout
      title="Welcome back"
      subtitle="Enter your email to continue"
    >
      <div className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div className="text-sm text-red-700">
              {error}
              {error.includes('No account found') && (
                <button
                  onClick={onShowOnboarding}
                  className="block mt-2 text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  Create new organization →
                </button>
              )}
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleEmailSubmit()}
                placeholder="Enter your email"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>

          <Button 
            onClick={handleEmailSubmit} 
            className="w-full"
            size="lg"
            loading={loading}
            disabled={!email.trim()}
          >
            Continue
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>

        <div className="text-center">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">New to InsightFlow?</span>
            </div>
          </div>
          <button
            onClick={onShowOnboarding}
            className="mt-4 text-indigo-600 hover:text-indigo-700 font-medium text-sm"
          >
            Create your organization
          </button>
        </div>
      </div>
    </AuthLayout>
  );

  const renderPasswordStep = () => (
    <AuthLayout
      title="Enter your password"
      subtitle={`Signing in as ${email}`}
    >
      <div className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div className="text-sm text-red-700">{error}</div>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <PasswordInput
              value={password}
              onChange={setPassword}
              placeholder="Enter your password"
            />
          </div>

          <div className="flex space-x-3">
            <Button 
              onClick={() => setCurrentStep('email')} 
              variant="outline" 
              className="flex-1"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>
            <Button 
              onClick={handleLogin} 
              className="flex-1"
              loading={loading}
              disabled={!password.trim()}
            >
              Sign In
            </Button>
          </div>
        </div>

        <div className="text-center">
          <button className="text-indigo-600 hover:text-indigo-700 text-sm">
            Forgot your password?
          </button>
        </div>
      </div>
    </AuthLayout>
  );


  switch (currentStep) {
    case 'email':
      return renderEmailStep();
    case 'password':
      return renderPasswordStep();
    default:
      return renderEmailStep();
  }
};