import React, { useState } from 'react';
import { AuthLayout, Button, PasswordInput } from './AuthLayout';
import { 
  Mail, 
  ArrowRight, 
  AlertCircle,
  Building,
  ArrowLeft,
  CheckCircle
} from 'lucide-react';

interface LoginFlowProps {
  onLogin: (userData: any) => void;
  onShowOnboarding: () => void;
}

type LoginStep = 'email' | 'password' | 'organization';

export const LoginFlow: React.FC<LoginFlowProps> = ({ onLogin, onShowOnboarding }) => {
  const [currentStep, setCurrentStep] = useState<LoginStep>('email');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [organizations, setOrganizations] = useState<any[]>([]);

  const handleEmailSubmit = async () => {
    if (!email.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Check if user exists and get their organizations
      // For now, we'll simulate this - in production, you'd call an API
      // that returns organizations for this email
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock response - in production, call: /api/auth/check-email
      const mockOrgs = [
        { org_id: '123', org_name: 'Acme Corp', domain: 'acme.com', role: 'admin' },
        { org_id: '456', org_name: 'TechStart Inc', domain: 'techstart.io', role: 'employee' }
      ];
      
      if (mockOrgs.length === 0) {
        // No organizations found - redirect to onboarding
        setError('No account found with this email. Would you like to create one?');
        return;
      } else if (mockOrgs.length === 1) {
        // Single organization - go directly to password
        setOrganizations(mockOrgs);
        setCurrentStep('password');
      } else {
        // Multiple organizations - show selection
        setOrganizations(mockOrgs);
        setCurrentStep('organization');
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (selectedOrgId?: string) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          org_id: selectedOrgId
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
              onClick={() => handleLogin(organizations[0]?.org_id)} 
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

  const renderOrganizationStep = () => (
    <AuthLayout
      title="Select Organization"
      subtitle={`Choose which organization to sign in to`}
    >
      <div className="space-y-6">
        <div className="space-y-3">
          {organizations.map((org) => (
            <button
              key={org.org_id}
              onClick={() => setCurrentStep('password')}
              className="w-full p-4 border-2 border-gray-200 rounded-xl hover:border-indigo-300 hover:bg-indigo-50 transition-all text-left group"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="p-2 bg-gray-100 group-hover:bg-indigo-100 rounded-lg transition-colors">
                    <Building className="h-5 w-5 text-gray-600 group-hover:text-indigo-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{org.org_name}</div>
                    <div className="text-sm text-gray-500">{org.domain}</div>
                    <div className="text-xs text-indigo-600 font-medium mt-1">
                      {org.role === 'admin' ? '👑 Administrator' : '👤 Team Member'}
                    </div>
                  </div>
                </div>
                <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-indigo-500 transition-colors" />
              </div>
            </button>
          ))}
        </div>

        <Button 
          onClick={() => setCurrentStep('email')} 
          variant="outline" 
          className="w-full"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Email
        </Button>
      </div>
    </AuthLayout>
  );

  switch (currentStep) {
    case 'email':
      return renderEmailStep();
    case 'password':
      return renderPasswordStep();
    case 'organization':
      return renderOrganizationStep();
    default:
      return renderEmailStep();
  }
};