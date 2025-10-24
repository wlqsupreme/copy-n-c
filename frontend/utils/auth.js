/**
 * 用户认证工具类
 * 管理用户登录状态、令牌存储和API调用
 */
import config from '../config/index.js'

class AuthManager {
  constructor() {
    this.baseURL = config.apiBaseURL
    this.tokenKey = config.auth.tokenKey
    this.userKey = config.auth.userKey
  }

  /**
   * 获取存储的访问令牌
   */
  getToken() {
    return uni.getStorageSync(this.tokenKey)
  }

  /**
   * 获取存储的用户信息
   */
  getUserInfo() {
    return uni.getStorageSync(this.userKey)
  }

  /**
   * 检查用户是否已登录
   */
  isLoggedIn() {
    const token = this.getToken()
    const userInfo = this.getUserInfo()
    return !!(token && userInfo)
  }

  /**
   * 保存用户登录信息
   */
  saveAuth(token, userInfo) {
    uni.setStorageSync(this.tokenKey, token)
    uni.setStorageSync(this.userKey, userInfo)
  }

  /**
   * 清除用户登录信息
   */
  clearAuth() {
    uni.removeStorageSync(this.tokenKey)
    uni.removeStorageSync(this.userKey)
  }

  /**
   * 用户登录
   */
  async login(username, password) {
    try {
      const response = await uni.request({
        url: `${this.baseURL}${config.endpoints.login}`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          username,
          password
        }
      })

      if (response.statusCode === 200) {
        const { access_token, user } = response.data
        this.saveAuth(access_token, user)
        return {
          success: true,
          data: response.data
        }
      } else {
        return {
          success: false,
          message: response.data.detail || '登录失败'
        }
      }
    } catch (error) {
      console.error('登录API调用失败:', error)
      return {
        success: false,
        message: '网络错误，请稍后重试'
      }
    }
  }

  /**
   * 用户注册
   */
  async register(username, email, password) {
    try {
      const response = await uni.request({
        url: `${this.baseURL}${config.endpoints.register}`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        data: {
          username,
          email,
          password
        }
      })

      if (response.statusCode === 200) {
        const { access_token, user } = response.data
        this.saveAuth(access_token, user)
        return {
          success: true,
          data: response.data
        }
      } else {
        return {
          success: false,
          message: response.data.detail || '注册失败'
        }
      }
    } catch (error) {
      console.error('注册API调用失败:', error)
      return {
        success: false,
        message: '网络错误，请稍后重试'
      }
    }
  }

  /**
   * 用户登出
   */
  async logout() {
    try {
      const token = this.getToken()
      if (token) {
        await uni.request({
          url: `${this.baseURL}${config.endpoints.logout}`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
      }
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      this.clearAuth()
    }
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser() {
    try {
      const token = this.getToken()
      if (!token) {
        return {
          success: false,
          message: '用户未登录'
        }
      }

      const response = await uni.request({
        url: `${this.baseURL}${config.endpoints.me}`,
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.statusCode === 200) {
        return {
          success: true,
          data: response.data
        }
      } else {
        // 令牌可能已过期，清除本地存储
        this.clearAuth()
        return {
          success: false,
          message: '用户认证已过期，请重新登录'
        }
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return {
        success: false,
        message: '网络错误，请稍后重试'
      }
    }
  }

  /**
   * 刷新访问令牌
   */
  async refreshToken() {
    try {
      const token = this.getToken()
      if (!token) {
        return {
          success: false,
          message: '用户未登录'
        }
      }

      const response = await uni.request({
        url: `${this.baseURL}${config.endpoints.refresh}`,
        method: 'POST',
        header: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.statusCode === 200) {
        const { access_token, user } = response.data
        this.saveAuth(access_token, user)
        return {
          success: true,
          data: response.data
        }
      } else {
        this.clearAuth()
        return {
          success: false,
          message: '令牌刷新失败，请重新登录'
        }
      }
    } catch (error) {
      console.error('刷新令牌失败:', error)
      return {
        success: false,
        message: '网络错误，请稍后重试'
      }
    }
  }

  /**
   * 带认证的API请求
   */
  async authenticatedRequest(options) {
    const token = this.getToken()
    if (!token) {
      throw new Error('用户未登录')
    }

    const defaultOptions = {
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }

    const requestOptions = {
      ...defaultOptions,
      ...options,
      header: {
        ...defaultOptions.header,
        ...options.header
      }
    }

    try {
      const response = await uni.request(requestOptions)
      
      // 如果返回401，尝试刷新令牌
      if (response.statusCode === 401) {
        const refreshResult = await this.refreshToken()
        if (refreshResult.success) {
          // 重新发送请求
          requestOptions.header.Authorization = `Bearer ${this.getToken()}`
          return await uni.request(requestOptions)
        } else {
          throw new Error('认证已过期，请重新登录')
        }
      }

      return response
    } catch (error) {
      console.error('认证请求失败:', error)
      throw error
    }
  }
}

// 创建全局实例
const authManager = new AuthManager()

// 导出
export default authManager
