<template>
  <view class="container">
    <!-- 通用头部 -->
    <CommonHeader />
    
    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 操作栏 -->
      <view class="action-bar">
        <text class="page-title">我的项目</text>
        <button class="add-btn" @click="showCreateProject">+ 新建项目</button>
      </view>

      <!-- 项目列表 -->
      <view class="project-list-container">
        <view 
          v-for="project in projects" 
          :key="project.project_id" 
          class="project-card"
          @click="goToProjectDetail(project)"
        >
          <view class="project-header">
            <text class="project-title">{{ project.title }}</text>
            <view class="project-status" :class="project.visibility">
              <text class="status-text">{{ project.visibility === 'public' ? '公开' : '私有' }}</text>
            </view>
          </view>
          
          <text class="project-description">{{ project.description || '暂无描述' }}</text>
          
          <view class="project-meta">
            <view class="meta-item">
              <text class="meta-icon">📖</text>
              <text class="meta-text">{{ project.chapter_count || 0 }} 章节</text>
            </view>
            <view class="meta-item">
              <text class="meta-icon">👥</text>
              <text class="meta-text">{{ project.character_count || 0 }} 角色</text>
            </view>
            <view class="meta-item">
              <text class="meta-icon">📅</text>
              <text class="meta-text">{{ formatDate(project.updated_at) }}</text>
            </view>
          </view>
          
          <view class="project-actions">
            <!-- 根据上传方式显示不同的按钮 -->
            <template v-if="project.upload_method === 'single_chapter'">
              <button class="action-btn import" @click.stop="importChapter(project)">导入单章小说原文</button>
              <button class="action-btn storyboard" @click.stop="goToProjectDetail(project)">编辑分镜描述</button>
              <button class="action-btn delete" @click.stop="deleteProject(project)">删除</button>
            </template>
            <template v-else>
              <button class="action-btn storyboard" @click.stop="editStoryboard(project)">编辑分镜</button>
              <button class="action-btn edit" @click.stop="editProject(project)">编辑</button>
              <button class="action-btn delete" @click.stop="deleteProject(project)">删除</button>
            </template>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="projects.length === 0">
        <text class="empty-icon">📚</text>
        <text class="empty-title">暂无项目</text>
        <text class="empty-desc">创建你的第一个项目开始创作吧</text>
        <button class="empty-btn" @click="showCreateProject">创建项目</button>
      </view>
    </view>

    <!-- 创建项目弹窗 -->
    <view class="modal" v-if="showCreateModal" @click="closeCreateModal">
      <view class="modal-content" @click.stop>
        <NewProjectForm @close="closeCreateModal" @submit="handleCreateProject" />
      </view>
    </view>
  </view>
</template>

<script>
import CommonHeader from '../../components/CommonHeader.vue'
import NewProjectForm from '../../components/NewProjectForm.vue'
import authManager from '../../utils/auth.js'

