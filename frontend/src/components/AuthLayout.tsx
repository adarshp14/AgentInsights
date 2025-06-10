import React, { useState } from 'react';
import { Brain, Sparkles, ArrowRight, Eye, EyeOff, Building, Users, Zap } from 'lucide-react';

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
  showLogo?: boolean;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  title, 
  subtitle, 
  showLogo = true 
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex">
      {/* Left Side - Branding & Features */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-purple-600 to-blue-700 p-12 flex-col justify-between relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='7' cy='7' r='7'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }} />
        </div>
        
        {/* Logo & Brand */}
        {showLogo && (
          <div className="relative z-10">
            <div className="flex items-center space-x-3 mb-8">
              <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                <Brain className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">InsightFlow</h1>
                <p className="text-blue-100 text-sm">AI-Powered Knowledge Hub</p>
              </div>
            </div>
          </div>
        )}

        {/* Features */}
        <div className="relative z-10 space-y-8">
          <div>
            <h2 className="text-3xl font-bold text-white mb-6">
              Transform Your Team's Knowledge
            </h2>
            <p className="text-blue-100 text-lg leading-relaxed">
              Unlock the power of AI-driven insights with secure, organization-wide knowledge management that scales with your team.
            </p>
          </div>

          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-white/20 backdrop-blur-sm rounded-lg">
                <Building className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Multi-Tenant Architecture</h3>
                <p className="text-blue-100 text-sm">Complete data isolation and security for every organization</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-white/20 backdrop-blur-sm rounded-lg">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Lightning Fast RAG</h3>
                <p className="text-blue-100 text-sm">Instant answers from your documents with advanced AI</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-white/20 backdrop-blur-sm rounded-lg">
                <Users className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Team Collaboration</h3>
                <p className="text-blue-100 text-sm">Role-based access and seamless team workflows</p>
              </div>
            </div>
          </div>
        </div>

        {/* Testimonial */}
        <div className="relative z-10">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <p className="text-white italic mb-4">
              "InsightFlow transformed how our team accesses and shares knowledge. Setup took minutes, impact was immediate."
            </p>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold text-sm">SF</span>
              </div>
              <div>
                <p className="text-white font-medium">Sarah Foster</p>
                <p className="text-blue-100 text-sm">Head of Operations, TechCorp</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Auth Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
            <div className="text-center mb-8">
              {/* Mobile Logo */}
              <div className="lg:hidden flex items-center justify-center space-x-2 mb-6">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Brain className="h-6 w-6 text-indigo-600" />
                </div>
                <span className="text-xl font-bold text-gray-900">InsightFlow</span>
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
              <p className="text-gray-600">{subtitle}</p>
            </div>

            {children}
          </div>

          {/* Security Badge */}
          <div className="mt-8 text-center">
            <div className="inline-flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-full"></div>
              </div>
              <span>Enterprise-grade security</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Password Input Component
interface PasswordInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export const PasswordInput: React.FC<PasswordInputProps> = ({
  value,
  onChange,
  placeholder = "Password",
  className = ""
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="relative">
      <input
        type={showPassword ? "text" : "password"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 pr-12 ${className}`}
      />
      <button
        type="button"
        onClick={() => setShowPassword(!showPassword)}
        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
      >
        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
      </button>
    </div>
  );
};

// Button Component
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit';
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = ""
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variantClasses = {
    primary: "bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg hover:shadow-xl",
    secondary: "bg-gray-100 hover:bg-gray-200 text-gray-900",
    outline: "border-2 border-gray-300 hover:border-gray-400 text-gray-700 bg-white hover:bg-gray-50"
  };
  
  const sizeClasses = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg"
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {loading ? (
        <>
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      ) : (
        children
      )}
    </button>
  );
};