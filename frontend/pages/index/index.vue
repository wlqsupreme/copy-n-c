<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <text class="logo">小说转漫画</text>
      </view>
      <view class="nav-right">
        <text class="nav-link" @click="goToLogin">登录</text>
        <text class="nav-link" @click="goToRegister">注册</text>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- Hero Section -->
      <view class="hero-section">
        <view class="hero-icon">
          <view class="icon-gradient">
            <text class="icon-text">N</text>
          </view>
        </view>
        
        <text class="hero-title">发现你的故事灵感</text>
        <text class="hero-subtitle">拥有超过500,000个故事和1,000个创作项目—每周都有新内容</text>
        
        <view class="cta-buttons">
          <button class="btn-primary" @click="goToScriptAnalyzer">免费开始</button>
          <button class="btn-secondary" @click="goToLayoutPlanner">查看我们的计划 →</button>
        </view>
      </view>

      <!-- Trust Section -->
      <view class="trust-section">
        <text class="trust-text">受到创作者的信赖</text>
        <view class="trust-logos">
          <view class="logo-item">AI</view>
          <view class="logo-item">创作</view>
          <view class="logo-item">故事</view>
          <view class="logo-item">漫画</view>
          <view class="logo-item">分镜</view>
          <view class="logo-item">设计</view>
          <view class="logo-item">灵感</view>
        </view>
      </view>

      <!-- Features Section -->
      <view class="features-section">
        <text class="section-title">核心功能</text>
        <view class="features-grid">
          <view class="feature-card" @click="goToScriptAnalyzer">
            <view class="feature-icon">📖</view>
            <text class="feature-title">智能文本分析</text>
            <text class="feature-desc">AI自动解析小说情节、角色和场景</text>
          </view>
          
          <view class="feature-card" @click="goToLayoutPlanner">
            <view class="feature-icon">🎬</view>
            <text class="feature-title">专业分镜规划</text>
            <text class="feature-desc">可视化编辑分镜脚本，调整画面布局</text>
          </view>
          
          <view class="feature-card" @click="showComingSoon">
            <view class="feature-icon">🎨</view>
            <text class="feature-title">AI图像生成</text>
            <text class="feature-desc">智能生成漫画图像，一键完成创作</text>
          </view>
          
          <view class="feature-card" @click="goToProjects">
            <view class="feature-icon">📚</view>
            <text class="feature-title">项目管理</text>
            <text class="feature-desc">管理你的创作项目，导出最终作品</text>
          </view>
        </view>
      </view>

      <!-- How it works -->
      <view class="how-it-works">
        <text class="section-title">如何使用</text>
        <view class="steps">
          <view class="step">
            <view class="step-number">1</view>
            <text class="step-text">上传或输入小说文本</text>
          </view>
          <view class="step">
            <view class="step-number">2</view>
            <text class="step-text">AI自动解析情节和角色</text>
          </view>
          <view class="step">
            <view class="step-number">3</view>
            <text class="step-text">编辑和调整分镜脚本</text>
          </view>
          <view class="step">
            <view class="step-number">4</view>
            <text class="step-text">生成最终的漫画作品</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // 移除弹窗相关的数据
    }
  },
  
  methods: {
    goToLogin() {
      uni.navigateTo({
        url: '/pages/auth/login'
      })
    },
    
    goToRegister() {
      uni.navigateTo({
        url: '/pages/auth/register'
      })
    },
    
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
    
    goToProjects() {
      uni.navigateTo({
        url: '/pages/projects/list'
      })
    },
    
    showComingSoon() {
      uni.showToast({
        title: '功能即将推出',
        icon: 'none'
      })
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
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 60rpx;
  background-color: transparent;
}

.logo {
  font-size: 48rpx;
  font-weight: bold;
  color: #000000;
}

.nav-right {
  display: flex;
  gap: 40rpx;
}

.nav-link {
  font-size: 32rpx;
  color: #000000;
  cursor: pointer;
}

.main-content {
  padding: 80rpx 60rpx;
  text-align: center;
}

.hero-section {
  margin-bottom: 120rpx;
}

.hero-icon {
  margin-bottom: 60rpx;
}

.icon-gradient {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.icon-text {
  font-size: 60rpx;
  font-weight: bold;
  color: #ffffff;
}

.hero-title {
  font-size: 80rpx;
  font-weight: bold;
  color: #000000;
  display: block;
  margin-bottom: 40rpx;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 32rpx;
  color: #666666;
  display: block;
  margin-bottom: 80rpx;
  line-height: 1.5;
  max-width: 800rpx;
  margin-left: auto;
  margin-right: auto;
}

.cta-buttons {
  display: flex;
  gap: 30rpx;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  padding: 30rpx 60rpx;
  background-color: #000000;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  min-width: 200rpx;
}

.btn-secondary {
  padding: 30rpx 60rpx;
  background-color: #ffffff;
  color: #000000;
  border: 2rpx solid #000000;
  border-radius: 12rpx;
  font-size: 32rpx;
  font-weight: bold;
  min-width: 200rpx;
}

.trust-section {
  margin-bottom: 120rpx;
}

.trust-text {
  font-size: 28rpx;
  color: #999999;
  display: block;
  margin-bottom: 60rpx;
}

.trust-logos {
  display: flex;
  justify-content: center;
  gap: 60rpx;
  flex-wrap: wrap;
}

.logo-item {
  font-size: 24rpx;
  color: #999999;
  font-weight: 500;
}

.features-section {
  margin-bottom: 120rpx;
}

.section-title {
  font-size: 60rpx;
  font-weight: bold;
  color: #000000;
  display: block;
  margin-bottom: 80rpx;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 40rpx;
  max-width: 1000rpx;
  margin: 0 auto;
}

.feature-card {
  background-color: #ffffff;
  border: 2rpx solid #f0f0f0;
  border-radius: 20rpx;
  padding: 60rpx 40rpx;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:active {
  transform: scale(0.98);
  border-color: #000000;
}

.feature-icon {
  font-size: 80rpx;
  margin-bottom: 30rpx;
}

.feature-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #000000;
  display: block;
  margin-bottom: 20rpx;
}

.feature-desc {
  font-size: 28rpx;
  color: #666666;
  line-height: 1.5;
  display: block;
}

.how-it-works {
  max-width: 800rpx;
  margin: 0 auto;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 60rpx;
}

.step {
  display: flex;
  align-items: center;
  gap: 40rpx;
  text-align: left;
}

.step-number {
  width: 80rpx;
  height: 80rpx;
  background-color: #000000;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: bold;
  flex-shrink: 0;
}

.step-text {
  font-size: 32rpx;
  color: #000000;
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 750rpx) {
  .hero-title {
    font-size: 60rpx;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .trust-logos {
    gap: 40rpx;
  }
}
</style>
