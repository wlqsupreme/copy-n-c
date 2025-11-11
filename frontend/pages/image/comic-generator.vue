<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <button class="back-btn" @click="goBack">←</button>
        <text class="page-title">🎨 生成漫画</text>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <view class="subtitle">为分镜生成完整的漫画图片（含对话框）</view>

      <!-- 分镜信息展示 -->
      <view v-if="storyboardInfo" class="storyboard-info">
        <view class="info-box">
          <text class="info-title">📋 分镜信息</text>
          
          <view class="info-field">
            <text class="field-label">原文片段：</text>
            <text class="field-value">{{ storyboardInfo.original_text_snippet || '-' }}</text>
          </view>
          
          <view class="info-field">
            <text class="field-label">角色外观：</text>
            <text class="field-value">{{ storyboardInfo.character_appearance || '-' }}</text>
          </view>
          
          <view class="info-field">
            <text class="field-label">场景光线：</text>
            <text class="field-value">{{ storyboardInfo.scene_and_lighting || '-' }}</text>
          </view>
          
          <view class="info-field">
            <text class="field-label">镜头构图：</text>
            <text class="field-value">{{ storyboardInfo.camera_and_composition || '-' }}</text>
          </view>
          
          <view class="info-field">
            <text class="field-label">表情动作：</text>
            <text class="field-value">{{ storyboardInfo.expression_and_action || '-' }}</text>
          </view>
          
          <view class="info-field">
            <text class="field-label">风格要求：</text>
            <text class="field-value">{{ storyboardInfo.style_requirements || '-' }}</text>
          </view>
          
          <!-- 对话内容预览 -->
          <view v-if="hasDialogue" class="dialogue-preview">
            <text class="dialogue-label">💬 对话内容：</text>
            <view class="dialogue-items">
              <view class="dialogue-item" v-for="(d, idx) in dialogues" :key="idx">
                <text class="dialogue-speaker">{{ d.speaker || '旁白' }}：</text>
                <text class="dialogue-content">{{ d.text }}</text>
              </view>
            </view>
            <text class="dialogue-tip">⚡ 将自动添加对话框！</text>
          </view>
          <view v-else class="info-field">
            <text class="field-label">对话：</text>
            <text class="field-value">无</text>
          </view>
        </view>
      </view>

      <!-- 生成选项 -->
      <view class="form-section">
        <view class="form-group">
          <text class="form-label">图片尺寸</text>
          <picker mode="selector" :range="sizeOptions" range-key="label" @change="onSizeChange">
            <view class="form-picker">{{ sizeOptions[sizeIndex].label }}</view>
          </picker>
        </view>

        <button class="submit-btn" @click="generateComic" :disabled="isLoading">
          {{ isLoading ? '生成中...' : '🎨 生成完整漫画' }}
        </button>
      </view>

      <!-- 加载状态 -->
      <view class="loading" v-if="isLoading">
        <view class="spinner"></view>
        <text class="loading-text">正在生成漫画图片，请稍候（约30-60秒）...</text>
      </view>

      <!-- 生成结果 -->
      <view class="result" v-if="result">
        <view class="result-header">
          <text class="result-title">{{ result.success ? '✅ 生成成功' : '❌ 生成失败' }}</text>
        </view>
        
        <view v-if="result.success">
          <!-- 生成流程 -->
          <view class="info-box" style="background: #fff3cd; border-left-color: #ffc107;">
            <text class="info-title" style="color: #856404;">🎨 生成流程：</text>
            <view class="process-list">
              <text class="process-item">1. AI生成纯画面（不含文字）✅</text>
              <text class="process-item">2. {{ result.has_dialogue ? '自动添加对话框 ✅' : '无对话内容，跳过 ⚪' }}</text>
              <text class="process-item">3. 返回完整漫画 ✅</text>
            </view>
          </view>

          <!-- 对话内容 -->
          <view v-if="result.has_dialogue && result.dialogues" class="info-box" style="background: #e8f5e9; border-left-color: #4CAF50;">
            <text class="info-title" style="color: #2e7d32;">💬 对话内容（{{ result.dialogue_count }} 条）：</text>
            <view class="dialogue-list">
              <view class="dialogue-item" v-for="(d, idx) in result.dialogues" :key="idx">
                <text class="dialogue-speaker">{{ d.speaker || '旁白' }}：</text>
                <text class="dialogue-content">{{ d.text }}</text>
              </view>
            </view>
          </view>

          <!-- 生成的图片 -->
          <view v-if="result.image && result.image.url" class="image-grid">
            <view class="image-item">
              <image :src="result.image.url" mode="aspectFit" class="result-image"></image>
              <view class="image-info">
                <text v-if="result.has_dialogue" class="info-item">
                  <text class="info-label">✨ 对话框：</text>已自动添加！文字清晰无乱码！
                </text>
                <text v-if="result.dialogue_count" class="info-item">
                  <text class="info-label">对话数量：</text>{{ result.dialogue_count }} 条
                </text>
              </view>
            </view>
          </view>
        </view>
        
        <text v-else class="error-text">{{ result.error }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      storyboardId: null,
      projectId: null,
      textId: null,
      storyboardInfo: null,
      hasDialogue: false,
      dialogues: [],
      sizeIndex: 0,
      isLoading: false,
      result: null,
      sizeOptions: [
        { label: '1024x1024（正方形，推荐）', value: '1024x1024' },
        { label: '1792x1024（横向宽屏）', value: '1792x1024' },
        { label: '1024x1792（竖向）', value: '1024x1792' }
      ]
    }
  },
  
  onLoad(options) {
    if (options.storyboard_id && options.project_id && options.text_id) {
      this.storyboardId = options.storyboard_id;
      this.projectId = options.project_id;
      this.textId = options.text_id;
      this.loadStoryboardInfo();
    } else {
      uni.showToast({
        title: '缺少必要参数',
        icon: 'none'
      });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack();
    },
    
    async loadStoryboardInfo() {
      try {
        const response = await uni.request({
          url: `/api/v1/storyboard-gen/storyboard/${this.storyboardId}`,
          method: 'GET'
        });
        
        if (response.statusCode === 200 && response.data.ok) {
          const data = response.data.storyboard;
          this.storyboardInfo = {
            original_text_snippet: data.original_text_snippet,
            character_appearance: data.character_appearance,
            scene_and_lighting: data.scene_and_lighting,
            camera_and_composition: data.camera_and_composition,
            expression_and_action: data.expression_and_action,
            style_requirements: data.style_requirements,
            panel_elements: data.panel_elements
          };
          
          // 检查是否有对话
          this.parseDialogueInfo(data);
        }
      } catch (error) {
        console.error('加载分镜信息失败:', error);
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        });
      }
    },
    
    parseDialogueInfo(data) {
      try {
        if (data.panel_elements) {
          const panelElements = typeof data.panel_elements === 'string' 
            ? JSON.parse(data.panel_elements) 
            : data.panel_elements;
          
          if (Array.isArray(panelElements) && panelElements.length > 0) {
            const dialogueItems = panelElements.filter(el => el.dialogue && el.dialogue.trim());
            if (dialogueItems.length > 0) {
              this.hasDialogue = true;
              this.dialogues = dialogueItems.map(el => ({
                speaker: el.character_id ? '角色' : '旁白',
                text: el.dialogue
              }));
            }
          }
        }
      } catch (e) {
        console.error('解析对话信息失败:', e);
      }
    },
    
    onSizeChange(e) {
      this.sizeIndex = e.detail.value;
    },
    
    async generateComic() {
      // 检查是否有对话内容
      if (!this.hasDialogue) {
        uni.showModal({
          title: '提示',
          content: '此分镜没有对话内容，将生成不含对话框的漫画图片。是否继续？',
          confirmText: '继续生成',
          cancelText: '取消',
          success: async (res) => {
            if (res.confirm) {
              await this.executeGenerate();
            }
          }
        });
      } else {
        await this.executeGenerate();
      }
    },
    
    async executeGenerate() {
      this.isLoading = true;
      this.result = null;
      
      const size = this.sizeOptions[this.sizeIndex].value;
      
      try {
        const response = await uni.request({
          url: `/api/v1/storyboard-gen/generate-from-db/${this.storyboardId}?size=${size}`,
          method: 'POST'
        });
        
        console.log('收到响应:', response);
        console.log('响应数据:', response.data);
        
        if (response.statusCode === 200 && response.data.ok) {
      this.result = {
        success: true,
        image: response.data.image,
        has_dialogue: response.data.has_dialogue,
        dialogue_count: response.data.dialogue_count || 0,
        dialogues: response.data.dialogues || []
      };
      
      console.log('设置结果:', this.result);
      console.log('图片对象:', this.result.image);
      console.log('图片URL:', this.result.image ? this.result.image.url : 'null');
      console.log('图片URL类型:', typeof (this.result.image ? this.result.image.url : null));
      console.log('图片URL长度:', this.result.image ? (this.result.image.url ? this.result.image.url.length : 0) : 0);
          
          uni.showToast({
            title: '生成成功',
            icon: 'success'
          });
        } else {
          throw new Error(response.data.detail || '生成失败');
        }
      } catch (error) {
        console.error('生成失败:', error);
        this.result = {
          success: false,
          error: error.message || '请求失败'
        };
        
        uni.showToast({
          title: '生成失败',
          icon: 'none'
        });
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60rpx 60rpx 40rpx 60rpx;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.back-btn {
  width: 60rpx;
  height: 60rpx;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title {
  font-size: 48rpx;
  font-weight: bold;
  color: white;
}

.main-content {
  background: white;
  border-radius: 40rpx 40rpx 0 0;
  margin-top: 20rpx;
  padding: 60rpx 40rpx;
  min-height: calc(100vh - 200rpx);
}

.subtitle {
  font-size: 28rpx;
  color: #666;
  text-align: center;
  margin-bottom: 40rpx;
  display: block;
}

.storyboard-info {
  margin-bottom: 40rpx;
}

.info-box {
  background: #e3f2fd;
  padding: 30rpx;
  border-radius: 16rpx;
  margin-bottom: 40rpx;
  border-left: 8rpx solid #2196F3;
}

.info-title {
  color: #1976D2;
  font-size: 32rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}

.info-field {
  margin: 16rpx 0;
  padding: 16rpx;
  background: white;
  border-radius: 8rpx;
  font-size: 26rpx;
}

.field-label {
  color: #666;
  font-weight: bold;
  display: inline-block;
  width: 160rpx;
}

.field-value {
  color: #333;
}

.dialogue-preview {
  background: #fff3cd;
  padding: 20rpx;
  border-radius: 8rpx;
  border-left: 8rpx solid #ffc107;
  margin: 16rpx 0;
}

.dialogue-label {
  font-weight: bold;
  color: #856404;
  display: block;
  margin-bottom: 10rpx;
  font-size: 26rpx;
}

.dialogue-items {
  margin-top: 10rpx;
}

.dialogue-item {
  background: white;
  padding: 12rpx;
  border-radius: 6rpx;
  margin: 8rpx 0;
  font-size: 24rpx;
}

.dialogue-speaker {
  font-weight: bold;
  color: #856404;
  margin-right: 10rpx;
}

.dialogue-content {
  color: #333;
}

.dialogue-tip {
  font-size: 22rpx;
  color: #856404;
  display: block;
  margin-top: 10rpx;
}

.form-section {
  margin-top: 40rpx;
}

.form-group {
  margin-bottom: 40rpx;
}

.form-label {
  display: block;
  margin-bottom: 15rpx;
  font-weight: 600;
  font-size: 28rpx;
  color: #333;
}

.form-picker {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  border: 4rpx solid #e0e0e0;
  border-radius: 16rpx;
  font-size: 28rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.submit-btn {
  width: 100%;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: bold;
  transition: transform 0.2s;
}

.submit-btn:disabled {
  background: #ccc;
  transform: none;
}

.loading {
  text-align: center;
  padding: 60rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
  margin-top: 40rpx;
}

.spinner {
  border: 8rpx solid #f3f3f3;
  border-top: 8rpx solid #667eea;
  border-radius: 50%;
  width: 100rpx;
  height: 100rpx;
  animation: spin 1s linear infinite;
  margin: 0 auto 30rpx;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 26rpx;
  color: #666;
}

.result {
  margin-top: 40rpx;
  padding: 40rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
  border-left: 8rpx solid #667eea;
}

.result-header {
  margin-bottom: 30rpx;
}

.result-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #667eea;
}

.process-list {
  margin-top: 20rpx;
}

.process-item {
  font-size: 26rpx;
  color: #856404;
  line-height: 2;
  display: block;
}

.dialogue-list {
  margin-top: 20rpx;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 40rpx;
}

.image-item {
  background: white;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
}

.result-image {
  width: 100%;
  height: auto;
  min-height: 400rpx;
  display: block;
}

.image-info {
  padding: 30rpx;
}

.info-item {
  font-size: 26rpx;
  color: #333;
  line-height: 1.6;
  display: block;
  margin-bottom: 15rpx;
}

.info-label {
  font-weight: bold;
  color: #666;
}

.error-text {
  color: #f44336;
  font-size: 28rpx;
}
</style>

