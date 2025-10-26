<template>
  <view class="container">
    <view class="header">
      <text class="title">分镜规划</text>
      <view class="header-actions">
        <button class="edit-chapter-btn" @click="openEditChapterModal">编辑章节</button>
        <button class="back-btn" @click="goBack">返回</button>
      </view>
    </view>
    
    <view class="storyboard-content">
      <!-- 角色基础设定 -->
      <view class="characters-section">
        <text class="section-title">角色基础设定</text>
        <text class="section-description">【角色基础设定】包含：年龄, 性别, 身高, 体型, 发型, 发色, 眼睛, 穿着, 特殊配饰等</text>
        
        <view class="characters-list" v-if="characters.length > 0">
          <view class="character-card" v-for="char in characters" :key="char.character_id">
            <view class="character-header">
              <text class="character-name">{{ char.name }}</text>
            </view>
            <text class="character-description">{{ char.description || '暂无描述' }}</text>
          </view>
        </view>
        
        <view class="empty-state" v-else>
          <text class="empty-text">暂无角色</text>
        </view>
      </view>
      
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
              <text class="field-label">角色外貌（分镜特定）：</text>
              <text class="field-value">{{ panel.character_appearance }}</text>
              <text class="field-hint" v-if="panel.character_id">✓ 此角色已设定：{{ getCharacterName(panel.character_id) }}</text>
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
    
    <!-- 编辑章节弹窗 -->
    <view class="modal-overlay" v-if="showEditChapterModal" @click="closeChapterModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑章节信息</text>
          <button class="close-btn" @click="closeChapterModal">×</button>
        </view>
        
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">章节编号：</text>
            <input 
              class="form-input" 
              v-model="editingChapter.chapter_number"
              type="number"
              placeholder="输入章节编号..."
            />
          </view>
          
          <view class="form-group">
            <text class="form-label">章节名称：</text>
            <input 
              class="form-input" 
              v-model="editingChapter.chapter_name"
              placeholder="输入章节名称..."
            />
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="cancel-btn" @click="closeChapterModal">取消</button>
          <button class="save-btn" @click="saveChapter" :disabled="isLoading">
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
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
            <text class="form-label">角色外貌（分镜特定）：</text>
            <text class="form-hint">描述该分镜中角色的特定外貌变化（如：衣服破损、受伤状态等）</text>
            <textarea 
              class="form-textarea" 
              v-model="editingPanel.character_appearance"
              placeholder="描述角色在该分镜中的特定外貌..."
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
      characters: [],
      chapterInfo: null,
      isLoading: false,
      showEditModal: false,
      showEditChapterModal: false,
      editingPanel: {},
      editingChapter: {},
      editingPanelIndex: -1
    }
  },
  
  onLoad(options) {
    if (options.project_id && options.text_id) {
      this.projectId = options.project_id;
      this.textId = options.text_id;
      this.loadChapterInfo();
      this.loadCharacters();
      this.loadPanelsData();
    } else {
      uni.showToast({ title: '缺少项目或文本ID', icon: 'none' });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    }
  },
  
  methods: {
    async loadChapterInfo() {
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/source_texts/${this.textId}`,
          method: 'GET'
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          this.chapterInfo = response.data.chapter;
        }
      } catch (e) {
        console.error('加载章节信息失败:', e);
      }
    },
    
    async loadCharacters() {
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/projects/${this.projectId}/characters`,
          method: 'GET'
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          this.characters = response.data.characters;
        }
      } catch (e) {
        console.error('加载角色信息失败:', e);
      }
    },
    
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
    
    async deletePanel(panelIndex) {
      const panelToDelete = this.panels[panelIndex];
      const panelId = panelToDelete.storyboard_id;

      uni.showModal({
        title: '确认删除',
        content: `确定要删除面板 ${panelToDelete.panel_index + 1} 吗？`,
        success: async (res) => {
          if (res.confirm) {
            uni.showLoading({ title: '删除中...' });
            try {
              const response = await uni.request({
                url: `http://localhost:8000/api/v1/storyboard/${panelId}`,
                method: 'DELETE'
              });

              if (response.statusCode === 200 && response.data.ok) {
                this.panels.splice(panelIndex, 1);
                // 可选：重新编排 panel_index (如果后端不处理的话)
                this.panels.forEach((p, i) => p.panel_index = i);
                uni.showToast({ title: '删除成功', icon: 'success' });
              } else {
                throw new Error(response.data.detail || '删除失败');
              }
            } catch (e) {
              uni.showToast({ title: e.message || '删除失败', icon: 'none' });
            } finally {
              uni.hideLoading();
            }
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
    },
    
    openEditChapterModal() {
      this.editingChapter = { ...this.chapterInfo };
      this.showEditChapterModal = true;
    },
    
    closeChapterModal() {
      this.showEditChapterModal = false;
      this.editingChapter = {};
    },
    
    async saveChapter() {
      this.isLoading = true;
      
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/source_text/${this.textId}`,
          method: 'PUT',
          data: {
            chapter_number: parseInt(this.editingChapter.chapter_number),
            chapter_name: this.editingChapter.chapter_name
          }
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          this.chapterInfo = { ...this.editingChapter };
          uni.showToast({ title: '保存成功', icon: 'success' });
          this.closeChapterModal();
        } else {
          throw new Error('保存失败');
        }
      } catch (e) {
        uni.showToast({ title: e.message || '保存失败', icon: 'none' });
      } finally {
        this.isLoading = false;
      }
    },
    
    getCharacterName(characterId) {
      const character = this.characters.find(c => c.character_id === characterId);
      return character ? character.name : '未知角色';
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

.edit-chapter-btn {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  margin-right: 10px;
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

.field-hint {
  font-size: 12px;
  color: #28a745;
  margin-top: 4px;
  display: block;
}

.form-hint {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  display: block;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

/* 角色基础设定样式 */
.characters-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007aff;
  word-wrap: break-word;
  white-space: normal;
  line-height: 1.5;
  overflow-wrap: break-word;
  max-width: 100%;
  box-sizing: border-box;
}

.characters-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.character-card {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.character-header {
  margin-bottom: 0;
}

.character-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.character-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  flex: 1;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-text {
  font-size: 14px;
  color: #999;
}
</style>
