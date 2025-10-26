<template>
	<view class="container">
	  <view class="header">
		<button class="back-btn" @click="goBack">← 返回</button>
		<text class="title">文本分析</text>
	  </view>
	  
	  <view class="form-section">
		<view class="input-group">
		  <text class="label">章节编号 <text class="required">*</text>：</text>
		  <input 
			class="input" 
			v-model="chapterNumber" 
			type="number"
			placeholder="输入章节编号（例如：1）"
			:class="{ 'error': errors.chapterNumber }"
		  />
		  <text class="error-text" v-if="errors.chapterNumber">{{ errors.chapterNumber }}</text>
		</view>
		
		<view class="input-group">
		  <text class="label">章节名称 <text class="required">*</text>：</text>
		  <input 
			class="input" 
			v-model="chapterName" 
			placeholder="输入章节名称（例如：第一章 下山）"
			:class="{ 'error': errors.chapterName }"
		  />
		  <text class="error-text" v-if="errors.chapterName">{{ errors.chapterName }}</text>
		</view>
		
		<view class="input-group">
		  <text class="label">小说标题（可选）：</text>
		  <input 
			class="input" 
			v-model="title" 
			placeholder="输入小说标题..."
		  />
		</view>
		
		<view class="input-group">
		  <text class="label">小说文本：</text>
		  <textarea 
			class="textarea" 
			v-model="text" 
			placeholder="把小说文本粘贴到这里（支持3000-5000字）..."
			:maxlength="5000"
			rows="15"
		  ></textarea>
		  <text class="char-count">{{ text.length }}/5000</text>
		</view>
		
		<view class="input-group">
		  <text class="label">或上传文件：</text>
		  <view class="upload-section">
			<button class="upload-btn" @click="chooseFile">
			  选择文件 (TXT/Word)
			</button>
			<text class="file-info" v-if="selectedFile">{{ selectedFile.name }}</text>
		  </view>
		</view>
		
		<button class="submit-btn" @click="submitText" :disabled="loading">
		  {{ loading ? '生成中...' : '生成分镜' }}
		</button>
	  </view>
	  
	  <view class="result-section" v-if="result">
		<text class="section-title">生成结果：</text>
		<view class="result-content">
		  <text class="result-text">{{ formattedResult }}</text>
		</view>
	  </view>
	</view>
  </template>
  
  <script>
  import authManager from '../../utils/auth.js'
  
  export default {
	data() {
	  return {
		chapterNumber: '',
		chapterName: '',
		title: '',
		text: '',
		result: null,
		loading: false,
		selectedFile: null,
		projectId: null,
		pollingInterval: null,
		currentTextId: null,
		errors: {}
	  }
	},
	computed: {
	  formattedResult() {
		if (!this.result) return ''
		return JSON.stringify(this.result, null, 2)
	  }
	},
	onLoad(options) {
	  // 检查登录状态
	  if (!this.checkAuth()) {
		return;
	  }
	  
	  if (options.project_id) {
		this.projectId = options.project_id;
		console.log('项目ID:', this.projectId);
	  } else {
		// 如果没有project_id，跳转到项目列表页
		uni.showToast({
		  title: '请先选择项目',
		  icon: 'none'
		});
		setTimeout(() => {
		  uni.navigateTo({
			url: '/pages/projects/list'
		  });
		}, 1500);
	  }
	},
	onUnload() {
	  // 页面卸载时清除定时器
	  if (this.pollingInterval) {
		clearInterval(this.pollingInterval);
		this.pollingInterval = null;
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
	  
	  goBack() {
		uni.navigateBack()
	  },
	  
	  // 选择文件
	  chooseFile() {
		uni.chooseFile({
		  count: 1,
		  type: 'file',
		  extension: ['txt', 'doc', 'docx'],
		  success: (res) => {
			this.selectedFile = res.tempFiles[0]
			this.readFileContent(res.tempFiles[0])
		  },
		  fail: (err) => {
			uni.showToast({
			  title: '文件选择失败',
			  icon: 'none'
			})
		  }
		})
	  },
	  
	  // 读取文件内容
	  readFileContent(file) {
		const reader = new FileReader()
		reader.onload = (e) => {
		  this.text = e.target.result
		  uni.showToast({
			title: '文件读取成功',
			icon: 'success'
		  })
		}
		reader.onerror = () => {
		  uni.showToast({
			title: '文件读取失败',
			icon: 'none'
		  })
		}
		reader.readAsText(file)
	  },
	  
	  async submitText() {
		// 清空错误信息
		this.errors = {};
		
		// 验证必填字段
		if (!this.chapterNumber) {
		  this.errors.chapterNumber = '请输入章节编号';
		  uni.showToast({
			title: '请输入章节编号',
			icon: 'none'
		  });
		  return;
		}
		
		if (!this.chapterName.trim()) {
		  this.errors.chapterName = '请输入章节名称';
		  uni.showToast({
			title: '请输入章节名称',
			icon: 'none'
		  });
		  return;
		}
		
		// 验证文本
		if (!this.text.trim()) {
		  uni.showToast({
			title: '请输入小说文本或上传文件',
			icon: 'none'
		  })
		  return
		}
		
		if (this.text.length < 100) {
		  uni.showToast({
			title: '文本太短，请输入至少100字',
			icon: 'none'
		  })
		  return
		}
		
		this.loading = true;
		this.result = null; // 清除旧结果显示
		this.currentTextId = null; // 清除旧 ID
		if (this.pollingInterval) clearInterval(this.pollingInterval); // 清除旧轮询

		try {
		  const response = await uni.request({
			url: 'http://localhost:8000/api/v1/parse',
			method: 'POST',
			header: { 'Content-Type': 'application/json' },
			data: {
			  title: this.chapterName, // 使用章节名称作为标题
			  text: this.text,
			  project_id: this.projectId,
			  chapter_number: parseInt(this.chapterNumber),
			  chapter_name: this.chapterName
			}
		  });

		  if (response.statusCode === 200 && response.data.ok) {
			uni.showToast({ title: '已提交后台处理...', icon: 'loading', duration: 2000 });
			this.currentTextId = response.data.text_id;
			this.startPollingStatus(response.data.text_id, response.data.project_id); // 开始轮询
		  } else {
			throw new Error(response.data.detail || `HTTP ${response.statusCode}`);
		  }
		} catch (error) {
		  console.error('Submit failed:', error);
		  uni.showToast({ title: '提交失败：' + error.message, icon: 'none' });
		  this.loading = false; // 出错时停止 loading
		} 
		// 注意：finally 不再设置 loading = false，由轮询结束时设置
	  },

	  startPollingStatus(textId, projectId) {
		this.loading = true; // 保持 loading 状态
		this.pollingInterval = setInterval(async () => {
		  try {
			const statusRes = await uni.request({
			  url: `http://localhost:8000/api/v1/source_text_status/${textId}`,
			  method: 'GET'
			});

			if (statusRes.statusCode === 200 && statusRes.data.ok) {
			  const status = statusRes.data.status;
			  if (status === 'completed') {
				clearInterval(this.pollingInterval);
				this.pollingInterval = null;
				this.loading = false;
				uni.showToast({ title: '处理完成！', icon: 'success' });
				// 跳转
				uni.navigateTo({
				  url: `/pages/storyboard/layout-planner?project_id=${projectId}&text_id=${textId}`
				});
			  } else if (status === 'failed') {
				clearInterval(this.pollingInterval);
				this.pollingInterval = null;
				this.loading = false;
				uni.showModal({
					title: '处理失败',
					content: statusRes.data.error || '未知错误',
					showCancel: false
				});
			  } else {
				// 'pending' 或 'processing'，继续轮询
				console.log(`Polling status: ${status}`);
			  }
			} else {
			  // 查询状态接口本身出错
			   throw new Error('无法获取状态');
			}
		  } catch (pollError) {
			clearInterval(this.pollingInterval);
			this.pollingInterval = null;
			this.loading = false;
			uni.showToast({ title: '查询状态失败: ' + pollError.message, icon: 'none' });
		  }
		}, 3000); // 每 3 秒轮询一次
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
	align-items: center;
	justify-content: space-between;
	margin-bottom: 40rpx;
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
  
  .form-section {
	background-color: white;
	padding: 30rpx;
	border-radius: 20rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
  }
  
  .input-group {
	margin-bottom: 30rpx;
  }
  
  .label {
	display: block;
	font-size: 32rpx;
	color: #666;
	margin-bottom: 10rpx;
  }
  
  .required {
	color: #ff4757;
  }
  
  .input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #ddd;
	border-radius: 10rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	box-sizing: border-box;
  }
  
  .input.error {
	border-color: #ff4757;
  }
  
  .error-text {
	font-size: 24rpx;
	color: #ff4757;
	display: block;
	margin-top: 10rpx;
  }
  
  .textarea {
	width: 100%;
	min-height: 400rpx;
	border: 2rpx solid #ddd;
	border-radius: 10rpx;
	padding: 20rpx;
	font-size: 28rpx;
	box-sizing: border-box;
	resize: vertical;
  }
  
  .char-count {
	font-size: 24rpx;
	color: #999;
	text-align: right;
	display: block;
	margin-top: 10rpx;
  }
  
  .upload-section {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
  }
  
  .upload-btn {
	width: 100%;
	height: 80rpx;
	background-color: #f0f0f0;
	color: #333;
	border: 2rpx dashed #ccc;
	border-radius: 10rpx;
	font-size: 28rpx;
	display: flex;
	align-items: center;
	justify-content: center;
  }
  
  .file-info {
	font-size: 24rpx;
	color: #666;
	text-align: center;
  }
  
  .submit-btn {
	width: 100%;
	height: 80rpx;
	background-color: #007aff;
	color: white;
	border: none;
	border-radius: 10rpx;
	font-size: 32rpx;
	font-weight: bold;
  }
  
  .submit-btn:disabled {
	background-color: #ccc;
  }
  
  .result-section {
	background-color: white;
	padding: 30rpx;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
  }
  
  .section-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 20rpx;
	display: block;
  }
  
  .result-content {
	background-color: #f8f8f8;
	padding: 20rpx;
	border-radius: 10rpx;
	border: 1rpx solid #eee;
  }
  
  .result-text {
	font-size: 24rpx;
	color: #333;
	font-family: 'Courier New', monospace;
	white-space: pre-wrap;
	word-break: break-all;
  }
  </style>
  