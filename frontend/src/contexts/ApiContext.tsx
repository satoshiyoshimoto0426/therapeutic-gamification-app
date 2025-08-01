import React, { createContext, useContext, ReactNode } from 'react'
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

interface ApiContextType {
  api: AxiosInstance
  get: (url: string, config?: AxiosRequestConfig) => Promise<any>
  post: (url: string, data?: any, config?: AxiosRequestConfig) => Promise<any>
  put: (url: string, data?: any, config?: AxiosRequestConfig) => Promise<any>
  delete: (url: string, config?: AxiosRequestConfig) => Promise<any>
}

const ApiContext = createContext<ApiContextType | undefined>(undefined)

export const useApi = () => {
  const context = useContext(ApiContext)
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider')
  }
  return context
}

interface ApiProviderProps {
  children: ReactNode
}

export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  // Create axios instance
  const api = axios.create({
    baseURL: '/api',
    timeout: 10000,
  })

  // Request interceptor to add auth token
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor for error handling
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )

  // Convenience methods
  const get = (url: string, config?: AxiosRequestConfig) => api.get(url, config)
  const post = (url: string, data?: any, config?: AxiosRequestConfig) => api.post(url, data, config)
  const put = (url: string, data?: any, config?: AxiosRequestConfig) => api.put(url, data, config)
  const del = (url: string, config?: AxiosRequestConfig) => api.delete(url, config)

  const value = {
    api,
    get,
    post,
    put,
    delete: del
  }

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  )
}