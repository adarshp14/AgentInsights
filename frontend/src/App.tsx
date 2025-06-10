import { useState, useEffect } from 'react';
import { LoginFlow } from './components/LoginFlow';
import { OnboardingFlow } from './components/OnboardingFlow';
import { DashboardRouter } from './components/DashboardRouter';

type AuthState = 'login' | 'onboarding' | 'authenticated';

function App() {
  const [authState, setAuthState] = useState<AuthState>('login');
  const [userData, setUserData] = useState<any>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Check for existing authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const storedUserData = localStorage.getItem('user_data');
    
    if (token && storedUserData) {
      try {
        const user = JSON.parse(storedUserData);
        setUserData(user);
        setAuthState('authenticated');
      } catch (error) {
        // Invalid stored data, clear it
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
      }
    }
  }, []);


  const handleUserLogin = (user: any) => {
    setUserData(user);
    setAuthState('authenticated');
    setShowOnboarding(false);
  };

  const handleUserLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    setUserData(null);
    setAuthState('login');
  };

  const handleOnboardingComplete = (orgData: any) => {
    // Auto-login after successful organization creation
    if (orgData.user && orgData.token) {
      localStorage.setItem('auth_token', orgData.token.access_token);
      localStorage.setItem('user_data', JSON.stringify(orgData.user));
      handleUserLogin(orgData.user);
    }
  };

  const handleShowOnboarding = () => {
    setShowOnboarding(true);
  };

  const handleBackToLogin = () => {
    setShowOnboarding(false);
  };

  // Show onboarding flow
  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  // Show login flow if not authenticated
  if (authState === 'login') {
    return (
      <LoginFlow 
        onLogin={handleUserLogin} 
        onShowOnboarding={handleShowOnboarding}
      />
    );
  }

  // Show role-based dashboard for authenticated users
  if (authState === 'authenticated' && userData) {
    return (
      <DashboardRouter
        currentUser={userData}
        onLogout={handleUserLogout}
      />
    );
  }

  // Fallback loading state
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-2 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

export default App;