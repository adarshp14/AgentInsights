import { useState, useEffect } from 'react';
import { StreamingChatInterface } from './components/StreamingChatInterface';
import { AdminDashboard } from './components/AdminDashboard';
import { AdminLogin } from './components/AdminLogin';
import { DocumentUpload } from './components/DocumentUpload';
import { RealtimeDashboard } from './components/RealtimeDashboard';
import { LoginFlow } from './components/LoginFlow';
import { OnboardingFlow } from './components/OnboardingFlow';
import { 
  MessageSquare, 
  Upload, 
  BarChart3, 
  Shield,
  FileText,
  Brain,
  Zap,
  LogOut,
  User
} from 'lucide-react';

type ViewMode = 'chat' | 'upload' | 'dashboard' | 'admin';
type AuthState = 'login' | 'onboarding' | 'authenticated' | 'admin';

interface UploadedDocument {
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunks_created: number;
  status: 'success' | 'error';
  error?: string;
}

function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('chat');
  const [authState, setAuthState] = useState<AuthState>('login');
  const [userData, setUserData] = useState<any>(null);
  const [adminToken, setAdminToken] = useState<string | null>(
    localStorage.getItem('admin_token')
  );
  const [showAdminLogin, setShowAdminLogin] = useState(false);
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

  const handleAdminLogin = (token: string) => {
    setAdminToken(token);
    setShowAdminLogin(false);
    setAuthState('admin');
  };

  const handleAdminLogout = () => {
    localStorage.removeItem('admin_token');
    setAdminToken(null);
    setAuthState('authenticated');
    setCurrentView('chat');
  };

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
    setCurrentView('chat');
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

  const handleUploadComplete = (document: UploadedDocument) => {
    console.log('Document uploaded:', document);
    // Could show a notification or update UI
  };

  const navigation = [
    {
      id: 'chat' as ViewMode,
      name: 'Chat',
      icon: MessageSquare,
      description: 'AI Assistant with streaming responses'
    },
    {
      id: 'upload' as ViewMode,
      name: 'Upload',
      icon: Upload,
      description: 'Upload documents to knowledge base'
    },
    {
      id: 'dashboard' as ViewMode,
      name: 'Analytics',
      icon: BarChart3,
      description: 'Real-time query analysis'
    }
  ];

  // Show onboarding flow
  if (showOnboarding) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  // Show admin login
  if (showAdminLogin) {
    return <AdminLogin onLogin={handleAdminLogin} />;
  }

  // Show admin dashboard
  if (authState === 'admin' && adminToken) {
    return <AdminDashboard authToken={adminToken} onLogout={handleAdminLogout} />;
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

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">InsightFlow</h1>
              <p className="text-xs text-gray-500">{userData?.organization?.org_name || 'AI Knowledge Hub'}</p>
            </div>
          </div>
        </div>

        {/* User Info */}
        {userData && (
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-indigo-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {userData.name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {userData.role === 'admin' ? '👑 Administrator' : '👤 Team Member'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  currentView === item.id
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <div>
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-gray-500">{item.description}</div>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Features */}
        <div className="p-4 border-t border-gray-200">
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Zap className="w-4 h-4 text-green-500" />
              <span>Streaming Responses</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <FileText className="w-4 h-4 text-blue-500" />
              <span>ChromaDB Vector Store</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Brain className="w-4 h-4 text-purple-500" />
              <span>Google Gemini 2.0</span>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-gray-200 space-y-2">
          <button
            onClick={() => setShowAdminLogin(true)}
            className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <Shield className="w-4 h-4" />
            <span>Admin Dashboard</span>
          </button>
          
          <button
            onClick={handleUserLogout}
            className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {navigation.find(nav => nav.id === currentView)?.name || 'InsightFlow'}
              </h2>
              <p className="text-sm text-gray-600">
                {navigation.find(nav => nav.id === currentView)?.description || 'AI Agent Platform'}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {userData && (
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{userData.name}</p>
                  <p className="text-xs text-gray-500">{userData.email}</p>
                </div>
              )}
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Online</span>
              </div>
            </div>
          </div>
        </header>

        {/* View Content */}
        <main className="flex-1 overflow-hidden">
          {currentView === 'chat' && (
            <StreamingChatInterface conversationId="default" />
          )}
          
          {currentView === 'upload' && (
            <div className="h-full overflow-y-auto p-6">
              <div className="max-w-4xl mx-auto">
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Document Upload
                  </h3>
                  <p className="text-gray-600">
                    Upload PDF, TXT, or DOCX files to expand the AI's knowledge base. 
                    Documents are automatically processed and made searchable.
                  </p>
                </div>
                <DocumentUpload onUploadComplete={handleUploadComplete} />
              </div>
            </div>
          )}
          
          {currentView === 'dashboard' && (
            <div className="h-full overflow-y-auto p-6">
              <div className="max-w-7xl mx-auto">
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Real-time Analytics
                  </h3>
                  <p className="text-gray-600">
                    Monitor query processing, system performance, and usage patterns in real-time.
                  </p>
                </div>
                <RealtimeDashboard />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;