export default {
  components: {
    CommonHeader,
    NewProjectForm
  },
  
  data() {
    return {
      projects: [],
      showCreateModal: false,
      isLoading: false
    }
  },
  
  onLoad() {
    // 检查登录状态
    this.checkAuth();
    // 加载项目列表
    this.loadProjects();
  },
  
  onShow() {
    // 每次页面显示时重新加载项目列表
    this.loadProjects();
  },
  
  methods: {
    checkAuth() {
      if (!authManager.isLoggedIn()) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        });
        setTimeout(() => {
          uni.navigateTo({
            url: '/pages/auth/login'
          });
        }, 1500);
        return false;
      }
      return true;
    },
    
    async loadProjects() {
      if (!this.checkAuth()) return;
      
      // 获取用户信息
      const userInfo = authManager.getUserInfo();
      if (!userInfo || !userInfo.user_id) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        });
        return;
      }
      
      this.isLoading = true;
      try {
        const response = await uni.request({
          url: `/api/v1/projects?user_id=${userInfo.user_id}`,
          method: 'GET',
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authManager.getToken()}`
          }
        });
        
        if (response.statusCode === 200) {
          this.projects = response.data || [];
        } else {
          throw new Error(response.data.detail || '加载失败');
        }
      } catch (error) {
        console.error('加载项目列表失败:', error);
        uni.showToast({
          title: '加载失败: ' + error.message,
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    },
    
    showCreateProject() {
      this.showCreateModal = true;
    },
    
    closeCreateModal() {
      this.showCreateModal = false;
    },
    
    handleCreateProject(newProject) {
      // 将新项目添加到列表顶部
      this.projects.unshift(newProject);
      uni.showToast({
        title: '项目创建成功',
        icon: 'success'
      });
    },
    
    formatDate(dateString) {
      if (!dateString) return '未知';
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN');
    },
    
    goToProjectDetail(project) {
      uni.navigateTo({
        url: `/pages/projects/detail?projectId=${project.project_id}`
      });
    },
    
    importChapter(project) {
      uni.navigateTo({
        url: `/pages/storyboard/script-analyzer?project_id=${project.project_id}`
      });
    },
    
    editStoryboard(project) {
      uni.navigateTo({
        url: `/pages/storyboard/script-analyzer?project_id=${project.project_id}`
      });
    },
    
    editProject(project) {
      uni.showToast({
        title: '编辑功能开发中',
        icon: 'none'
      });
    },
    
    deleteProject(project) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除项目"${project.title}"吗？此操作不可恢复。`,
        success: async (res) => {
          if (res.confirm) {
            try {
              const response = await uni.request({
                url: `/api/v1/projects/${project.project_id}`,
                method: 'DELETE'
              });
              
              if (response.statusCode === 200) {
                // 从列表中移除项目
                const index = this.projects.findIndex(p => p.project_id === project.project_id);
                if (index > -1) {
                  this.projects.splice(index, 1);
                }
                uni.showToast({
                  title: '删除成功',
                  icon: 'success'
                });
              } else {
                throw new Error(response.data.detail || '删除失败');
              }
            } catch (error) {
              uni.showToast({
                title: '删除失败: ' + error.message,
                icon: 'none'
              });
            }
          }
        }
      });
    }
  }
}
</script>

<style scoped>
.container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.main-content {
  padding: 40rpx 60rpx;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.page-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #000000;
}

.add-btn {
  padding: 20rpx 30rpx;
  background-color: #000000;
  color: #ffffff;
  border: none;
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: bold;
}

/* 项目列表容器 - 响应式网格 */
.project-list-container {
  display: flex;
  flex-wrap: wrap;
  gap: 30rpx;
  justify-content: flex-start;
}

/* 项目卡片 */
.project-card {
  flex-basis: 400rpx;
  flex-grow: 1;
  min-width: 350rpx;
  
  border: 2rpx solid #e9ecef;
  border-radius: 16rpx;
  padding: 30rpx;
  background-color: #ffffff;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.project-card:hover {
  border-color: #000000;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
  transform: translateY(-2rpx);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.project-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #000000;
  flex: 1;
  margin-right: 20rpx;
}

.project-status {
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
}

.project-status.private {
  background-color: #f8f9fa;
  color: #6c757d;
}

.project-status.public {
  background-color: #d4edda;
  color: #155724;
}

.project-description {
  font-size: 26rpx;
  color: #666666;
  line-height: 1.5;
  margin-bottom: 30rpx;
  display: block;
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
  margin-bottom: 30rpx;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.meta-icon {
  font-size: 24rpx;
}

.meta-text {
  font-size: 24rpx;
  color: #666666;
}

.project-actions {
  display: flex;
  gap: 15rpx;
}

.action-btn {
  flex: 1;
  padding: 20rpx;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: bold;
}

.action-btn.import {
  background-color: #28a745;
  color: #ffffff;
}

.action-btn.storyboard {
  background-color: #007aff;
  color: #ffffff;
}

.action-btn.edit {
  background-color: #f8f9fa;
  color: #495057;
}

.action-btn.delete {
  background-color: #f8d7da;
  color: #721c24;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 120rpx 40rpx;
}

.empty-icon {
  font-size: 120rpx;
  display: block;
  margin-bottom: 30rpx;
}

.empty-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #000000;
  display: block;
  margin-bottom: 20rpx;
}

.empty-desc {
  font-size: 28rpx;
  color: #666666;
  display: block;
  margin-bottom: 40rpx;
}

.empty-btn {
  padding: 30rpx 60rpx;
  background-color: #000000;
  color: #ffffff;
  border: none;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: bold;
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

/* 响应式设计 */
@media (max-width: 750rpx) {
  .main-content {
    padding: 30rpx;
  }
  
  .project-list-container {
    flex-direction: column;
  }
  
  .project-card {
    flex-basis: auto;
    min-width: auto;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 20rpx;
  }
}
</style>