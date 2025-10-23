<template>
	<view class="container">
	  <view class="header">
		<button class="back-btn" @click="goBack">← 返回</button>
		<text class="title">文本分析</text>
	  </view>
	  
	  <view class="form-section">
		<view class="input-group">
		  <text class="label">标题（可选）：</text>
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
  export default {
	data() {
	  return {
		title: '',
		text: '',
		result: null,
		loading: false,
		selectedFile: null
	  }
	},
	computed: {
	  formattedResult() {
		if (!this.result) return ''
		return JSON.stringify(this.result, null, 2)
	  }
	},
	methods: {
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
		
		this.loading = true
		this.result = null
		
		try {
		  const response = await uni.request({
			url: 'http://localhost:8000/api/v1/parse',
			method: 'POST',
			header: {
			  'Content-Type': 'application/json'
			},
			data: {
			  title: this.title,
			  text: this.text
			}
		  })
		  
		  if (response.statusCode === 200) {
			this.result = response.data
			if (response.data.ok) {
			  uni.showToast({
				title: '生成成功！',
				icon: 'success'
			  })
			  
			  // 跳转到分镜规划页面
			  setTimeout(() => {
				uni.navigateTo({
				  url: `/pages/storyboard/layout-planner?storyboard=${encodeURIComponent(JSON.stringify(response.data.storyboard))}`
				})
			  }, 1500)
			} else {
			  uni.showToast({
				title: '解析失败，请查看结果',
				icon: 'none'
			  })
			}
		  } else {
			throw new Error(`HTTP ${response.statusCode}`)
		  }
		} catch (error) {
		  console.error('Request failed:', error)
		  uni.showToast({
			title: '请求失败：' + error.message,
			icon: 'none'
		  })
		  this.result = { error: error.message }
		} finally {
		  this.loading = false
		}
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
  
  .input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #ddd;
	border-radius: 10rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	box-sizing: border-box;
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
  