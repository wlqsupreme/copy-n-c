<template>
  <view class="container">
    <view class="header">
      <text class="title">分镜规划</text>
      <view class="header-actions">
        <button 
          class="save-btn" 
          @click="saveStoryboardToDatabase" 
          :disabled="isLoading || !hasUnsavedChanges"
          v-if="projectId"
        >
          <text v-if="isLoading">保存中...</text>
          <text v-else>保存分镜</text>
        </button>
        <button class="back-btn" @click="goBack">返回</button>
      </view>
    </view>
    
    <view class="storyboard-content">
      <!-- 分镜页面列表 -->
      <view class="pages-section">
        <text class="section-title">分镜页面 ({{ pages.length }}页)</text>
        
        <view class="page-item" v-for="(page, pageIndex) in pages" :key="pageIndex">
          <view class="page-header">
            <text class="page-title">第 {{ page.page_index }} 页</text>
            <view class="page-actions">
              <button class="action-btn" @click="editPage(pageIndex)">编辑</button>
              <button class="action-btn delete" @click="deletePage(pageIndex)">删除</button>
            </view>
          </view>
          
          <!-- 面板列表 -->
          <view class="panels-container">
            <view class="panel-item" v-for="(panel, panelIndex) in page.panels" :key="panelIndex">
              <view class="panel-header">
                <text class="panel-title">面板 {{ panel.panel_index }}</text>
                <view class="panel-actions">
                  <button class="small-btn" @click="editPanel(pageIndex, panelIndex)">编辑</button>
                  <button class="small-btn delete" @click="deletePanel(pageIndex, panelIndex)">删除</button>
                </view>
              </view>
              
              <view class="panel-content">
                <view class="panel-field">
                  <text class="field-label">场景描述：</text>
                  <text class="field-value">{{ panel.description }}</text>
                </view>
                
                <view class="panel-field" v-if="panel.characters && panel.characters.length > 0">
                  <text class="field-label">角色：</text>
                  <text class="field-value">{{ panel.characters.join(', ') }}</text>
                </view>
                
                <view class="panel-field" v-if="panel.dialogue && panel.dialogue.length > 0">
                  <text class="field-label">对话：</text>
                  <text class="field-value">{{ panel.dialogue.join(' | ') }}</text>
                </view>
                
                <view class="panel-field" v-if="panel.camera_angle">
                  <text class="field-label">镜头角度：</text>
                  <text class="field-value">{{ panel.camera_angle }}</text>
                </view>
                
                <view class="panel-field" v-if="panel.emotion">
                  <text class="field-label">情绪：</text>
                  <text class="field-value">{{ panel.emotion }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 编辑面板弹窗 -->
    <view class="modal" v-if="showEditModal" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑面板</text>
          <button class="close-btn" @click="closeModal">×</button>
        </view>
        
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">场景描述：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.description"
              placeholder="描述场景、人物动作、环境等..."
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">角色：</text>
            <input 
              class="form-input" 
              v-model="editingPanel.characters_text"
              placeholder="用逗号分隔多个角色"
            />
          </view>
          
          <view class="form-group">
            <text class="form-label">对话：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.dialogue_text"
              placeholder="输入对话内容，用 | 分隔多句对话"
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">镜头角度：</text>
            <select class="form-select" v-model="editingPanel.camera_angle">
              <option value="">选择镜头角度</option>
              <option value="特写">特写</option>
              <option value="近景">近景</option>
              <option value="中景">中景</option>
              <option value="远景">远景</option>
              <option value="鸟瞰">鸟瞰</option>
              <option value="仰视">仰视</option>
              <option value="俯视">俯视</option>
            </select>
          </view>
          
          <view class="form-group">
            <text class="form-label">情绪：</text>
            <select class="form-select" v-model="editingPanel.emotion">
              <option value="">选择情绪</option>
              <option value="开心">开心</option>
              <option value="愤怒">愤怒</option>
              <option value="悲伤">悲伤</option>
              <option value="惊讶">惊讶</option>
              <option value="恐惧">恐惧</option>
              <option value="平静">平静</option>
              <option value="紧张">紧张</option>
            </select>
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="btn cancel" @click="closeModal">取消</button>
          <button class="btn confirm" @click="savePanel">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      pages: [],
      showEditModal: false,
      editingPanel: {
        description: '',
        characters_text: '',
        dialogue_text: '',
        camera_angle: '',
        emotion: ''
      },
      editingPageIndex: -1,
      editingPanelIndex: -1,
      projectId: null,
      isLoading: false,
      hasUnsavedChanges: false
    }
  },
  
  onLoad(options) {
    // 场景一：从上一页接收分镜数据（新建分镜）
    if (options.storyboard) {
      try {
        const storyboard = JSON.parse(decodeURIComponent(options.storyboard))
        this.pages = storyboard.pages || []
        console.log('加载新建分镜数据:', this.pages)
      } catch (e) {
        console.error('解析分镜数据失败:', e)
        uni.showToast({
          title: '数据解析失败',
          icon: 'none'
        })
      }
    }
    // 场景二：从数据库加载已有分镜
    else if (options.project_id) {
      this.projectId = options.project_id
      this.loadExistingStoryboard(options.project_id)
    }
    else {
      uni.showToast({
        title: '缺少必要参数',
        icon: 'none'
      })
      setTimeout(() => {
        uni.navigateBack()
      }, 1500)
    }
  },
  
  methods: {
    // 场景二：从数据库加载已有分镜
    async loadExistingStoryboard(projectId) {
      this.isLoading = true
      uni.showLoading({
        title: '加载分镜中...'
      })
      
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/project/${projectId}`,
          method: 'GET',
          header: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.statusCode === 200 && response.data) {
          const projectData = response.data
          console.log('从数据库加载的项目数据:', projectData)
          
          // 解析分镜数据
          if (projectData.storyboard_data) {
            try {
              const storyboardData = typeof projectData.storyboard_data === 'string' 
                ? JSON.parse(projectData.storyboard_data) 
                : projectData.storyboard_data
              
              this.pages = storyboardData.pages || []
              console.log('解析后的分镜页面:', this.pages)
              
              uni.showToast({
                title: '分镜加载成功',
                icon: 'success'
              })
            } catch (parseError) {
              console.error('解析分镜数据失败:', parseError)
              uni.showToast({
                title: '分镜数据格式错误',
                icon: 'none'
              })
            }
          } else {
            // 如果没有分镜数据，初始化为空数组
            this.pages = []
            uni.showToast({
              title: '暂无分镜数据',
              icon: 'none'
            })
          }
        } else {
          throw new Error(`请求失败: ${response.statusCode}`)
        }
      } catch (error) {
        console.error('加载分镜失败:', error)
        uni.showToast({
          title: '加载分镜失败',
          icon: 'none'
        })
        // 加载失败时初始化为空数组
        this.pages = []
      } finally {
        this.isLoading = false
        uni.hideLoading()
      }
    },
    
    // 场景三：保存分镜到数据库
    async saveStoryboardToDatabase() {
      if (!this.projectId) {
        uni.showToast({
          title: '缺少项目ID',
          icon: 'none'
        })
        return false
      }
      
      this.isLoading = true
      uni.showLoading({
        title: '保存中...'
      })
      
      try {
        const storyboardData = {
          pages: this.pages
        }
        
        const response = await uni.request({
          url: 'http://localhost:8000/api/v1/save-storyboard',
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            project_id: this.projectId,
            storyboard_data: storyboardData
          }
        })
        
        if (response.statusCode === 200) {
          this.hasUnsavedChanges = false
          uni.showToast({
            title: '保存成功',
            icon: 'success'
          })
          return true
        } else {
          throw new Error(`保存失败: ${response.statusCode}`)
        }
      } catch (error) {
        console.error('保存分镜失败:', error)
        uni.showToast({
          title: '保存失败，请重试',
          icon: 'none'
        })
        return false
      } finally {
        this.isLoading = false
        uni.hideLoading()
      }
    },
    
    goBack() {
      // 如果有未保存的更改，提示用户
      if (this.hasUnsavedChanges) {
        uni.showModal({
          title: '未保存的更改',
          content: '您有未保存的更改，确定要离开吗？',
          success: (res) => {
            if (res.confirm) {
              uni.navigateBack()
            }
          }
        })
      } else {
        uni.navigateBack()
      }
    },
    
    editPanel(pageIndex, panelIndex) {
      const panel = this.pages[pageIndex].panels[panelIndex]
      this.editingPanel = {
        description: panel.description || '',
        characters_text: (panel.characters || []).join(', '),
        dialogue_text: (panel.dialogue || []).join(' | '),
        camera_angle: panel.camera_angle || '',
        emotion: panel.emotion || ''
      }
      this.editingPageIndex = pageIndex
      this.editingPanelIndex = panelIndex
      this.showEditModal = true
    },
    
    async savePanel() {
      if (!this.editingPanel.description.trim()) {
        uni.showToast({
          title: '请输入场景描述',
          icon: 'none'
        })
        return
      }
      
      const panel = this.pages[this.editingPageIndex].panels[this.editingPanelIndex]
      panel.description = this.editingPanel.description
      panel.characters = this.editingPanel.characters_text ? 
        this.editingPanel.characters_text.split(',').map(s => s.trim()).filter(s => s) : []
      panel.dialogue = this.editingPanel.dialogue_text ? 
        this.editingPanel.dialogue_text.split('|').map(s => s.trim()).filter(s => s) : []
      panel.camera_angle = this.editingPanel.camera_angle
      panel.emotion = this.editingPanel.emotion
      
      this.closeModal()
      
      // 标记有未保存的更改
      this.hasUnsavedChanges = true
      
      // 如果有项目ID，自动保存到数据库
      if (this.projectId) {
        await this.saveStoryboardToDatabase()
      } else {
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
      }
    },
    
    deletePanel(pageIndex, panelIndex) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个面板吗？',
        success: (res) => {
          if (res.confirm) {
            this.pages[pageIndex].panels.splice(panelIndex, 1)
            // 重新编号
            this.pages[pageIndex].panels.forEach((panel, index) => {
              panel.panel_index = index + 1
            })
            // 标记有未保存的更改
            this.hasUnsavedChanges = true
          }
        }
      })
    },
    
    deletePage(pageIndex) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这一页吗？',
        success: (res) => {
          if (res.confirm) {
            this.pages.splice(pageIndex, 1)
            // 重新编号
            this.pages.forEach((page, index) => {
              page.page_index = index + 1
            })
            // 标记有未保存的更改
            this.hasUnsavedChanges = true
          }
        }
      })
    },
    
    closeModal() {
      this.showEditModal = false
      this.editingPageIndex = -1
      this.editingPanelIndex = -1
    }
  }
}
</script>

<style>
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
  padding: 20rpx;
  background-color: white;
  border-radius: 10rpx;
}

.header-actions {
  display: flex;
  gap: 15rpx;
  align-items: center;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
}

.save-btn {
  padding: 10rpx 20rpx;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5rpx;
  font-size: 28rpx;
}

.save-btn:disabled {
  background-color: #6c757d;
  opacity: 0.6;
}

.back-btn {
  padding: 10rpx 20rpx;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 5rpx;
  font-size: 28rpx;
}

.storyboard-content {
  background-color: white;
  border-radius: 10rpx;
  padding: 30rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 30rpx;
  display: block;
}

.page-item {
  border: 2rpx solid #eee;
  border-radius: 10rpx;
  margin-bottom: 30rpx;
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background-color: #f8f8f8;
  border-bottom: 1rpx solid #eee;
}

.page-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.page-actions {
  display: flex;
  gap: 10rpx;
}

.action-btn {
  padding: 8rpx 16rpx;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 5rpx;
  font-size: 24rpx;
}

.action-btn.delete {
  background-color: #ff3b30;
}

.panels-container {
  padding: 20rpx;
}

.panel-item {
  border: 1rpx solid #ddd;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 20rpx;
  background-color: #f0f0f0;
  border-bottom: 1rpx solid #ddd;
}

.panel-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.panel-actions {
  display: flex;
  gap: 8rpx;
}

.small-btn {
  padding: 6rpx 12rpx;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 4rpx;
  font-size: 22rpx;
}

.small-btn.delete {
  background-color: #ff3b30;
}

.panel-content {
  padding: 20rpx;
}

.panel-field {
  margin-bottom: 15rpx;
}

.field-label {
  font-size: 26rpx;
  color: #666;
  font-weight: bold;
  display: block;
  margin-bottom: 8rpx;
}

.field-value {
  font-size: 28rpx;
  color: #333;
  line-height: 1.5;
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
  border-radius: 10rpx;
  width: 90%;
  max-height: 80%;
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
  max-height: 60vh;
  overflow-y: auto;
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

.form-input, .form-textarea, .form-select {
  width: 100%;
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  padding: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.form-textarea {
  min-height: 120rpx;
  resize: vertical;
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
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: bold;
}

.btn.cancel {
  background-color: #f0f0f0;
  color: #666;
}

.btn.confirm {
  background-color: #007aff;
  color: white;
}
</style>
