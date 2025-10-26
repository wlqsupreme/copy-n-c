<template>
  <view class="popup-form-container">
    <view class="popup-title">新建小说转漫画项目</view>
    
    <view class="form-group">
      <text class="form-label">项目名称 <text class="required">*</text></text>
      <input 
        class="form-input" 
        v-model="form.title" 
        placeholder="请输入项目名称"
        :class="{ 'error': errors.title }"
      />
      <text class="error-text" v-if="errors.title">{{ errors.title }}</text>
    </view>
    
    <view class="form-group">
      <text class="form-label">项目描述</text>
      <textarea 
        class="form-textarea" 
        v-model="form.description" 
        placeholder="请输入项目描述（可选）"
      ></textarea>
    </view>

    <view class="form-group">
      <text class="form-label">小说上传方式 <text class="required">*</text></text>
      <view class="upload-method-group">
        <view 
          :class="['method-option', form.upload_method === 'single_chapter' ? 'active' : '']"
          @click="selectMethod('single_chapter')"
        >
          <view class="method-title">小说单章文字上传</view>
          <view class="method-desc">适合微调每一分镜的图片细节</view>
        </view>
        
        <view 
          :class="['method-option', form.upload_method === 'full_novel' ? 'active' : '']"
          @click="selectMethod('full_novel')"
        >
          <view class="method-title">以文件形式上传整本小说</view>
          <view class="method-desc">适合迅速生成</view>
        </view>
      </view>
    </view>

    <view class="form-group">
      <text class="form-label">默认风格提示词</text>
      <textarea 
        class="form-textarea" 
        v-model="form.default_style_prompt" 
        placeholder="例如：日系漫画, 黑白, 简洁线条"
      ></textarea>
    </view>

    <view class="form-group">
      <text class="form-label">项目可见性</text>
      <view class="radio-group">
        <view class="radio-item" @click="form.visibility = 'private'">
          <view class="radio-button" :class="{ 'checked': form.visibility === 'private' }">
            <text class="radio-dot" v-if="form.visibility === 'private'">●</text>
          </view>
          <text class="radio-text">私有 (仅自己可见)</text>
        </view>
        <view class="radio-item" @click="form.visibility = 'public'">
          <view class="radio-button" :class="{ 'checked': form.visibility === 'public' }">
            <text class="radio-dot" v-if="form.visibility === 'public'">●</text>
          </view>
          <text class="radio-text">公开 (他人可见)</text>
        </view>
      </view>
    </view>

    <view class="popup-actions">
      <button class="btn cancel" @click="$emit('close')">取消</button>
      <button class="btn confirm" @click="handleSubmit" :disabled="isSubmitting">
        <text v-if="isSubmitting">创建中...</text>
        <text v-else>创建项目</text>
      </button>
    </view>
  </view>
</template>

<script>
import authManager from '../utils/auth.js'

export default {
  name: 'NewProjectForm',
  data() {
    return {
      form: {
        title: '',
        description: '',
        upload_method: 'single_chapter', // 默认选中第一个
        default_style_prompt: '',
        visibility: 'private' // 默认私有
      },
      errors: {},
      isSubmitting: false
    }
  },
  
  methods: {
    selectMethod(method) {
      this.form.upload_method = method;
    },
    
    validateForm() {
      this.errors = {};
      
      if (!this.form.title.trim()) {
        this.errors.title = '请输入项目名称';
      } else if (this.form.title.length < 2) {
        this.errors.title = '项目名称至少2个字符';
      }
      
      return Object.keys(this.errors).length === 0;
    },
    
    async handleSubmit() {
      if (!this.validateForm()) {
        return;
      }
      
      this.isSubmitting = true;
      
      try {
        // 获取用户信息
        const userInfo = authManager.getUserInfo();
        if (!userInfo || !userInfo.user_id) {
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          });
          return;
        }
        
        // 发送创建项目请求
        const response = await uni.request({
          url: 'http://localhost:8000/api/v1/projects',
          method: 'POST',
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authManager.getToken()}`
          },
          data: {
            ...this.form,
            user_id: userInfo.user_id
          }
        });
        
        if (response.statusCode === 200 || response.statusCode === 201) {
          uni.showToast({
            title: '项目创建成功',
            icon: 'success'
          });
          
          // 通知父组件项目创建成功
          this.$emit('submit', response.data);
          this.$emit('close');
        } else {
          throw new Error(response.data.detail || '创建失败');
        }
      } catch (error) {
        console.error('创建项目失败:', error);
        uni.showToast({
          title: '创建失败: ' + error.message,
          icon: 'none'
        });
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped>
/* 弹窗表单的样式 */
.popup-form-container {
  width: 90vw; /* 移动端宽度 */
  max-width: 600rpx; /* PC端最大宽度 */
  background-color: #fff;
  padding: 40rpx;
  border-radius: 20rpx;
}

.popup-title {
  font-size: 40rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 40rpx;
  color: #333;
}

.form-group {
  margin-bottom: 40rpx;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}

.required {
  color: #ff4757;
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

.error-text {
  font-size: 24rpx;
  color: #ff4757;
  display: block;
  margin-top: 10rpx;
}

/* 上传方式选项 */
.upload-method-group {
  display: flex;
  gap: 20rpx;
}

/* 适配移动端：如果空间不够就换行 */
@media (max-width: 500px) {
  .upload-method-group {
    flex-direction: column;
  }
}

.method-option {
  flex: 1;
  border: 2rpx solid #dcdfe6;
  border-radius: 10rpx;
  padding: 30rpx 20rpx;
  cursor: pointer;
  transition: all 0.3s;
}

.method-option:hover {
  border-color: #409eff;
  box-shadow: 0 0 10rpx rgba(64, 158, 255, 0.2);
}

.method-option.active {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.method-title {
  font-weight: bold;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
}

.method-desc {
  font-size: 24rpx;
  color: #888;
}

/* 单选按钮样式 */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  cursor: pointer;
}

.radio-button {
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid #ddd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.radio-button.checked {
  border-color: #409eff;
}

.radio-dot {
  font-size: 24rpx;
  color: #409eff;
}

.radio-text {
  font-size: 28rpx;
  color: #333;
}

/* 底部操作按钮 */
.popup-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
  margin-top: 40rpx;
}

.btn {
  padding: 20rpx 40rpx;
  border: none;
  border-radius: 10rpx;
  font-size: 28rpx;
  font-weight: bold;
  cursor: pointer;
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
  cursor: not-allowed;
}
</style>
