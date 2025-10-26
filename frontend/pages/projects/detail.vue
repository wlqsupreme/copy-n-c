<template>
  <view class="container">
    <!-- 页面头部 -->
    <view class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <text class="title">{{ projectInfo.title || '项目详情' }}</text>
    </view>

    <!-- 项目信息 -->
    <view class="info-section">
      <view class="info-card">
        <text class="info-label">项目标题</text>
        <text class="info-value">{{ projectInfo.title }}</text>
      </view>
      <view class="info-card" v-if="projectInfo.description">
        <text class="info-label">项目描述</text>
        <text class="info-value">{{ projectInfo.description }}</text>
      </view>
      <view class="info-card">
        <text class="info-label">项目状态</text>
        <text class="info-value">{{ projectInfo.visibility === 'public' ? '公开' : '私有' }}</text>
      </view>
    </view>

    <!-- 角色基础设定 -->
    <view class="section">
      <view class="section-header">
		  <text class="section-title">角色基础设定</text>
		  <text class="section-count">共 {{ characters.length }} 个角色</text>
	  </view>
      
	  <view class="section-header">
	    <text class="section-description">【角色基础设定】包含：年龄, 性别, 身高, 体型, 发型, 发色, 眼睛, 穿着, 特殊配饰等</text>
	  </view>

      <view class="characters-list" v-if="characters.length > 0">
        <view class="character-card" v-for="char in characters" :key="char.character_id">
          <view class="character-header">
            <text class="character-name">{{ char.name }}</text>
          </view>
          <text class="character-description">{{ char.description || '暂无描述' }}</text>
          <button class="edit-character-btn" @click="editCharacter(char)">编辑</button>
        </view>
      </view>
      
      <view class="empty-state" v-else>
        <text class="empty-text">暂无角色</text>
      </view>
    </view>

    <!-- 分镜（章节）列表 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">分镜（章节）列表</text>
        <text class="section-count">共 {{ chapters.length }} 个章节</text>
      </view>
      
      <view class="chapters-list" v-if="chapters.length > 0">
        <view 
          class="chapter-card" 
          v-for="(chapter, index) in chapters" 
          :key="chapter.text_id"
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
          @click="onChapterClick(chapter)"
          @touchstart.passive="onTouchStart(index, $event)"
          @touchmove.passive="onTouchMove($event)"
          @touchend="onTouchEnd($event)"
        >
          <view class="drag-handle">⋮⋮</view>
          <view class="chapter-content">
            <view class="chapter-header">
              <text class="chapter-name">{{ chapter.chapter_name }}</text>
              <view class="chapter-status" :class="chapter.processing_status">
                <text class="status-text">{{ getStatusText(chapter.processing_status) }}</text>
              </view>
            </view>
            <view class="chapter-meta">
              <text class="meta-item">章节编号：{{ chapter.chapter_number }}</text>
              <text class="meta-item">分镜数量：{{ chapter.storyboard_count }} 个</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-else>
        <text class="empty-text">暂无章节，请先导入章节</text>
      </view>
      
      <view class="add-chapter-section">
        <button class="add-chapter-btn" @click="addNewChapter">
          + 新增章节
        </button>
      </view>
    </view>

    <!-- 编辑角色弹窗 -->
    <view class="modal-overlay" v-if="showEditCharacterModal" @click="closeCharacterModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">编辑角色描述</text>
          <button class="close-btn" @click="closeCharacterModal">×</button>
        </view>
        
        <view class="modal-body">
          <view class="form-group">
            <text class="form-label">角色名称：</text>
            <text class="form-readonly">{{ editingCharacter.name }}</text>
          </view>
          
          <view class="form-group">
            <text class="form-label">角色描述：</text>
            <text class="form-hint">【角色基础设定】包含：年龄, 性别, 身高, 体型, 发型, 发色, 眼睛, 穿着, 特殊配饰等</text>
            <textarea 
              class="form-textarea" 
              v-model="editingCharacter.description"
              placeholder="输入角色描述..."
            ></textarea>
          </view>
        </view>
        
        <view class="modal-footer">
          <button class="cancel-btn" @click="closeCharacterModal">取消</button>
          <button class="save-btn" @click="saveCharacter" :disabled="isLoading">
            {{ isLoading ? '保存中...' : '保存' }}
          </button>
        </view>
      </view>
    </view>

    <!-- 加载提示 -->
    <view class="loading-mask" v-if="isLoading">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script>
