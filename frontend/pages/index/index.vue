<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <button class="nav-btn" @click="showLogin = true">登录</button>
        <button class="nav-btn" @click="showRegister = true">注册</button>
      </view>
      <view class="nav-right">
        <text class="app-title">小说转漫画</text>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 项目介绍 -->
      <view class="intro-section">
        <view class="intro-card">
          <text class="intro-title">AI 驱动的小说转漫画平台</text>
          <text class="intro-subtitle">将文字故事转化为视觉分镜，让创作更简单</text>
          
          <view class="features">
            <view class="feature-item">
              <text class="feature-icon">📝</text>
              <text class="feature-text">智能文本解析</text>
            </view>
            <view class="feature-item">
              <text class="feature-icon">🎬</text>
              <text class="feature-text">专业分镜规划</text>
            </view>
            <view class="feature-item">
              <text class="feature-icon">🎨</text>
              <text class="feature-text">AI 图像生成</text>
            </view>
            <view class="feature-item">
              <text class="feature-icon">✏️</text>
              <text class="feature-text">可视化编辑</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 功能导航 -->
      <view class="nav-section">
        <text class="nav-title">开始创作</text>
        
        <view class="nav-cards">
          <view class="nav-card" @click="goToScriptAnalyzer">
            <view class="card-icon">📖</view>
            <text class="card-title">文本分析</text>
            <text class="card-desc">上传小说文本，AI智能解析情节和角色</text>
            <button class="card-btn">开始分析</button>
          </view>
          
          <view class="nav-card" @click="goToLayoutPlanner">
            <view class="card-icon">🎭</view>
            <text class="card-title">分镜规划</text>
            <text class="card-desc">可视化编辑分镜脚本，调整画面布局</text>
            <button class="card-btn">开始规划</button>
          </view>
          
          <view class="nav-card" @click="showComingSoon">
            <view class="card-icon">🖼️</view>
            <text class="card-title">图像生成</text>
            <text class="card-desc">AI生成漫画图像，一键完成创作</text>
            <button class="card-btn">即将推出</button>
          </view>
          
          <view class="nav-card" @click="showComingSoon">
            <view class="card-icon">📚</view>
            <text class="card-title">作品管理</text>
            <text class="card-desc">管理你的创作项目，导出最终作品</text>
            <button class="card-btn">即将推出</button>
          </view>
        </view>
      </view>

      <!-- 使用说明 -->
      <view class="guide-section">
        <text class="guide-title">如何使用</text>
        <view class="guide-steps">
          <view class="step-item">
            <view class="step-number">1</view>
            <text class="step-text">上传或输入小说文本</text>
          </view>
          <view class="step-item">
            <view class="step-number">2</view>
            <text class="step-text">AI 自动解析情节和角色</text>
          </view>
          <view class="step-item">
            <view class="step-number">3</view>
            <text class="step-text">编辑和调整分镜脚本</text>
          </view>
          <view class="step-item">
            <view class="step-number">4</view>
            <text class="step-text">生成最终的漫画作品</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 登录弹窗 -->
    <view class="modal" v-if="showLogin" @click="showLogin = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">用户登录</text>
          <button class="close-btn" @click="showLogin = false">×</button>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">用户名/邮箱</text>
            <input class="form-input" v-model="loginForm.username" placeholder="请输入用户名或邮箱" />
          </view>
          <view class="form-group">
            <text class="form-label">密码</text>
            <input class="form-input" v-model="loginForm.password" type="password" placeholder="请输入密码" />
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn cancel" @click="showLogin = false">取消</button>
          <button class="btn confirm" @click="handleLogin">登录</button>
        </view>
      </view>
    </view>

    <!-- 注册弹窗 -->
    <view class="modal" v-if="showRegister" @click="showRegister = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">用户注册</text>
          <button class="close-btn" @click="showRegister = false">×</button>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">用户名</text>
            <input class="form-input" v-model="registerForm.username" placeholder="请输入用户名" />
          </view>
          <view class="form-group">
            <text class="form-label">邮箱</text>
            <input class="form-input" v-model="registerForm.email" placeholder="请输入邮箱" />
          </view>
          <view class="form-group">
            <text class="form-label">密码</text>
            <input class="form-input" v-model="registerForm.password" type="password" placeholder="请输入密码" />
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn cancel" @click="showRegister = false">取消</button>
          <button class="btn confirm" @click="handleRegister">注册</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      showLogin: false,
      showRegister: false,
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: ''
      }
    }
  },
  
  methods: {
    goToScriptAnalyzer() {
      uni.navigateTo({
        url: '/pages/storyboard/script-analyzer'
      })
    },
    
    goToLayoutPlanner() {
      uni.navigateTo({
        url: '/pages/storyboard/layout-planner'
      })
    },
    
    showComingSoon() {
      uni.showToast({
        title: '功能即将推出',
        icon: 'none'
      })
    },
    
    handleLogin() {
      if (!this.loginForm.username || !this.loginForm.password) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        })
        return
      }
      
      // 这里可以添加实际的登录逻辑
      uni.showToast({
        title: '登录功能开发中',
        icon: 'none'
      })
      this.showLogin = false
    },
    
    handleRegister() {
      if (!this.registerForm.username || !this.registerForm.email || !this.registerForm.password) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        })
        return
      }
      
      // 这里可以添加实际的注册逻辑
      uni.showToast({
        title: '注册功能开发中',
        icon: 'none'
      })
      this.showRegister = false
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10rpx);
}

