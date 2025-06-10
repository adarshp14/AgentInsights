import React, { useState } from 'react';
import { UserButton, OrganizationSwitcher } from '@clerk/clerk-react';
import {
  Users,
  FileText,
  Settings,
  BarChart3,
  Plus,
  Bell,
  Search,
  Menu,
  X,
  Home,
  Shield,
  Upload,
  Activity,
  UserPlus,
  Building
} from 'lucide-react';

interface AdminDashboardLayoutProps {
  children: React.ReactNode;
  currentUser: {
    user_id: string;
    email: string;
    full_name: string;
    role: string;
    org_id: string;
    org_name: string;
  };
  activeTab: string;
  onTabChange: (tab: string) => void;
  onLogout: () => void;
}

interface NavigationItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  badge?: number;
}

export const AdminDashboardLayout: React.FC<AdminDashboardLayoutProps> = ({
  children,
  currentUser,
  activeTab,
  onTabChange,
  onLogout
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifications] = useState(3); // Mock notification count

  const navigationItems: NavigationItem[] = [
    {
      id: 'overview',
      name: 'Overview',
      icon: Home,
      description: 'Dashboard overview and key metrics'
    },
    {
      id: 'users',
      name: 'User Management',
      icon: Users,
      description: 'Manage organization users and permissions',
      badge: 2 // New users pending
    },
    {
      id: 'documents',
      name: 'Documents',
      icon: FileText,
      description: 'Upload and manage knowledge base documents'
    },
    {
      id: 'analytics',
      name: 'Analytics',
      icon: BarChart3,
      description: 'Usage statistics and performance metrics'
    },
    {
      id: 'settings',
      name: 'Organization Settings',
      icon: Settings,
      description: 'Configure organization preferences'
    }
  ];

  const quickActions = [
    {
      id: 'invite-user',
      name: 'Invite User',
      icon: UserPlus,
      color: 'bg-blue-500 hover:bg-blue-600',
      action: () => onTabChange('users')
    },
    {
      id: 'upload-doc',
      name: 'Upload Document',
      icon: Upload,
      color: 'bg-green-500 hover:bg-green-600',
      action: () => onTabChange('documents')
    },
    {
      id: 'view-analytics',
      name: 'View Analytics',
      icon: Activity,
      color: 'bg-purple-500 hover:bg-purple-600',
      action: () => onTabChange('analytics')
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform lg:translate-x-0 lg:static lg:inset-0 transition duration-200 ease-in-out`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Admin Panel</h1>
              <p className="text-xs text-gray-500 truncate max-w-32">{currentUser.org_name}</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-md text-gray-500 hover:text-gray-900"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* User Info */}
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
              <span className="text-indigo-600 font-semibold text-sm">
                {currentUser.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {currentUser.full_name}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {currentUser.email}
              </p>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                Administrator
              </span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onTabChange(item.id);
                    setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 group ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-sm'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600'}`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{item.name}</span>
                      {item.badge && (
                        <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 bg-red-500 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Quick Actions */}
        <div className="p-4 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Actions</h3>
          <div className="space-y-2">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <button
                  key={action.id}
                  onClick={action.action}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-white text-sm font-medium transition-colors ${action.color}`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{action.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center justify-center">
            <UserButton 
              appearance={{
                elements: {
                  avatarBox: "w-8 h-8",
                  userButtonTrigger: "focus:shadow-none"
                }
              }}
              showName={true}
              userProfileMode="navigation"
              userProfileUrl="/user-profile"
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100"
              >
                <Menu className="w-5 h-5" />
              </button>
              
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {navigationItems.find(item => item.id === activeTab)?.name || 'Dashboard'}
                </h1>
                <p className="text-sm text-gray-600">
                  {navigationItems.find(item => item.id === activeTab)?.description}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative hidden md:block">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* Notifications */}
              <button className="relative p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                <Bell className="w-5 h-5" />
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
                    {notifications}
                  </span>
                )}
              </button>

              {/* Organization Switcher */}
              <div className="hidden md:block">
                <OrganizationSwitcher 
                  appearance={{
                    elements: {
                      organizationSwitcherTrigger: "bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg px-3 py-2",
                      organizationSwitcherTriggerIcon: "text-gray-500"
                    }
                  }}
                  createOrganizationMode="navigation"
                  organizationProfileMode="navigation"
                />
              </div>

              {/* User Button */}
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-8 h-8",
                    userButtonTrigger: "focus:shadow-none"
                  }
                }}
              />
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};