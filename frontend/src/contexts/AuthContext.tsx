import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface User {
  id: string
  name: string
  email: string
  level: number
  xp: number
  xpToNextLevel: number
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing auth token
    const token = localStorage.getItem('auth_token')
    if (token) {
      // Validate token and get user info
      fetchUserInfo(token)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUserInfo = async (token: string) => {
    try {
      // For demo purposes, validate mock token
      if (token === 'mock-jwt-token') {
        const mockUser = {
          id: '1',
          name: 'テストユーザー',
          email: 'test@example.com',
          level: 3,
          xp: 150,
          xpToNextLevel: 200,
        };
        setUser(mockUser);
      } else {
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  }

  const login = async (email: string, password: string) => {
    try {
      // For demo purposes, accept any email/password
      if (email && password) {
        const mockUser = {
          id: '1',
          name: 'テストユーザー',
          email: email,
          level: 3,
          xp: 150,
          xpToNextLevel: 200,
        };
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        localStorage.setItem('auth_token', 'mock-jwt-token');
        setUser(mockUser);
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  const value = {
    user,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}