import authManager from '../../utils/auth.js'

export default {
  data() {
    return {
      projectId: null,
      projectInfo: {},
      chapters: [],
      characters: [],
      isLoading: false,
      showEditCharacterModal: false,
      editingCharacter: {},
      draggedIndex: null,
      dragOverIndex: null,
      isDragging: false,
      touchStartY: 0,
      touchActiveIndex: null,
      suppressClickTimeout: null
    }
  },
  
  onLoad(options) {
    if (options.projectId) {
      this.projectId = options.projectId;
      this.loadProjectData();
    } else {
      uni.showToast({ title: '缺少项目ID', icon: 'none' });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    }
  },
  
  onShow() {
    // 每次显示页面时重新加载数据
    if (this.projectId) {
      this.loadProjectData();
    }
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
    
    async loadProjectData() {
      if (!this.checkAuth()) return;
      
      this.isLoading = true;
      
      try {
        // 并行加载所有数据
        await Promise.all([
          this.loadProjectInfo(),
          this.loadChapters(),
          this.loadCharacters()
        ]);
      } catch (error) {
        console.error('加载项目数据失败:', error);
        uni.showToast({
          title: '加载失败: ' + error.message,
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    },
    
    async loadProjectInfo() {
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/project/${this.projectId}`,
          method: 'GET'
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          this.projectInfo = response.data.project;
        } else {
          throw new Error('加载项目信息失败');
        }
      } catch (error) {
        console.error('加载项目信息失败:', error);
        throw error;
      }
    },
    
    async loadChapters() {
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/projects/${this.projectId}/chapters`,
          method: 'GET'
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          this.chapters = response.data.chapters;
        } else {
          throw new Error('加载章节列表失败');
        }
      } catch (error) {
        console.error('加载章节列表失败:', error);
        throw error;
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
        } else {
          throw new Error('加载角色列表失败');
        }
      } catch (error) {
        console.error('加载角色列表失败:', error);
        throw error;
      }
    },
    
    goToEditChapter(chapter) {
      // 跳转到编辑分镜页面
      uni.navigateTo({
        url: `/pages/storyboard/layout-planner?project_id=${this.projectId}&text_id=${chapter.text_id}`
      });
    },
    
    getStatusText(status) {
      const statusMap = {
        'pending': '待处理',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '处理失败'
      };
      return statusMap[status] || '未知';
    },
    
    editCharacter(char) {
      this.editingCharacter = { ...char };
      this.showEditCharacterModal = true;
    },
    
    closeCharacterModal() {
      this.showEditCharacterModal = false;
      this.editingCharacter = {};
    },
    
    async saveCharacter() {
      this.isLoading = true;
      
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/character/${this.editingCharacter.character_id}`,
          method: 'PUT',
          data: {
            description: this.editingCharacter.description
          }
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          // 更新本地数据
          const index = this.characters.findIndex(c => c.character_id === this.editingCharacter.character_id);
          if (index > -1) {
            this.characters[index].description = this.editingCharacter.description;
          }
          uni.showToast({ title: '保存成功', icon: 'success' });
          this.closeCharacterModal();
        } else {
          throw new Error('保存失败');
        }
      } catch (e) {
        uni.showToast({ title: e.message || '保存失败', icon: 'none' });
      } finally {
        this.isLoading = false;
      }
    },
    
    addNewChapter() {
      uni.navigateTo({
        url: `/pages/storyboard/script-analyzer?project_id=${this.projectId}`
      });
    },
    
    // 桌面原生 dragstart（HTML5）
    onNativeDragStart(index, event) {
      // 不要 preventDefault() 在 dragstart 上
      this.draggedIndex = index;
      this.isDragging = true;
      try {
        // 放入 dataTransfer 以便 drop 读取（某些浏览器需要）
        event.dataTransfer.setData('text/plain', String(index));
        event.dataTransfer.effectAllowed = 'move';
      } catch (e) {
        // ignore
      }
      this._suppressClick();
    },

    onNativeDragEnter(index, event) {
      // 当拖拽元素进入某项，更新 hover 目标显示
      this.dragOverIndex = index;
    },

    onNativeDragOver(index, event) {
      // 保持 dragOverIndex（dragover 上一般需要 preventDefault 才能 drop）
      this.dragOverIndex = index;
    },

    onNativeDrop(index, event) {
      event.preventDefault();
      let src = null;
      try { 
        src = parseInt(event.dataTransfer.getData('text/plain'), 10); 
      } catch (e) { 
        src = this.draggedIndex; 
      }

      const dest = index;
      this._reorderAndSave(src, dest);
      // 在 drop 后立刻清理状态（同时 onNativeDragEnd 也会被触发，但这里先清理）
      this._clearDragState();
    },

    onNativeDragEnd(event) {
      // dragend 一定会触发（即使 drop 未触发），用于清理残留样式
      // 若需要在没有 drop 的情况下同步一次最终位置，也可在这判断并保存
      // 这里直接清理状态
      this._clearDragState();
    },

    // 点击时候的统一入口，若刚发生过拖拽则屏蔽点击导航
    onChapterClick(chapter) {
      if (this.isDragging) {
        return;
      }
      this.goToEditChapter(chapter);
    },

    // 移动端 touch 实现（fallback）
    onTouchStart(index, event) {
      const touch = (event.touches && event.touches[0]) || event;
      this.touchStartY = touch.clientY;
      this.touchActiveIndex = index;
      this.draggedIndex = index;
      this.isDragging = false;
    },

    onTouchMove(event) {
      if (this.touchActiveIndex === null) return;
      const touch = (event.touches && event.touches[0]) || event;
      const y = touch.clientY;

      if (!this.isDragging && Math.abs(y - this.touchStartY) > 8) {
        this.isDragging = true;
        this._suppressClick();
      }

      if (!this.isDragging) return;

      // 根据触点位置判断当前悬停的目标 index
      const el = document.elementFromPoint(touch.clientX, touch.clientY);
      if (!el) return;
      const cardEl = el.closest ? el.closest('.chapter-card') : this._closestByAttr(el, 'chapter-card');
      if (!cardEl) return;
      const nodes = Array.from(document.querySelectorAll('.chapter-card'));
      const overIndex = nodes.indexOf(cardEl);
      if (overIndex > -1 && overIndex !== this.dragOverIndex) {
        this.dragOverIndex = overIndex;
        this._swapArray(this.chapters, this.draggedIndex, overIndex);
        this.draggedIndex = overIndex;
      }
    },

    onTouchEnd(event) {
      if (this.isDragging) {
        this.updateChapterOrder();
      }
      this._clearDragState();
    },

    // 复用：把 src/dest 交换并保存
    _reorderAndSave(src, dest) {
      if (src == null || dest == null || src === dest) return;
      this._swapArray(this.chapters, src, dest);
      this.updateChapterOrder();
    },

    // 交换数组中两个元素（就地）
    _swapArray(arr, i, j) {
      if (!Array.isArray(arr) || i === j) return;
      const item = arr.splice(i, 1)[0];
      arr.splice(j, 0, item);
    },

    // 清理拖拽状态
    _clearDragState() {
      this.draggedIndex = null;
      this.dragOverIndex = null;
      this.touchActiveIndex = null;
      setTimeout(() => { this.isDragging = false; }, 50);
    },

    // 在拖拽开始时短时间抑制 click 行为
    _suppressClick() {
      this.isDragging = true;
      if (this.suppressClickTimeout) clearTimeout(this.suppressClickTimeout);
      this.suppressClickTimeout = setTimeout(() => {
        this.isDragging = false;
      }, 250);
    },

    // 兼容查找最近父元素
    _closestByAttr(node, className) {
      while (node && node !== document) {
        if (node.classList && node.classList.contains(className)) return node;
        node = node.parentNode;
      }
      return null;
    },

    async updateChapterOrder() {
      try {
        const updates = this.chapters.map((chapter, index) => ({
          text_id: chapter.text_id,
          order_index: index
        }));

        for (const update of updates) {
          await uni.request({
            url: `http://localhost:8000/api/v1/source_text/${update.text_id}`,
            method: 'PUT',
            data: { order_index: update.order_index }
          });
        }

        uni.showToast({ title: '排序已保存', icon: 'success' });
      } catch (e) {
        console.error(e);
        uni.showToast({ title: '保存排序失败', icon: 'none' });
      }
    },
    
    goBack() {
      uni.navigateBack();
    }
  }
}
</script>

