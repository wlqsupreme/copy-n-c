/**
 * 应用配置文件
 * 管理API基础URL和其他配置项
 */
const config = {
  // API基础URL
  apiBaseURL: 'http://localhost:8000',
  
  // 开发环境配置
  development: {
    apiBaseURL: 'http://localhost:8000',
    debug: true
  },
  
  // 生产环境配置
  production: {
    apiBaseURL: 'https://your-api-domain.com',
    debug: false
  }
}

// 根据环境选择配置
const env = process.env.NODE_ENV || 'development'
const currentConfig = config[env] || config.development

export default {
  ...currentConfig,
  // 认证相关配置
  auth: {
    tokenKey: 'access_token',
    userKey: 'user_info',
    tokenExpireTime: 30 * 60 * 1000 // 30分钟
  },
  
  // API端点
  endpoints: {
    login: '/api/v1/auth/login',
    register: '/api/v1/auth/register',
    logout: '/api/v1/auth/logout',
    me: '/api/v1/auth/me',
    refresh: '/api/v1/auth/refresh',
    projects: '/api/v1/projects',
    storyboard: '/api/v1/storyboard'
  }
}


