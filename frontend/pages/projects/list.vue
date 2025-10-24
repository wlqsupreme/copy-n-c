<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <button class="back-btn" @click="goBack">←</button>
        <text class="page-title">我的项目</text>
      </view>
      <view class="nav-right">
        <button class="add-btn" @click="showCreateProject">+ 新建项目</button>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <!-- 统计信息 -->
      <view class="stats-section">
        <view class="stat-card">
          <text class="stat-number">{{ projects.length }}</text>
          <text class="stat-label">总项目</text>
        </view>
        <view class="stat-card">
          <text class="stat-number">{{ activeProjects }}</text>
          <text class="stat-label">进行中</text>
        </view>
        <view class="stat-card">
          <text class="stat-number">{{ completedProjects }}</text>
          <text class="stat-label">已完成</text>
        </view>
      </view>

      <!-- 项目列表 -->
      <view class="projects-section">
        <view class="section-header">
          <text class="section-title">项目列表</text>
          <view class="filter-tabs">
            <text 
              class="filter-tab" 
              :class="{ active: currentFilter === 'all' }"
              @click="setFilter('all')"
            >全部</text>
            <text 
              class="filter-tab" 
              :class="{ active: currentFilter === 'active' }"
              @click="setFilter('active')"
            >进行中</text>
            <text 
              class="filter-tab" 
              :class="{ active: currentFilter === 'completed' }"
              @click="setFilter('completed')"
            >已完成</text>
          </view>
        </view>

        <view class="projects-grid">
          <view 
            class="project-card" 
            v-for="project in filteredProjects" 
            :key="project.project_id"
            @click="openProject(project)"
          >
            <view class="project-header">
              <text class="project-title">{{ project.title }}</text>
              <view class="project-status" :class="project.status">
                <text class="status-text">{{ getStatusText(project.status) }}</text>
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
              <button class="action-btn storyboard" @click.stop="editStoryboard(project)">编辑分镜</button>
              <button class="action-btn edit" @click.stop="editProject(project)">编辑</button>
              <button class="action-btn delete" @click.stop="deleteProject(project)">删除</button>
            </view>
          </view>
        </view>

        <!-- 空状态 -->
        <view class="empty-state" v-if="filteredProjects.length === 0">
          <text class="empty-icon">📚</text>
          <text class="empty-title">暂无项目</text>
          <text class="empty-desc">创建你的第一个项目开始创作吧</text>
          <button class="empty-btn" @click="showCreateProject">创建项目</button>
        </view>
      </view>
    </view>

    <!-- 创建项目弹窗 -->
    <view class="modal" v-if="showCreateModal" @click="closeCreateModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">创建新项目</text>
          <button class="close-btn" @click="closeCreateModal">×</button>
        </view>
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">项目标题</text>
            <input 
              class="form-input" 
              v-model="newProject.title" 
              placeholder="请输入项目标题"
              :class="{ 'error': errors.title }"
            />
            <text class="error-text" v-if="errors.title">{{ errors.title }}</text>
          </view>
          
          <view class="form-group">
            <text class="form-label">项目描述</text>
            <textarea 
              class="form-textarea" 
              v-model="newProject.description" 
              placeholder="请输入项目描述（可选）"
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">可见性</text>
            <view class="radio-group">
              <view class="radio-item">
                <radio value="private" :checked="newProject.visibility === 'private'" @click="newProject.visibility = 'private'" />
                <text class="radio-text">私有</text>
              </view>
              <view class="radio-item">
                <radio value="public" :checked="newProject.visibility === 'public'" @click="newProject.visibility = 'public'" />
                <text class="radio-text">公开</text>
              </view>
            </view>
          </view>
        </view>
        <view class="modal-footer">
          <button class="btn cancel" @click="closeCreateModal">取消</button>
          <button class="btn confirm" @click="createProject" :disabled="isCreating">
            <text v-if="isCreating">创建中...</text>
            <text v-else>创建项目</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      projects: [
        {
          project_id: '1',
          title: '修仙传说',
          description: '一个关于修仙世界的奇幻故事',
          visibility: 'private',
          status: 'active',
          chapter_count: 5,
          character_count: 8,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-20T15:30:00Z'
        },
        {
          project_id: '2',
          title: '都市情缘',
          description: '现代都市背景的爱情故事',
          visibility: 'public',
          status: 'completed',
          chapter_count: 12,
          character_count: 6,
          created_at: '2024-01-10T09:00:00Z',
          updated_at: '2024-01-18T20:00:00Z'
        },
        {
          project_id: '3',
          title: '星际战争',
          description: '未来科幻背景的战争史诗',
          visibility: 'private',
          status: 'active',
          chapter_count: 3,
          character_count: 12,
          created_at: '2024-01-22T14:00:00Z',
          updated_at: '2024-01-23T11:15:00Z'
        }
      ],
      currentFilter: 'all',
      showCreateModal: false,
      isCreating: false,
      newProject: {
        title: '',
        description: '',
        visibility: 'private'
      },
      errors: {}
    }
  },
  
  computed: {
    activeProjects() {
      return this.projects.filter(p => p.status === 'active').length
    },
    
    completedProjects() {
      return this.projects.filter(p => p.status === 'completed').length
    },
    
    filteredProjects() {
      if (this.currentFilter === 'all') {
        return this.projects
      }
      return this.projects.filter(p => p.status === this.currentFilter)
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack()
    },
    
    setFilter(filter) {
      this.currentFilter = filter
    },
    
    getStatusText(status) {
      const statusMap = {
        'active': '进行中',
        'completed': '已完成',
        'draft': '草稿'
      }
      return statusMap[status] || '未知'
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    },
    
    showCreateProject() {
      this.showCreateModal = true
      this.newProject = {
        title: '',
        description: '',
        visibility: 'private'
      }
      this.errors = {}
    },
    
    closeCreateModal() {
      this.showCreateModal = false
    },
    
    validateProject() {
      this.errors = {}
      
      if (!this.newProject.title.trim()) {
        this.errors.title = '请输入项目标题'
      } else if (this.newProject.title.length < 2) {
        this.errors.title = '项目标题至少2个字符'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    async createProject() {
      if (!this.validateProject()) {
        return
      }
      
      this.isCreating = true
      
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const newProjectData = {
          project_id: Date.now().toString(),
          title: this.newProject.title,
          description: this.newProject.description,
          visibility: this.newProject.visibility,
          status: 'active',
          chapter_count: 0,
          character_count: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        this.projects.unshift(newProjectData)
        
        uni.showToast({
          title: '项目创建成功',
          icon: 'success'
        })
        
        this.closeCreateModal()
        
      } catch (error) {
        uni.showToast({
          title: '创建失败，请重试',
          icon: 'none'
        })
      } finally {
        this.isCreating = false
      }
    },
    
    openProject(project) {
      uni.navigateTo({
        url: `/pages/projects/detail?projectId=${project.project_id}`
      })
    },
    
    editStoryboard(project) {
      uni.navigateTo({
        url: `/pages/storyboard/script-analyzer?project_id=${project.project_id}`
      })
    },
    
    editProject(project) {
      uni.showToast({
        title: '编辑功能开发中',
        icon: 'none'
      })
    },
    
    deleteProject(project) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除项目"${project.title}"吗？此操作不可恢复。`,
        success: (res) => {
          if (res.confirm) {
            const index = this.projects.findIndex(p => p.project_id === project.project_id)
            if (index > -1) {
              this.projects.splice(index, 1)
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
            }
          }
        }
      })
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 60rpx;
  background-color: #ffffff;
  border-bottom: 1rpx solid #e9ecef;
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

.add-btn {
  padding: 20rpx 30rpx;
  background-color: #000000;
  color: #ffffff;
  border: none;
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.main-content {
  padding: 40rpx 60rpx;
}

.stats-section {
  display: flex;
  gap: 30rpx;
  margin-bottom: 60rpx;
}

.stat-card {
  flex: 1;
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 40rpx 30rpx;
  text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 48rpx;
  font-weight: bold;
  color: #000000;
  display: block;
  margin-bottom: 10rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #666666;
}

.projects-section {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 40rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #000000;
}

.filter-tabs {
  display: flex;
  gap: 20rpx;
}

.filter-tab {
  padding: 15rpx 30rpx;
  font-size: 26rpx;
  color: #666666;
  border-radius: 20rpx;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tab.active {
  background-color: #000000;
  color: #ffffff;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400rpx, 1fr));
  gap: 30rpx;
}

.project-card {
  border: 2rpx solid #e9ecef;
  border-radius: 16rpx;
  padding: 30rpx;
  transition: all 0.3s ease;
  cursor: pointer;
}

.project-card:hover {
  border-color: #000000;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
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

.project-status.active {
  background-color: #e3f2fd;
  color: #1976d2;
}

.project-status.completed {
  background-color: #e8f5e8;
  color: #2e7d32;
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

.empty-state {
  text-align: center;
  padding: 80rpx 40rpx;
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

.form-input.error {
  border-color: #ff4757;
}

.form-textarea {
  width: 100%;
  height: 120rpx;
  border: 2rpx solid #ddd;
  border-radius: 10rpx;
  padding: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
  resize: none;
}

.radio-group {
  display: flex;
  gap: 30rpx;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.radio-text {
  font-size: 28rpx;
  color: #333;
}

.error-text {
  font-size: 24rpx;
  color: #ff4757;
  display: block;
  margin-top: 10rpx;
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
  background-color: #000000;
  color: white;
}

.btn.confirm:disabled {
  opacity: 0.6;
}

/* 响应式设计 */
@media (max-width: 750rpx) {
  .main-content {
    padding: 30rpx;
  }
  
  .stats-section {
    flex-direction: column;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20rpx;
  }
}
</style>
