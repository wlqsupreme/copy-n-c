<template>
  <view class="modal-overlay" v-if="visible" @click="handleOverlayClick">
    <view class="modal-content" @click.stop>
      <view class="modal-header">
        <text class="modal-title">{{ isEdit ? '编辑分镜面板' : '添加分镜面板' }}</text>
        <button class="close-btn" @click="handleClose">×</button>
      </view>
      
      <view class="modal-body">
        <!-- 原文片段 -->
        <view class="form-group">
          <text class="form-label">原文片段：</text>
          <text class="field-description">该分镜对应的原始小说文本片段 (方便用户对照)</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.original_text_snippet"
            placeholder="输入原文片段..."
          ></textarea>
        </view>
        
        <!-- 角色外貌 -->
        <view class="form-group">
          <text class="form-label">角色外貌：</text>
          <text class="field-description">【角色外貌】的详细描述 (例如：年龄, 性别, 身高, 体型, 发型, 发色, 眼睛, 穿着, 特殊配饰)</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.character_appearance"
            placeholder="描述角色在该分镜中的特定外貌..."
          ></textarea>
        </view>
        
        <!-- 场景与光照 -->
        <view class="form-group">
          <text class="form-label">场景与光照：</text>
          <text class="field-description">【场景与光照】的详细描述 (例如：地点, 时间, 天气, 光源, 氛围)</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.scene_and_lighting"
            placeholder="描述场景和光照..."
          ></textarea>
        </view>
        
        <!-- 镜头与构图 -->
        <view class="form-group">
          <text class="form-label">镜头与构图：</text>
          <text class="field-description">【镜头与构图】的详细描述 (例如：镜头景别(特写/中景/全景), 角度(正面/四分之三/低角度/高角度), 聚焦于角色, 动态姿势)</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.camera_and_composition"
            placeholder="描述镜头和构图..."
          ></textarea>
        </view>
        
        <!-- 表情与动作 -->
        <view class="form-group">
          <text class="form-label">表情与动作：</text>
          <text class="field-description">【表情与动作】的详细描述 (例如：情绪, 面部表情, 手势, 动作)</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.expression_and_action"
            placeholder="描述表情和动作..."
          ></textarea>
        </view>
        
        <!-- 风格要求 -->
        <view class="form-group">
          <text class="form-label">风格要求：</text>
          <text class="field-description">【风格要求】的详细描述 (例如：漫画, 黑白网点, 清晰线条, 分镜构图, 高清晰度, 详细背景, 角色设计一致性)</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.style_requirements"
            placeholder="描述风格要求..."
          ></textarea>
        </view>
        
        <!-- 多人对话编辑 -->
        <view class="form-group">
          <text class="form-label">对话内容：</text>
          <text class="field-description">【对话】的详细描述 - 存储面板中的多个元素，例如 [{"character_id": "uuid", "dialogue": "你好"}, {"character_id": "uuid2", "dialogue": "再见"}]</text>
          <view class="dialogue-editor">
            <view class="dialogue-item" v-for="(element, elementIndex) in formData.panel_elements" :key="elementIndex">
              <view class="dialogue-row">
                <select class="character-select" v-model="element.character_id">
                  <option value="">选择角色</option>
                  <option v-for="char in characters" :key="char.character_id" :value="char.character_id">
                    {{ char.name }}
                  </option>
                </select>
                <input 
                  class="dialogue-input" 
                  v-model="element.dialogue"
                  placeholder="输入对话内容..."
                />
                <button class="remove-dialogue-btn" @click="removeDialogue(elementIndex)">删除</button>
              </view>
            </view>
            <button class="add-dialogue-btn" @click="addDialogue">添加对话</button>
          </view>
        </view>
      </view>
      
      <view class="modal-footer">
        <button class="cancel-btn" @click="handleClose">取消</button>
        <button class="save-btn" @click="handleSave" :disabled="isLoading">
          {{ isLoading ? '保存中...' : (isEdit ? '更新' : '创建') }}
        </button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'StoryboardEditor',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    characters: {
      type: Array,
      default: () => []
    },
    editingData: {
      type: Object,
      default: () => ({})
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      formData: {
        original_text_snippet: '',
        character_appearance: '',
        scene_and_lighting: '',
        camera_and_composition: '',
        expression_and_action: '',
        style_requirements: '',
        panel_elements: []
      }
    }
  },
  
  computed: {
    isEdit() {
      return this.editingData && this.editingData.storyboard_id
    }
  },
  
  watch: {
    visible(newVal) {
      if (newVal) {
        this.initFormData()
      }
    },
    editingData: {
      handler() {
        if (this.visible) {
          this.initFormData()
        }
      },
      deep: true
    }
  },
  
  methods: {
    initFormData() {
      if (this.isEdit) {
        // 编辑模式：使用传入的数据
        this.formData = {
          original_text_snippet: this.editingData.original_text_snippet || '',
          character_appearance: this.editingData.character_appearance || '',
          scene_and_lighting: this.editingData.scene_and_lighting || '',
          camera_and_composition: this.editingData.camera_and_composition || '',
          expression_and_action: this.editingData.expression_and_action || '',
          style_requirements: this.editingData.style_requirements || '',
          panel_elements: this.editingData.panel_elements ? [...this.editingData.panel_elements] : []
        }
        
        // 兼容旧数据：如果有 character_id 但没有 panel_elements，创建一个
        if (this.editingData.character_id && this.formData.panel_elements.length === 0) {
          this.formData.panel_elements = [{
            character_id: this.editingData.character_id,
            dialogue: this.editingData.dialogue || ''
          }]
        }
      } else {
        // 新建模式：重置表单
        this.formData = {
          original_text_snippet: '',
          character_appearance: '',
          scene_and_lighting: '',
          camera_and_composition: '',
          expression_and_action: '',
          style_requirements: '',
          panel_elements: []
        }
      }
    },
    
    addDialogue() {
      this.formData.panel_elements.push({
        character_id: '',
        dialogue: ''
      })
    },
    
    removeDialogue(index) {
      this.formData.panel_elements.splice(index, 1)
    },
    
    handleSave() {
      // 验证必填字段
      if (!this.formData.original_text_snippet?.trim()) {
        uni.showToast({ title: '原文片段不能为空', icon: 'none' })
        return
      }
      
      // 发送事件给父组件
      this.$emit('save', {
        ...this.formData,
        isEdit: this.isEdit,
        storyboard_id: this.isEdit ? this.editingData.storyboard_id : null
      })
    },
    
    handleClose() {
      this.$emit('close')
    },
    
    handleOverlayClick() {
      this.handleClose()
    }
  }
}
</script>

<style scoped>
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
  width: 95%;
  max-width: 700px;
  max-height: 90vh;
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
  margin-bottom: 20px;
}

.form-label {
  font-weight: bold;
  color: #555;
  display: block;
  margin-bottom: 5px;
  font-size: 16px;
}

.field-description {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  display: block;
  line-height: 1.4;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #007bff;
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

/* 对话相关样式 */
.dialogue-editor {
  margin-top: 8px;
}

.dialogue-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.character-select {
  flex: 0 0 120px;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.dialogue-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.remove-dialogue-btn {
  flex: 0 0 auto;
  padding: 6px 12px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
}

.add-dialogue-btn {
  padding: 8px 16px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 8px;
}
</style>
