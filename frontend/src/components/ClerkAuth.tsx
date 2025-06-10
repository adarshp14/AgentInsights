import React from 'react';
import {
  SignedIn,
  SignedOut,
  SignInButton,
  UserButton,
  useUser,
  useOrganization,
  OrganizationSwitcher,
  CreateOrganization
} from '@clerk/clerk-react';
import { DashboardRouter } from './DashboardRouter';

interface ClerkAuthProps {
  onAuthenticated?: (user: any) => void;
}

export const ClerkAuth: React.FC<ClerkAuthProps> = ({ onAuthenticated }) => {
  const { user, isLoaded: userLoaded } = useUser();
  const { organization, isLoaded: orgLoaded } = useOrganization();

  // Show loading while Clerk is initializing
  if (!userLoaded || !orgLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  // Transform Clerk user data to match our existing format
  const transformedUser = user ? {
    user_id: user.id,
    email: user.primaryEmailAddress?.emailAddress || '',
    full_name: user.fullName || `${user.firstName} ${user.lastName}`.trim(),
    role: organization?.role === 'org:admin' ? 'admin' : 'employee',
    org_id: organization?.id || '',
    org_name: organization?.name || ''
  } : null;

  return (
    <>
      <SignedOut>
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full space-y-8">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">AgentInsights</h1>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">Welcome back</h2>
              <p className="text-gray-600 mb-8">
                Sign in to access your organization's AI-powered knowledge base
              </p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
              <SignInButton mode="modal">
                <button className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                  Sign In to Continue
                </button>
              </SignInButton>
              
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  New organization? 
                  <SignInButton mode="modal">
                    <button className="ml-1 text-indigo-600 hover:text-indigo-700 font-medium">
                      Create account
                    </button>
                  </SignInButton>
                </p>
              </div>
            </div>
            
            <div className="text-center text-xs text-gray-500">
              Powered by Clerk • Enterprise-grade security
            </div>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        {transformedUser && organization ? (
          <DashboardRouter 
            currentUser={transformedUser} 
            onLogout={() => {
              // Clerk handles logout automatically
            }} 
          />
        ) : (
          <OrganizationRequiredWrapper />
        )}
      </SignedIn>
    </>
  );
};

// Component to handle cases where user needs to create/join an organization
const OrganizationRequiredWrapper: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Organization Required
          </h2>
          <p className="text-gray-600 mb-8">
            You need to create or join an organization to access AgentInsights.
          </p>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
          <div className="space-y-4">
            <CreateOrganization />
            
            <div className="text-center">
              <p className="text-sm text-gray-500">
                Or switch to an existing organization:
              </p>
              <div className="mt-4">
                <OrganizationSwitcher />
              </div>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <UserButton />
        </div>
      </div>
    </div>
  );
};

export default ClerkAuth;