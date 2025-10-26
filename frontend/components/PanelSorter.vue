<template>
  <view class="modal-overlay" v-if="visible" @click="handleOverlayClick">
    <view class="modal-content" @click.stop>
      <view class="modal-header">
        <text class="modal-title">分镜面板排序</text>
        <button class="close-btn" @click="handleClose">×</button>
      </view>
      
      <view class="modal-body">
        <view class="sort-description">
          <text class="description-title">排序说明：</text>
          <text class="description-text">拖拽面板可以调整分镜顺序，排序会影响漫画的阅读顺序。每个面板都有对应的原文片段，请根据故事情节合理安排顺序。</text>
        </view>
        
        <view class="panels-list">
          <view 
            class="panel-item" 
            v-for="(panel, index) in sortedPanels" 
            :key="panel.storyboard_id"
            :class="{ 
              'dragging': draggedIndex === index,
              'drag-over': dragOverIndex === index 
            }"
            draggable="true"
            @dragstart="onNativeDragStart(index, $event)"
            @dragenter.prevent="onNativeDragEnter(index, $event)"
            @dragover.prevent="onNativeDragOver(index, $event)"
            @drop.prevent="onNativeDrop(index, $event)"
            @dragend="onNativeDragEnd($event)"
            @touchstart.passive="onTouchStart(index, $event)"
            @touchmove.passive="onTouchMove($event)"
            @touchend="onTouchEnd($event)"
          >
            <view class="drag-handle">⋮⋮</view>
            <view class="panel-content">
              <view class="panel-header">
                <text class="panel-title">面板 {{ index + 1 }}</text>
                <text class="panel-index">索引: {{ panel.panel_index }}</text>
              </view>
              <view class="panel-snippet">
                <text class="snippet-label">原文片段：</text>
                <text class="snippet-text">{{ panel.original_text_snippet || '无原文片段' }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <view class="modal-footer">
        <button class="cancel-btn" @click="handleClose">取消</button>
        <button class="save-btn" @click="handleSave" :disabled="isLoading">
          {{ isLoading ? '保存中...' : '保存排序' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'PanelSorter',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    panels: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      sortedPanels: [],
      draggedIndex: null,
      dragOverIndex: null,
      isDragging: false,
      touchStartY: 0,
      touchActiveIndex: null,
      suppressClickTimeout: null
    }
  },
  
  watch: {
    visible(newVal) {
      if (newVal) {
        this.initSortedPanels()
      }
    },
    panels: {
      handler() {
        if (this.visible) {
          this.initSortedPanels()
        }
      },
      deep: true
    }
  },
  
  methods: {
    initSortedPanels() {
      // 按 panel_index 排序
      this.sortedPanels = [...this.panels].sort((a, b) => a.panel_index - b.panel_index)
    },
    
    // 桌面原生 dragstart（HTML5）
    onNativeDragStart(index, event) {
      this.draggedIndex = index
      this.isDragging = true
      try {
        event.dataTransfer.setData('text/plain', String(index))
        event.dataTransfer.effectAllowed = 'move'
      } catch (e) {
        // ignore
      }
      this._suppressClick()
    },

    onNativeDragEnter(index, event) {
      this.dragOverIndex = index
    },

    onNativeDragOver(index, event) {
      this.dragOverIndex = index
    },

    onNativeDrop(index, event) {
      event.preventDefault()
      let src = null
      try { 
        src = parseInt(event.dataTransfer.getData('text/plain'), 10) 
      } catch (e) { 
        src = this.draggedIndex 
      }

      const dest = index
      this._reorderAndSave(src, dest)
      this._clearDragState()
    },

    onNativeDragEnd(event) {
      this._clearDragState()
    },

    // 移动端 touch 实现（fallback）
    onTouchStart(index, event) {
      const touch = (event.touches && event.touches[0]) || event
      this.touchStartY = touch.clientY
      this.touchActiveIndex = index
      this.draggedIndex = index
      this.isDragging = false
    },

    onTouchMove(event) {
      if (this.touchActiveIndex === null) return
      const touch = (event.touches && event.touches[0]) || event
      const y = touch.clientY

      if (!this.isDragging && Math.abs(y - this.touchStartY) > 8) {
        this.isDragging = true
        this._suppressClick()
      }

      if (!this.isDragging) return

      // 根据触点位置判断当前悬停的目标 index
      const el = document.elementFromPoint(touch.clientX, touch.clientY)
      if (!el) return
      const cardEl = el.closest ? el.closest('.panel-item') : this._closestByAttr(el, 'panel-item')
      if (!cardEl) return
      const nodes = Array.from(document.querySelectorAll('.panel-item'))
      const overIndex = nodes.indexOf(cardEl)
      if (overIndex > -1 && overIndex !== this.dragOverIndex) {
        this.dragOverIndex = overIndex
        this._swapArray(this.sortedPanels, this.draggedIndex, overIndex)
        this.draggedIndex = overIndex
      }
    },

    onTouchEnd(event) {
      if (this.isDragging) {
        // Touch 排序完成，不需要额外操作
      }
      this._clearDragState()
    },

    // 复用：把 src/dest 交换并保存
    _reorderAndSave(src, dest) {
      if (src == null || dest == null || src === dest) return
      this._swapArray(this.sortedPanels, src, dest)
    },

    // 交换数组中两个元素（就地）
    _swapArray(arr, i, j) {
      if (!Array.isArray(arr) || i === j) return
      const item = arr.splice(i, 1)[0]
      arr.splice(j, 0, item)
    },

    // 清理拖拽状态
    _clearDragState() {
      this.draggedIndex = null
      this.dragOverIndex = null
      this.touchActiveIndex = null
      setTimeout(() => { this.isDragging = false }, 50)
    },

    // 在拖拽开始时短时间抑制 click 行为
    _suppressClick() {
      this.isDragging = true
      if (this.suppressClickTimeout) clearTimeout(this.suppressClickTimeout)
      this.suppressClickTimeout = setTimeout(() => {
        this.isDragging = false
      }, 250)
    },

    // 兼容查找最近父元素
    _closestByAttr(node, className) {
      while (node && node !== document) {
        if (node.classList && node.classList.contains(className)) return node
        node = node.parentNode
      }
      return null
    },
    
    async handleSave() {
      this.$emit('save', this.sortedPanels)
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
  max-width: 800px;
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

.sort-description {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.description-title {
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 8px;
}

.description-text {
  color: #666;
  line-height: 1.5;
  font-size: 14px;
}

.panels-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
}

.panel-item:active {
  background-color: #e8e8e8;
  border-color: #007bff;
}

.panel-item.dragging {
  opacity: 0.5;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.panel-item.drag-over {
  border-color: #007bff;
  transform: translateY(6px);
}

.drag-handle {
  font-size: 20px;
  color: #999;
  cursor: grab;
  user-select: none;
  padding: 8px;
  line-height: 1;
}

.drag-handle:active {
  cursor: grabbing;
}

.panel-content {
  flex: 1;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.panel-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.panel-index {
  font-size: 12px;
  color: #999;
  background-color: #e9ecef;
  padding: 2px 8px;
  border-radius: 4px;
}

.panel-snippet {
  margin-top: 8px;
}

.snippet-label {
  font-size: 12px;
  color: #666;
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
}

.snippet-text {
  font-size: 14px;
  color: #555;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
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
