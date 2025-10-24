<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <button class="back-btn" @click="goBack">←</button>
        <text class="page-title">注册</text>
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
        <text class="welcome-title">创建账户</text>
        <text class="welcome-subtitle">加入我们，开始你的创作之旅</text>
      </view>

      <!-- 注册表单 -->
      <view class="form-section">
        <view class="form-group">
          <text class="form-label">用户名</text>
          <input 
            class="form-input" 
            v-model="registerForm.username" 
            placeholder="请输入用户名"
            :class="{ 'error': errors.username }"
          />
          <text class="error-text" v-if="errors.username">{{ errors.username }}</text>
        </view>
        
        <view class="form-group">
          <text class="form-label">邮箱</text>
          <input 
            class="form-input" 
            v-model="registerForm.email" 
            placeholder="请输入邮箱地址"
            :class="{ 'error': errors.email }"
          />
          <text class="error-text" v-if="errors.email">{{ errors.email }}</text>
        </view>
        
        <view class="form-group">
          <text class="form-label">密码</text>
          <input 
            class="form-input" 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码"
            :class="{ 'error': errors.password }"
          />
          <text class="error-text" v-if="errors.password">{{ errors.password }}</text>
        </view>
        
        <view class="form-group">
          <text class="form-label">确认密码</text>
          <input 
            class="form-input" 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            :class="{ 'error': errors.confirmPassword }"
          />
          <text class="error-text" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</text>
        </view>

        <view class="form-options">
          <view class="agree-terms">
            <checkbox v-model="agreeTerms" />
            <text class="option-text">我同意</text>
            <text class="terms-link" @click="showTerms">《用户协议》</text>
            <text class="option-text">和</text>
            <text class="terms-link" @click="showPrivacy">《隐私政策》</text>
          </view>
        </view>

        <button class="register-btn" @click="handleRegister" :disabled="isLoading || !agreeTerms">
          <text v-if="isLoading">注册中...</text>
          <text v-else>创建账户</text>
        </button>

        <view class="divider">
          <text class="divider-text">或</text>
        </view>

        <view class="social-login">
          <button class="social-btn google-btn">
            <text class="social-icon">G</text>
            <text class="social-text">使用 Google 注册</text>
          </button>
          <button class="social-btn github-btn">
            <text class="social-icon">G</text>
            <text class="social-text">使用 GitHub 注册</text>
          </button>
        </view>

        <view class="login-link">
          <text class="link-text">已有账户？</text>
          <text class="link-btn" @click="goToLogin">立即登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import authManager from '../../utils/auth.js'

export default {
  data() {
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      agreeTerms: false,
      isLoading: false,
      errors: {}
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack()
    },
    
    goToLogin() {
      uni.navigateTo({
        url: '/pages/auth/login'
      })
    },
    
    showTerms() {
      uni.showToast({
        title: '用户协议页面开发中',
        icon: 'none'
      })
    },
    
    showPrivacy() {
      uni.showToast({
        title: '隐私政策页面开发中',
        icon: 'none'
      })
    },
    
    validateForm() {
      this.errors = {}
      
      // 验证用户名
      if (!this.registerForm.username) {
        this.errors.username = '请输入用户名'
      } else if (this.registerForm.username.length < 3) {
        this.errors.username = '用户名至少3个字符'
      } else if (!/^[a-zA-Z0-9_]+$/.test(this.registerForm.username)) {
        this.errors.username = '用户名只能包含字母、数字和下划线'
      }
      
      // 验证邮箱
      if (!this.registerForm.email) {
        this.errors.email = '请输入邮箱地址'
      } else if (!this.isValidEmail(this.registerForm.email)) {
        this.errors.email = '请输入有效的邮箱地址'
      }
      
      // 验证密码
      if (!this.registerForm.password) {
        this.errors.password = '请输入密码'
      } else if (this.registerForm.password.length < 6) {
        this.errors.password = '密码至少6个字符'
      } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(this.registerForm.password)) {
        this.errors.password = '密码必须包含字母和数字'
      }
      
      // 验证确认密码
      if (!this.registerForm.confirmPassword) {
        this.errors.confirmPassword = '请确认密码'
      } else if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.errors.confirmPassword = '两次输入的密码不一致'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },
    
    async handleRegister() {
      if (!this.validateForm()) {
        return
      }
      
      if (!this.agreeTerms) {
        uni.showToast({
          title: '请先同意用户协议和隐私政策',
          icon: 'none'
        })
        return
      }
      
      this.isLoading = true
      
      try {
        // 使用认证管理器进行注册
        const result = await authManager.register(
          this.registerForm.username,
          this.registerForm.email,
          this.registerForm.password
        )
        
        if (result.success) {
          uni.showToast({
            title: '注册成功',
            icon: 'success'
          })
          
          // 注册成功后跳转到首页
          setTimeout(() => {
            uni.reLaunch({
              url: '/pages/index/index'
            })
          }, 1500)
        } else {
          throw new Error(result.message || '注册失败')
        }
        
      } catch (error) {
        console.error('注册失败:', error)
        uni.showToast({
          title: error.message || '注册失败，请稍后重试',
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
  margin-bottom: 60rpx;
}

.agree-terms {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}

.option-text {
  font-size: 26rpx;
  color: #666666;
}

.terms-link {
  font-size: 26rpx;
  color: #667eea;
  cursor: pointer;
  text-decoration: underline;
}

.register-btn {
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

.register-btn:disabled {
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

.login-link {
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
  
  .agree-terms {
    flex-direction: column;
    align-items: flex-start;
    gap: 5rpx;
  }
}
</style>
