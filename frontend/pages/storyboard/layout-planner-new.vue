<template>
  <view class="container">
    <view class="header">
      <text class="title">分镜规划</text>
      <view class="header-actions">
        <button class="back-btn" @click="goBack">返回</button>
      </view>
    </view>
    
    <view class="storyboard-content">
      <!-- 分镜面板列表 -->
      <view class="panels-section">
        <text class="section-title">分镜面板 ({{ panels.length }}个)</text>
        
        <view class="panel-item" v-for="(panel, panelIndex) in panels" :key="panel.storyboard_id">
          <view class="panel-header">
            <text class="panel-title">面板 {{ panel.panel_index + 1 }}</text>
            <view class="panel-actions">
              <button class="action-btn" @click="editPanel(panelIndex)">编辑</button>
              <button class="action-btn delete" @click="deletePanel(panelIndex)">删除</button>
            </view>
          </view>
          
          <view class="panel-content">
            <view class="panel-field">
              <text class="field-label">原文片段：</text>
              <text class="field-value">{{ panel.original_text_snippet }}</text>
            </view>
            
            <view class="panel-field">
              <text class="field-label">角色外貌：</text>
              <text class="field-value">{{ panel.character_appearance }}</text>
            </view>
            
            <view class="panel-field">
              <text class="field-label">场景光照：</text>
              <text class="field-value">{{ panel.scene_and_lighting }}</text>
            </view>
            
            <view class="panel-field">
              <text class="field-label">镜头构图：</text>
              <text class="field-value">{{ panel.camera_and_composition }}</text>
            </view>
            
            <view class="panel-field">
              <text class="field-label">表情动作：</text>
              <text class="field-value">{{ panel.expression_and_action }}</text>
            </view>
            
            <view class="panel-field">
              <text class="field-label">风格要求：</text>
              <text class="field-value">{{ panel.style_requirements }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 编辑面板弹窗 -->
    <view class="modal-overlay" v-if="showEditModal" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑分镜面板</text>
          <button class="close-btn" @click="closeModal">×</button>
        </view>
        
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">原文片段：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.original_text_snippet"
              placeholder="输入原文片段..."
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">角色外貌：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.character_appearance"
              placeholder="描述角色在该分镜中的外貌..."
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">场景光照：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.scene_and_lighting"
              placeholder="描述场景和光照..."
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">镜头构图：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.camera_and_composition"
              placeholder="描述镜头和构图..."
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">表情动作：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.expression_and_action"
              placeholder="描述表情和动作..."
            ></textarea>
          </view>
          
          <view class="form-group">
            <text class="form-label">风格要求：</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.style_requirements"
              placeholder="描述风格要求..."
            ></textarea>
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button class="save-btn" @click="savePanel" :disabled="isLoading">
            {{ isLoading ? '保存中...' : '保存' }}
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
      projectId: null,
      textId: null,
      panels: [],
      isLoading: false,
      showEditModal: false,
      editingPanel: {},
      editingPanelIndex: -1
    }
  },
  
  onLoad(options) {
    if (options.project_id && options.text_id) {
      this.projectId = options.project_id;
      this.textId = options.text_id;
      this.loadPanelsData();
    } else {
      uni.showToast({ title: '缺少项目或文本ID', icon: 'none' });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    }
  },
  
  methods: {
    async loadPanelsData() {
      this.isLoading = true;
      uni.showLoading({ title: '加载分镜中...' });
      
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/storyboards?text_id=${this.textId}`,
          method: 'GET'
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          this.panels = response.data.storyboards;
        } else {
          throw new Error('加载失败');
        }
      } catch (e) {
        uni.showToast({ title: e.message || '加载数据失败', icon: 'none' });
      } finally {
        this.isLoading = false;
        uni.hideLoading();
      }
    },
    
    editPanel(panelIndex) {
      this.editingPanelIndex = panelIndex;
      this.editingPanel = { ...this.panels[panelIndex] };
      this.showEditModal = true;
    },
    
    async savePanel() {
      if (!this.editingPanel.original_text_snippet?.trim()) {
        uni.showToast({ title: '原文片段不能为空', icon: 'none' });
        return;
      }
      
      this.isLoading = true;
      
      try {
        const panelToSave = this.editingPanel;
        const panelId = panelToSave.storyboard_id;
        
        const updates = {
          original_text_snippet: panelToSave.original_text_snippet,
          character_appearance: panelToSave.character_appearance,
          scene_and_lighting: panelToSave.scene_and_lighting,
          camera_and_composition: panelToSave.camera_and_composition,
          expression_and_action: panelToSave.expression_and_action,
          style_requirements: panelToSave.style_requirements
        };
        
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/storyboard/${panelId}`,
          method: 'PUT',
          data: updates
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          // 更新本地数据
          this.panels[this.editingPanelIndex] = { ...panelToSave };
          uni.showToast({ title: '保存成功', icon: 'success' });
          this.closeModal();
        } else {
          throw new Error('保存失败');
        }
      } catch (e) {
        uni.showToast({ title: e.message || '保存失败', icon: 'none' });
      } finally {
        this.isLoading = false;
      }
    },
    
    deletePanel(panelIndex) {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个分镜面板吗？',
        success: (res) => {
          if (res.confirm) {
            // 这里可以调用删除API
            this.panels.splice(panelIndex, 1);
            uni.showToast({ title: '删除成功', icon: 'success' });
          }
        }
      });
    },
    
    closeModal() {
      this.showEditModal = false;
      this.editingPanel = {};
      this.editingPanelIndex = -1;
    },
    
    goBack() {
      uni.navigateBack();
    }
  }
}
</script>

<style scoped>
.container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.back-btn {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}

.panels-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
}

.panel-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.panel-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
}

.action-btn.delete {
  background: #dc3545;
}

.panel-content {
  padding: 15px;
}

.panel-field {
  margin-bottom: 12px;
}

.field-label {
  font-weight: bold;
  color: #555;
  display: block;
  margin-bottom: 4px;
}

.field-value {
  color: #666;
  line-height: 1.4;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-label {
  font-weight: bold;
  color: #555;
  display: block;
  margin-bottom: 5px;
}

.form-textarea {
  width: 100%;
  min-height: 80px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}

.save-btn {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
