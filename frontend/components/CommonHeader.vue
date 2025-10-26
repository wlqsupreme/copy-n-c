<template>
  <view class="header">
    <view class="nav-left">
      <text class="logo">小说转漫画</text>
    </view>
    <view class="nav-right">
      <!-- 未登录状态 -->
      <template v-if="!isLoggedIn">
        <text class="nav-link" @click="goToLogin">登录</text>
        <text class="nav-link" @click="goToRegister">注册</text>
      </template>
      
      <!-- 已登录状态 -->
      <template v-else>
        <view class="user-dropdown" @mouseenter="showDropdown = true" @mouseleave="showDropdown = false">
          <view class="user-info">
            <view class="user-avatar">
              <text class="avatar-text">{{ userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}</text>
            </view>
            <text class="username">{{ userInfo.username || '用户' }}</text>
            <text class="dropdown-arrow">▼</text>
          </view>
          
          <!-- 下拉菜单 -->
          <view class="dropdown-menu" v-show="showDropdown">
            <view class="dropdown-item" @click="goToMyProjects">
              <text class="item-icon">📚</text>
              <text class="item-text">我的项目</text>
            </view>
            <view class="dropdown-item" @click="goToProfile">
              <text class="item-icon">👤</text>
              <text class="item-text">个人资料</text>
            </view>
            <view class="dropdown-divider"></view>
            <view class="dropdown-item" @click="handleLogout">
              <text class="item-icon">🚪</text>
              <text class="item-text">退出登录</text>
            </view>
          </view>
        </view>
      </template>
    </view>
  </view>
</template>

<script>
import authManager from '../utils/auth.js'

export default {
  name: 'CommonHeader',
  data() {
    return {
      isLoggedIn: false,
      userInfo: {},
      showDropdown: false
    }
  },
  
  mounted() {
    this.checkLoginStatus()
  },
  
  activated() {
    // 每次页面激活时检查登录状态
    this.checkLoginStatus()
  },
  
  methods: {
    // 检查登录状态
    checkLoginStatus() {
      this.isLoggedIn = authManager.isLoggedIn()
      if (this.isLoggedIn) {
        this.userInfo = authManager.getUserInfo() || {}
      } else {
        this.userInfo = {}
        this.showDropdown = false
      }
    },
    
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
    
    goToMyProjects() {
      this.showDropdown = false
      uni.navigateTo({
        url: '/pages/projects/list'
      })
    },
    
    goToProfile() {
      this.showDropdown = false
      uni.showToast({
        title: '个人资料功能开发中',
        icon: 'none'
      })
    },
    
    async handleLogout() {
      try {
        await authManager.logout()
        this.isLoggedIn = false
        this.userInfo = {}
        this.showDropdown = false
        
        uni.showToast({
          title: '已退出登录',
          icon: 'success'
        })
        
        // 刷新页面状态
        this.checkLoginStatus()
      } catch (error) {
        console.error('退出登录失败:', error)
        uni.showToast({
          title: '退出登录失败',
          icon: 'error'
        })
      }
    }
  }
}
</script>

<style scoped>
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

/* 用户下拉菜单样式 */
.user-dropdown {
  position: relative;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  border-radius: 12rpx;
  transition: background-color 0.3s ease;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.user-avatar {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

.username {
  font-size: 32rpx;
  color: #000000;
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 20rpx;
  color: #666666;
  transition: transform 0.3s ease;
}

.user-dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #ffffff;
  border: 2rpx solid #e0e0e0;
  border-radius: 12rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
  min-width: 240rpx;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx 32rpx;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item:active {
  background-color: #e9ecef;
}

.item-icon {
  font-size: 32rpx;
  width: 40rpx;
  text-align: center;
}

.item-text {
  font-size: 28rpx;
  color: #333333;
  flex: 1;
}

.dropdown-divider {
  height: 2rpx;
  background-color: #e0e0e0;
  margin: 8rpx 0;
}
</style>
