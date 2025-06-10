import React, { useState } from 'react';
import { AuthLayout, Button, PasswordInput } from './AuthLayout';
import { 
  Building, 
  Users, 
  ArrowRight, 
  CheckCircle, 
  Mail, 
  User,
  Globe,
  Sparkles,
  Rocket,
  ArrowLeft
} from 'lucide-react';

interface OnboardingFlowProps {
  onComplete: (orgData: any) => void;
}

type Step = 'welcome' | 'organization' | 'admin' | 'team' | 'complete';

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState<Step>('welcome');
  const [loading, setLoading] = useState(false);
  const [orgData, setOrgData] = useState({
    orgName: '',
    domain: '',
    planType: 'starter',
    adminName: '',
    adminEmail: '',
    adminPassword: '',
    teamSize: '1-10'
  });

  const steps: Step[] = ['welcome', 'organization', 'admin', 'team', 'complete'];
  const currentStepIndex = steps.indexOf(currentStep);

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStep(steps[currentStepIndex + 1]);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(steps[currentStepIndex - 1]);
    }
  };

  const handleCreateOrganization = async () => {
    setLoading(true);
    try {
      // Call organization registration API
      const response = await fetch('/api/organizations/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          org_name: orgData.orgName,
          domain: orgData.domain,
          plan_type: orgData.planType,
          admin_name: orgData.adminName,
          admin_email: orgData.adminEmail,
        }),
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        setCurrentStep('complete');
        // Auto-login the admin user
        setTimeout(() => {
          onComplete(result);
        }, 2000);
      } else {
        throw new Error(result.message || 'Failed to create organization');
      }
    } catch (error) {
      console.error('Error creating organization:', error);
      alert('Failed to create organization. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderWelcomeStep = () => (
    <AuthLayout
      title="Welcome to InsightFlow"
      subtitle="Let's set up your organization's AI knowledge hub"
    >
      <div className="space-y-6">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="p-4 bg-indigo-100 rounded-full">
              <Sparkles className="h-8 w-8 text-indigo-600" />
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Ready to transform your team's knowledge?
            </h3>
            <p className="text-gray-600 text-sm">
              We'll guide you through setting up your organization in just a few steps.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-gray-700">Secure multi-tenant setup</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-gray-700">AI-powered document search</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-gray-700">Team collaboration tools</span>
          </div>
        </div>

        <Button 
          onClick={handleNext} 
          className="w-full"
          size="lg"
        >
          Get Started
          <ArrowRight className="ml-2 h-5 w-5" />
        </Button>

        <p className="text-center text-xs text-gray-500">
          Already have an account? <button className="text-indigo-600 hover:text-indigo-700">Sign in</button>
        </p>
      </div>
    </AuthLayout>
  );

  const renderOrganizationStep = () => (
    <AuthLayout
      title="Create Your Organization"
      subtitle="Set up your organization's workspace"
    >
      <div className="space-y-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Organization Name *
            </label>
            <div className="relative">
              <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={orgData.orgName}
                onChange={(e) => setOrgData({ ...orgData, orgName: e.target.value })}
                placeholder="Acme Corp"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Domain (Optional)
            </label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={orgData.domain}
                onChange={(e) => setOrgData({ ...orgData, domain: e.target.value })}
                placeholder="acme.com"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Used for email-based organization detection
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Plan Type
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'starter', label: 'Starter', desc: 'Small teams' },
                { value: 'professional', label: 'Pro', desc: 'Growing teams' },
                { value: 'enterprise', label: 'Enterprise', desc: 'Large orgs' }
              ].map((plan) => (
                <button
                  key={plan.value}
                  onClick={() => setOrgData({ ...orgData, planType: plan.value })}
                  className={`p-3 rounded-lg border-2 text-center transition-all ${
                    orgData.planType === plan.value
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{plan.label}</div>
                  <div className="text-xs text-gray-500">{plan.desc}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <Button onClick={handleBack} variant="outline" className="flex-1">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button 
            onClick={handleNext} 
            className="flex-1"
            disabled={!orgData.orgName.trim()}
          >
            Continue
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </AuthLayout>
  );

  const renderAdminStep = () => (
    <AuthLayout
      title="Admin Account Setup"
      subtitle="Create your administrator account"
    >
      <div className="space-y-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Name *
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={orgData.adminName}
                onChange={(e) => setOrgData({ ...orgData, adminName: e.target.value })}
                placeholder="John Doe"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="email"
                value={orgData.adminEmail}
                onChange={(e) => setOrgData({ ...orgData, adminEmail: e.target.value })}
                placeholder="john@acme.com"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password *
            </label>
            <PasswordInput
              value={orgData.adminPassword}
              onChange={(value) => setOrgData({ ...orgData, adminPassword: value })}
              placeholder="Create a strong password"
            />
            <p className="text-xs text-gray-500 mt-1">
              Minimum 8 characters with letters and numbers
            </p>
          </div>
        </div>

        <div className="flex space-x-3">
          <Button onClick={handleBack} variant="outline" className="flex-1">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button 
            onClick={handleNext} 
            className="flex-1"
            disabled={!orgData.adminName.trim() || !orgData.adminEmail.trim() || orgData.adminPassword.length < 8}
          >
            Continue
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </AuthLayout>
  );

  const renderTeamStep = () => (
    <AuthLayout
      title="Team Setup"
      subtitle="Tell us about your team size"
    >
      <div className="space-y-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Expected Team Size
            </label>
            <div className="space-y-3">
              {[
                { value: '1-10', label: '1-10 people', desc: 'Small team or startup' },
                { value: '11-50', label: '11-50 people', desc: 'Growing company' },
                { value: '51-200', label: '51-200 people', desc: 'Mid-size organization' },
                { value: '200+', label: '200+ people', desc: 'Large enterprise' }
              ].map((size) => (
                <button
                  key={size.value}
                  onClick={() => setOrgData({ ...orgData, teamSize: size.value })}
                  className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                    orgData.teamSize === size.value
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{size.label}</div>
                      <div className="text-sm text-gray-500">{size.desc}</div>
                    </div>
                    <Users className="h-5 w-5 text-gray-400" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <Button onClick={handleBack} variant="outline" className="flex-1">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Button 
            onClick={handleCreateOrganization} 
            className="flex-1"
            loading={loading}
          >
            Create Organization
            <Rocket className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </AuthLayout>
  );

  const renderCompleteStep = () => (
    <AuthLayout
      title="Welcome to InsightFlow!"
      subtitle="Your organization has been successfully created"
    >
      <div className="space-y-6 text-center">
        <div className="flex justify-center">
          <div className="p-4 bg-green-100 rounded-full">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-900">
            🎉 Setup Complete!
          </h3>
          <p className="text-gray-600">
            Your organization <strong>{orgData.orgName}</strong> is ready to go.
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
          <div className="font-medium text-gray-900">Next Steps:</div>
          <div className="text-left space-y-1 text-gray-600">
            <div>• Upload your first documents</div>
            <div>• Invite team members</div>
            <div>• Start asking questions!</div>
          </div>
        </div>

        <div className="text-sm text-gray-500">
          Redirecting to your dashboard...
        </div>
      </div>
    </AuthLayout>
  );

  switch (currentStep) {
    case 'welcome':
      return renderWelcomeStep();
    case 'organization':
      return renderOrganizationStep();
    case 'admin':
      return renderAdminStep();
    case 'team':
      return renderTeamStep();
    case 'complete':
      return renderCompleteStep();
    default:
      return renderWelcomeStep();
  }
};