<style scoped>
.container {
  padding: 20rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
  padding-bottom: 40rpx;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30rpx;
  padding: 20rpx;
  background-color: white;
  border-radius: 10rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.back-btn {
  padding: 10rpx 20rpx;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 5rpx;
  font-size: 28rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

/* 项目信息卡片 */
.info-section {
  margin-bottom: 30rpx;
}

.info-card {
  background-color: white;
  padding: 30rpx;
  margin-bottom: 20rpx;
  border-radius: 10rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.info-label {
  display: block;
  font-size: 26rpx;
  color: #999;
  margin-bottom: 10rpx;
}

.info-value {
  display: block;
  font-size: 32rpx;
  color: #333;
  font-weight: 500;
}

/* 通用章节和角色区域 */
.section {
  background-color: white;
  padding: 30rpx;
  margin-bottom: 30rpx;
  border-radius: 10rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #f0f0f0;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.section-count {
  font-size: 26rpx;
  color: #999;
}

/* 角色卡片 */
.characters-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.character-card {
  border: 2rpx solid #e0e0e0;
  border-radius: 10rpx;
  padding: 30rpx;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.character-header {
  margin-bottom: 0;
}

.character-name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.character-description {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  flex: 1;
}

/* 章节卡片 */
.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.chapter-card {
  border: 2rpx solid #e0e0e0;
  border-radius: 10rpx;
  padding: 30rpx;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 20rpx;
  position: relative;
}

.chapter-card:active {
  background-color: #e8e8e8;
  border-color: #007aff;
}

.chapter-card.dragging {
  opacity: 0.5;
  transform: scale(1.05);
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.2);
}

.chapter-card.drag-over {
  border-color: #007aff;
  transform: translateY(6rpx);
}

.drag-handle {
  font-size: 24rpx;
  color: #999;
  cursor: grab;
  user-select: none;
  padding: 10rpx;
  line-height: 1;
}

.drag-handle:active {
  cursor: grabbing;
}

.chapter-content {
  flex: 1;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.chapter-name {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.chapter-status {
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
}

.chapter-status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.chapter-status.processing {
  background-color: #cfe2ff;
  color: #084298;
}

.chapter-status.completed {
  background-color: #d1e7dd;
  color: #0f5132;
}

.chapter-status.failed {
  background-color: #f8d7da;
  color: #842029;
}

.status-text {
  font-size: 22rpx;
}

.chapter-meta {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.meta-item {
  font-size: 24rpx;
  color: #666;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60rpx 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

/* 加载遮罩 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-text {
  color: white;
  font-size: 32rpx;
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

.form-readonly {
  padding: 8px 12px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}

.form-hint {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  display: block;
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

.edit-character-btn {
  padding: 5rpx 200rpx;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6rpx;
  font-size: 26rpx;
  align-self: flex-start;
  margin-top: 10rpx;
  min-width: 120rpx;
  text-align: center;
}

.character-hint {
  font-size: 24rpx;
  color: #999;
  margin-top: 10rpx;
  display: block;
}

.section-description {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 20rpx;
  padding: 20rpx;
  background-color: #f8f9fa;
  border-radius: 8rpx;
  border-left: 4rpx solid #007aff;
  word-wrap: break-word;
  white-space: normal;
  line-height: 1.5;
  overflow-wrap: break-word;
  max-width: 100%;
  box-sizing: border-box;
}

.add-chapter-section {
  margin-top: 30rpx;
  padding-top: 20rpx;
  border-top: 2rpx solid #f0f0f0;
}

.add-chapter-btn {
  width: 100%;
  height: 80rpx;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 10rpx;
  font-size: 32rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

