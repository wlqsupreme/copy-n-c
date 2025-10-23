<template>
  <view class="container">
    <view class="header">
      <text class="title">分镜规划</text>
      <button class="back-btn" @click="goBack">返回</button>
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
      editingPanelIndex: -1
    }
  },
  
  onLoad(options) {
    // 从上一页接收分镜数据
    if (options.storyboard) {
      try {
        const storyboard = JSON.parse(decodeURIComponent(options.storyboard))
        this.pages = storyboard.pages || []
      } catch (e) {
        console.error('解析分镜数据失败:', e)
        uni.showToast({
          title: '数据解析失败',
          icon: 'none'
        })
      }
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack()
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
    
    savePanel() {
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
      uni.showToast({
        title: '保存成功',
        icon: 'success'
      })
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

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
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
