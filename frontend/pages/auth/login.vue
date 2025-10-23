<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <button class="back-btn" @click="goBack">←</button>
        <text class="page-title">登录</text>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- Logo 区域 -->
      <view class="logo-section">
        <view class="logo-icon">
          <view class="icon-gradient">
            <text class="icon-text">N</text>
          </view>
        </view>
        <text class="welcome-title">欢迎回来</text>
        <text class="welcome-subtitle">登录你的账户，继续创作之旅</text>
      </view>

      <!-- 登录表单 -->
      <view class="form-section">
        <view class="form-group">
          <text class="form-label">用户名或邮箱</text>
          <input 
            class="form-input" 
            v-model="loginForm.username" 
            placeholder="请输入用户名或邮箱"
            :class="{ 'error': errors.username }"
          />
          <text class="error-text" v-if="errors.username">{{ errors.username }}</text>
        </view>
        
        <view class="form-group">
          <text class="form-label">密码</text>
          <input 
            class="form-input" 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            :class="{ 'error': errors.password }"
          />
          <text class="error-text" v-if="errors.password">{{ errors.password }}</text>
        </view>

        <view class="form-options">
          <view class="remember-me">
            <checkbox v-model="rememberMe" />
            <text class="option-text">记住我</text>
          </view>
          <text class="forgot-password" @click="showForgotPassword">忘记密码？</text>
        </view>

        <button class="login-btn" @click="handleLogin" :disabled="isLoading">
          <text v-if="isLoading">登录中...</text>
          <text v-else>登录</text>
        </button>

        <view class="divider">
          <text class="divider-text">或</text>
        </view>

        <view class="social-login">
          <button class="social-btn google-btn">
            <text class="social-icon">G</text>
            <text class="social-text">使用 Google 登录</text>
          </button>
          <button class="social-btn github-btn">
            <text class="social-icon">G</text>
            <text class="social-text">使用 GitHub 登录</text>
          </button>
        </view>

        <view class="signup-link">
          <text class="link-text">还没有账户？</text>
          <text class="link-btn" @click="goToRegister">立即注册</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rememberMe: false,
      isLoading: false,
      errors: {}
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack()
    },
    
    goToRegister() {
      uni.navigateTo({
        url: '/pages/auth/register'
      })
    },
    
    showForgotPassword() {
      uni.showToast({
        title: '忘记密码功能开发中',
        icon: 'none'
      })
    },
    
    validateForm() {
      this.errors = {}
      
      if (!this.loginForm.username) {
        this.errors.username = '请输入用户名或邮箱'
      } else if (!this.isValidEmail(this.loginForm.username) && this.loginForm.username.length < 3) {
        this.errors.username = '用户名至少3个字符'
      }
      
      if (!this.loginForm.password) {
        this.errors.password = '请输入密码'
      } else if (this.loginForm.password.length < 6) {
        this.errors.password = '密码至少6个字符'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },
    
    async handleLogin() {
      if (!this.validateForm()) {
        return
      }
      
      this.isLoading = true
      
      try {
        // 这里可以添加实际的登录API调用
        // const response = await this.loginAPI(this.loginForm)
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        // 登录成功后跳转到首页
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/index/index'
          })
        }, 1500)
        
      } catch (error) {
        uni.showToast({
          title: '登录失败，请检查用户名和密码',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #ffffff;
}

.header {
  display: flex;
  align-items: center;
  padding: 40rpx 60rpx;
  background-color: transparent;
}

.back-btn {
  width: 60rpx;
  height: 60rpx;
  background-color: #f5f5f5;
  color: #333333;
  border: none;
  border-radius: 50%;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #000000;
}

.main-content {
  padding: 60rpx;
  max-width: 600rpx;
  margin: 0 auto;
}

.logo-section {
  text-align: center;
  margin-bottom: 80rpx;
}

.logo-icon {
  margin-bottom: 40rpx;
}

.icon-gradient {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.icon-text {
  font-size: 50rpx;
  font-weight: bold;
  color: #ffffff;
}

.welcome-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #000000;
  display: block;
  margin-bottom: 20rpx;
}

.welcome-subtitle {
  font-size: 28rpx;
  color: #666666;
  display: block;
}

.form-section {
  width: 100%;
}

.form-group {
  margin-bottom: 40rpx;
}

.form-label {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
  display: block;
  margin-bottom: 15rpx;
}

.form-input {
  width: 100%;
  height: 100rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 12rpx;
  padding: 0 30rpx;
  font-size: 32rpx;
  box-sizing: border-box;
  background-color: #ffffff;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  border-color: #667eea;
  outline: none;
}

.form-input.error {
  border-color: #ff4757;
}

.error-text {
  font-size: 24rpx;
  color: #ff4757;
  display: block;
  margin-top: 10rpx;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 60rpx;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.option-text {
  font-size: 28rpx;
  color: #666666;
}

.forgot-password {
  font-size: 28rpx;
  color: #667eea;
  cursor: pointer;
}

.login-btn {
  width: 100%;
  height: 100rpx;
  background-color: #000000;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 40rpx;
  transition: opacity 0.3s ease;
}

.login-btn:disabled {
  opacity: 0.6;
}

.divider {
  position: relative;
  text-align: center;
  margin: 40rpx 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1rpx;
  background-color: #e0e0e0;
}

.divider-text {
  background-color: #ffffff;
  padding: 0 30rpx;
  font-size: 24rpx;
  color: #999999;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 60rpx;
}

.social-btn {
  width: 100%;
  height: 100rpx;
  border: 2rpx solid #e0e0e0;
  border-radius: 12rpx;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  font-size: 28rpx;
  color: #333333;
}

.social-icon {
  width: 40rpx;
  height: 40rpx;
  background-color: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: bold;
}

.signup-link {
  text-align: center;
}

.link-text {
  font-size: 28rpx;
  color: #666666;
}

.link-btn {
  font-size: 28rpx;
  color: #667eea;
  font-weight: bold;
  margin-left: 10rpx;
  cursor: pointer;
}

/* 响应式设计 */
@media (max-width: 750rpx) {
  .main-content {
    padding: 40rpx 30rpx;
  }
  
  .welcome-title {
    font-size: 40rpx;
  }
}
</style>