.nav-left {
  display: flex;
  gap: 20rpx;
}

.nav-btn {
  padding: 12rpx 24rpx;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1rpx solid rgba(255, 255, 255, 0.3);
  border-radius: 20rpx;
  font-size: 26rpx;
}

.app-title {
  font-size: 36rpx;
  font-weight: bold;
  color: white;
}

.main-content {
  padding: 40rpx 30rpx;
}

.intro-section {
  margin-bottom: 60rpx;
}

.intro-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.intro-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.intro-subtitle {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 40rpx;
}

.features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30rpx;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120rpx;
}

.feature-icon {
  font-size: 48rpx;
  margin-bottom: 10rpx;
}

.feature-text {
  font-size: 24rpx;
  color: #666;
  text-align: center;
}

.nav-section {
  margin-bottom: 60rpx;
}

.nav-title {
  font-size: 40rpx;
  font-weight: bold;
  color: white;
  text-align: center;
  margin-bottom: 40rpx;
  display: block;
}

.nav-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30rpx;
}

.nav-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 20rpx;
  padding: 30rpx;
  text-align: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.nav-card:active {
  transform: scale(0.95);
}

.card-icon {
  font-size: 60rpx;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 15rpx;
}

.card-desc {
  font-size: 24rpx;
  color: #666;
  line-height: 1.4;
  display: block;
  margin-bottom: 25rpx;
}

.card-btn {
  width: 100%;
  padding: 20rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 15rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.guide-section {
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 20rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.guide-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 40rpx;
  display: block;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.step-number {
  width: 60rpx;
  height: 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: bold;
  flex-shrink: 0;
}

.step-text {
  font-size: 28rpx;
  color: #333;
  flex: 1;
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 20rpx;
  width: 90%;
  max-width: 600rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.close-btn {
  width: 60rpx;
  height: 60rpx;
  background-color: #f0f0f0;
  color: #666;
  border: none;
  border-radius: 50%;
  font-size: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 30rpx;
}

.form-group {
  margin-bottom: 30rpx;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  display: block;
  margin-bottom: 10rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  border: 2rpx solid #ddd;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
  padding: 30rpx;
  border-top: 1rpx solid #eee;
}

.btn {
  padding: 20rpx 40rpx;
  border: none;
  border-radius: 10rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.btn.cancel {
  background-color: #f0f0f0;
  color: #666;
}

.btn.confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
</style>
