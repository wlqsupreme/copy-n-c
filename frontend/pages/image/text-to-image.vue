<template>
  <view class="container">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-left">
        <button class="back-btn" @click="goBack">←</button>
        <text class="page-title">🎨 文生图工具</text>
      </view>
    </view>

    <!-- 主要内容区域 -->
    <view class="main-content">
      <view class="subtitle">测试文字生成图片功能 - 七牛云AI大模型</view>

      <!-- 标签页 -->
      <view class="tabs">
        <button 
          class="tab" 
          :class="{ active: currentTab === 'single' }" 
          @click="switchTab('single')"
        >单张生成</button>
        <button 
          class="tab" 
          :class="{ active: currentTab === 'multiple' }" 
          @click="switchTab('multiple')"
        >多张生成</button>
        <button 
          class="tab" 
          :class="{ active: currentTab === 'storyboard' }" 
          @click="switchTab('storyboard')"
        >分镜配图</button>
        <button 
          class="tab" 
          :class="{ active: currentTab === 'database' }" 
          @click="switchTab('database')"
        >数据库分镜</button>
        <button 
          class="tab" 
          :class="{ active: currentTab === 'examples' }" 
          @click="switchTab('examples')"
        >提示词示例</button>
      </view>

      <!-- 单张生成 -->
      <view v-if="currentTab === 'single'" class="tab-content">
        <view class="info-box">
          <text class="info-title">单张图片生成</text>
          <text class="info-desc">输入详细的文字描述，AI将生成一张符合描述的图片。生成时间约10-30秒。</text>
        </view>

        <view class="form-group">
          <text class="form-label">图片描述（提示词）*</text>
          <textarea 
            class="form-textarea" 
            v-model="singleForm.prompt"
            placeholder="请输入详细的图片描述，例如：一只可爱的橘猫坐在窗台上，阳光洒在它身上，温暖的画面，高质量插图"
          ></textarea>
        </view>

        <view class="example-prompts">
          <text class="example-label">快速选择：</text>
          <text class="example-prompt" @click="setPrompt('single', '一位优雅的女性站在樱花树下，和服飘逸，春风拂面，唯美画风')">樱花和服</text>
          <text class="example-prompt" @click="setPrompt('single', '未来城市天际线，霓虹灯闪烁，飞行汽车穿梭，雨夜，赛博朋克')">赛博朋克</text>
          <text class="example-prompt" @click="setPrompt('single', '宁静的海边小屋，日落时分，温暖的色调，浪漫氛围')">海边日落</text>
        </view>

        <view class="form-group">
          <text class="form-label">图片尺寸</text>
          <picker mode="selector" :range="sizeOptions" range-key="label" @change="onSizeChange('single', $event)">
            <view class="form-picker">{{ sizeOptions[singleForm.sizeIndex].label }}</view>
          </picker>
        </view>

        <view class="form-group">
          <text class="form-label">图片风格</text>
          <picker mode="selector" :range="styleOptions" range-key="label" @change="onStyleChange('single', $event)">
            <view class="form-picker">{{ styleOptions[singleForm.styleIndex].label }}</view>
          </picker>
        </view>

        <view class="form-group">
          <text class="form-label">图片质量</text>
          <picker mode="selector" :range="qualityOptions" range-key="label" @change="onQualityChange($event)">
            <view class="form-picker">{{ qualityOptions[singleForm.qualityIndex].label }}</view>
          </picker>
        </view>

        <button class="submit-btn" @click="generateSingle" :disabled="isLoading">
          {{ isLoading ? '生成中...' : '🎨 生成图片' }}
        </button>

        <!-- 加载状态 -->
        <view class="loading" v-if="isLoading">
          <view class="spinner"></view>
          <text class="loading-text">正在生成图片，请稍候（约10-30秒）...</text>
        </view>

        <!-- 结果展示 -->
        <view class="result" v-if="singleResult">
          <view class="result-header">
            <text class="result-title">{{ singleResult.success ? '✅ 生成成功' : '❌ 生成失败' }}</text>
          </view>
          <view v-if="singleResult.success" class="image-grid">
            <view class="image-item">
              <image :src="singleResult.image.url" mode="aspectFit" class="result-image"></image>
              <view class="image-info">
                <text class="info-item"><text class="info-label">原始提示词：</text>{{ singleResult.prompt }}</text>
                <text class="info-item" v-if="singleResult.image.revised_prompt">
                  <text class="info-label">优化后：</text>{{ singleResult.image.revised_prompt }}
                </text>
              </view>
            </view>
          </view>
          <text v-else class="error-text">{{ singleResult.error }}</text>
        </view>
      </view>

      <!-- 多张生成 -->
      <view v-if="currentTab === 'multiple'" class="tab-content">
        <view class="info-box">
          <text class="info-title">多张图片生成</text>
          <text class="info-desc">使用相同的描述生成多张图片，提供多个选择供您挑选。生成时间约20-60秒。</text>
        </view>

        <view class="form-group">
          <text class="form-label">图片描述（提示词）*</text>
          <textarea 
            class="form-textarea" 
            v-model="multipleForm.prompt"
            placeholder="请输入图片描述"
          ></textarea>
        </view>

        <view class="form-group">
          <text class="form-label">生成数量（1-10）</text>
          <input 
            class="form-input" 
            type="number" 
            v-model.number="multipleForm.count" 
            :min="1" 
            :max="10"
          />
        </view>

        <view class="form-group">
          <text class="form-label">图片尺寸</text>
          <picker mode="selector" :range="sizeOptionsMultiple" range-key="label" @change="onSizeChange('multiple', $event)">
            <view class="form-picker">{{ sizeOptionsMultiple[multipleForm.sizeIndex].label }}</view>
          </picker>
        </view>

        <button class="submit-btn" @click="generateMultiple" :disabled="isLoading">
          {{ isLoading ? '生成中...' : '🎨 批量生成' }}
        </button>

        <!-- 加载状态 -->
        <view class="loading" v-if="isLoading">
          <view class="spinner"></view>
          <text class="loading-text">正在批量生成图片，请稍候（约20-60秒）...</text>
        </view>

        <!-- 结果展示 -->
        <view class="result" v-if="multipleResult">
          <view class="result-header">
            <text class="result-title">{{ multipleResult.success ? `✅ 成功生成 ${multipleResult.count} 张图片` : '❌ 生成失败' }}</text>
          </view>
          <view v-if="multipleResult.success" class="image-grid">
            <view class="image-item" v-for="(img, index) in multipleResult.images" :key="index">
              <image :src="img.url" mode="aspectFit" class="result-image"></image>
              <view class="image-info">
                <text class="info-item">图片 {{ index + 1 }}</text>
              </view>
            </view>
          </view>
          <text v-else class="error-text">{{ multipleResult.error }}</text>
        </view>
      </view>

      <!-- 分镜配图 -->
      <view v-if="currentTab === 'storyboard'" class="tab-content">
        <view class="info-box">
          <text class="info-title">分镜配图生成</text>
          <text class="info-desc">为漫画分镜或故事板的多个场景生成配图。每个场景一张图片。</text>
        </view>

        <view class="form-group">
          <text class="form-label">场景描述列表（每行一个场景）</text>
          <textarea 
            class="form-textarea large" 
            v-model="storyboardForm.scenes"
            placeholder="第1个场景描述&#10;第2个场景描述&#10;第3个场景描述"
          ></textarea>
        </view>

        <view class="form-group">
          <text class="form-label">图片尺寸</text>
          <picker mode="selector" :range="sizeOptionsStoryboard" range-key="label" @change="onSizeChange('storyboard', $event)">
            <view class="form-picker">{{ sizeOptionsStoryboard[storyboardForm.sizeIndex].label }}</view>
          </picker>
        </view>

        <button class="submit-btn" @click="generateStoryboard" :disabled="isLoading">
          {{ isLoading ? '生成中...' : '🎬 生成分镜配图' }}
        </button>

        <!-- 加载状态 -->
        <view class="loading" v-if="isLoading">
          <view class="spinner"></view>
          <text class="loading-text">正在生成分镜配图，请稍候...</text>
        </view>

        <!-- 结果展示 -->
        <view class="result" v-if="storyboardResult">
          <view class="result-header">
            <text class="result-title">{{ storyboardResult.success ? `✅ 分镜配图完成（${storyboardResult.success_count}/${storyboardResult.total}）` : '❌ 生成失败' }}</text>
          </view>
          <view v-if="storyboardResult.success" class="image-grid">
            <view class="image-item" v-for="(scene, index) in storyboardResult.storyboard" :key="index">
              <image v-if="scene.url" :src="scene.url" mode="aspectFit" class="result-image"></image>
              <view v-else class="image-placeholder">生成失败</view>
              <view class="image-info">
                <text class="info-item"><text class="info-label">场景 {{ scene.index }}：</text>{{ scene.description }}</text>
              </view>
            </view>
          </view>
          <text v-else class="error-text">{{ storyboardResult.error }}</text>
        </view>
      </view>

      <!-- 数据库分镜 -->
      <view v-if="currentTab === 'database'" class="tab-content">
        <view class="info-box">
          <text class="info-title">数据库分镜生成</text>
          <text class="info-desc">从数据库中加载已有的分镜数据，为每个分镜生成配图（含对话框）。</text>
        </view>

        <button class="submit-btn" @click="loadDatabaseStoryboards(1)" :disabled="isLoading">
          {{ isLoading ? '加载中...' : '📚 加载数据库分镜列表' }}
        </button>

        <!-- 分页控制 -->
        <view v-if="databaseStoryboards.length > 0" class="pagination">
          <button class="pagination-btn" @click="loadPreviousPage" :disabled="currentPage <= 1">
            ⬅️ 上一页
          </button>
          <text class="page-info">第 {{ currentPage }} 页</text>
          <button class="pagination-btn" @click="loadNextPage" :disabled="currentPage >= totalPages">
            下一页 ➡️
          </button>
          <text class="total-info">（共 {{ totalCount }} 条，每页10条）</text>
        </view>

        <!-- 分镜列表 -->
        <view v-if="databaseStoryboards.length > 0" class="storyboard-list">
          <view class="storyboard-item" v-for="(item, index) in databaseStoryboards" :key="item.storyboard_id">
            <view class="storyboard-header">
              <text class="storyboard-title">分镜 #{{ getGlobalIndex(index) }}</text>
              <text class="storyboard-id">ID: {{ item.storyboard_id ? item.storyboard_id.substring(0, 8) + '...' : '-' }}</text>
            </view>
            
            <view class="storyboard-field">
              <text class="field-label">原文片段:</text>
              <text class="field-value">{{ truncate(item.original_text_snippet || '-', 50) }}</text>
            </view>
            
            <view class="storyboard-field">
              <text class="field-label">角色外观:</text>
              <text class="field-value">{{ item.character_appearance || '-' }}</text>
            </view>
            
            <view class="storyboard-field">
              <text class="field-label">场景光线:</text>
              <text class="field-value">{{ item.scene_and_lighting || '-' }}</text>
            </view>
            
            <view class="storyboard-field">
              <text class="field-label">镜头构图:</text>
              <text class="field-value">{{ item.camera_and_composition || '-' }}</text>
            </view>
            
            <view class="storyboard-field">
              <text class="field-label">表情动作:</text>
              <text class="field-value">{{ item.expression_and_action || '-' }}</text>
            </view>

            <view class="storyboard-field">
              <text class="field-label">风格要求:</text>
              <text class="field-value">{{ item.style_requirements || '-' }}</text>
            </view>
            
            <!-- 对话内容预览 -->
            <view v-if="item.hasDialogue" class="dialogue-preview">
              <text class="dialogue-label">💬 对话内容:</text>
              <text class="dialogue-text">{{ item.dialoguePreview }}</text>
              <text class="dialogue-tip">⚡ 将自动添加对话框！</text>
            </view>
            <view v-else class="storyboard-field">
              <text class="field-label">对话:</text>
              <text class="field-value">无</text>
            </view>
            
            <button class="generate-btn-small" @click="generateFromDatabase(item.storyboard_id)" :disabled="isLoading">
              {{ isLoading ? '生成中...' : '🎨 生成完整漫画' + (item.hasDialogue ? '（含对话框）' : '') }}
            </button>
          </view>
        </view>

        <!-- 生成结果 -->
        <view class="result" v-if="databaseResult">
          <view class="result-header">
            <text class="result-title">{{ databaseResult.success ? '✅ ' + databaseResult.message : '❌ 生成失败' }}</text>
          </view>
          
          <view v-if="databaseResult.success">
            <!-- 生成流程 -->
            <view class="info-box" style="background: #fff3cd; border-left-color: #ffc107;">
              <text class="info-title" style="color: #856404;">🎨 生成流程：</text>
              <view class="process-list">
                <text class="process-item">1. AI生成纯画面（不含文字）✅</text>
                <text class="process-item">2. {{ databaseResult.has_dialogue ? '自动添加对话框 ✅' : '无对话内容，跳过 ⚪' }}</text>
                <text class="process-item">3. 返回完整漫画 ✅</text>
              </view>
            </view>

            <!-- 对话内容 -->
            <view v-if="databaseResult.has_dialogue && databaseResult.dialogues" class="info-box" style="background: #e8f5e9; border-left-color: #4CAF50;">
              <text class="info-title" style="color: #2e7d32;">💬 对话内容（{{ databaseResult.dialogue_count }} 条）：</text>
              <view class="dialogue-list">
                <view class="dialogue-item" v-for="(d, idx) in databaseResult.dialogues" :key="idx">
                  <text class="dialogue-speaker">{{ d.speaker || '旁白' }}：</text>
                  <text class="dialogue-content">{{ d.text }}</text>
                </view>
              </view>
            </view>

            <!-- 生成的图片 -->
            <view class="image-container">
              <text class="image-title">📸 最终效果：</text>
              <image :src="databaseResult.image.url" mode="aspectFit" class="result-image"></image>
              <text v-if="databaseResult.has_dialogue" class="success-tip">✨ 对话框已自动添加！文字清晰无乱码！</text>
            </view>
          </view>
          
          <text v-else class="error-text">{{ databaseResult.error }}</text>
        </view>
      </view>

      <!-- 提示词示例 -->
      <view v-if="currentTab === 'examples'" class="tab-content">
        <view class="info-box">
          <text class="info-title">优质提示词示例</text>
          <text class="info-desc">参考这些示例，学习如何编写高质量的提示词。点击示例可以快速应用。</text>
        </view>

        <view v-if="examplesData" class="examples-content">
          <view v-for="(examples, category) in examplesData.examples" :key="category" class="example-category">
            <text class="category-title">{{ category }}</text>
            <view class="example-prompts">
              <text 
                class="example-prompt" 
                v-for="(example, index) in examples" 
                :key="index"
                @click="setPrompt('single', example)"
              >
                {{ example.substring(0, 30) }}...
              </text>
            </view>
          </view>

          <view class="tips-box">
            <text class="tips-title">💡 编写提示词的技巧</text>
            <view class="tips-list">
              <text class="tip-item" v-for="(tip, index) in examplesData.tips" :key="index">• {{ tip }}</text>
            </view>
          </view>
        </view>
        <text v-else class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'single',
      isLoading: false,
      
      // 单张生成表单
      singleForm: {
        prompt: '一只可爱的橘猫坐在窗台上，阳光洒在它身上，温暖的画面，高质量插图',
        sizeIndex: 0,
        qualityIndex: 0,
        styleIndex: 0
      },
      
      // 多张生成表单
      multipleForm: {
        prompt: '科幻城市夜景，霓虹灯闪烁，未来感十足，赛博朋克风格',
        count: 4,
        sizeIndex: 0
      },
      
      // 分镜配图表单
      storyboardForm: {
        scenes: '清晨的城市街道，阳光透过高楼大厦\n主角走进温馨的咖啡店，暖黄色灯光\n咖啡店内，两人坐在窗边对话',
        sizeIndex: 0
      },
      
      // 选项
      sizeOptions: [
        { label: '1024x1024（正方形，推荐）', value: '1024x1024' },
        { label: '1792x1024（横向宽屏）', value: '1792x1024' },
        { label: '1024x1792（竖向）', value: '1024x1792' }
      ],
      
      sizeOptionsMultiple: [
        { label: '1024x1024（正方形，推荐）', value: '1024x1024' },
        { label: '1792x1024（横向宽屏）', value: '1792x1024' },
        { label: '1024x1792（竖向）', value: '1024x1792' }
      ],
      
      sizeOptionsStoryboard: [
        { label: '1024x1024（推荐）', value: '1024x1024' },
        { label: '1792x1024（横向）', value: '1792x1024' },
        { label: '1024x1792（竖向）', value: '1024x1792' }
      ],
      
      styleOptions: [
        { label: '生动（vivid）- 鲜艳、富有想象力', value: 'vivid' },
        { label: '自然（natural）- 真实、写实风格', value: 'natural' }
      ],
      
      qualityOptions: [
        { label: '标准（standard）- 较快', value: 'standard' },
        { label: '高清（hd）- 更精细但较慢', value: 'hd' }
      ],
      
      // 结果
      singleResult: null,
      multipleResult: null,
      storyboardResult: null,
      examplesData: null,
      
      // 数据库分镜相关
      databaseStoryboards: [],
      currentPage: 1,
      pageSize: 10,
      totalCount: 0,
      databaseResult: null
    }
  },
  
  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize)
    }
  },
  
  methods: {
    goBack() {
      uni.navigateBack()
    },
    
    switchTab(tab) {
      this.currentTab = tab
      if (tab === 'examples' && !this.examplesData) {
        this.loadExamples()
      }
      // 切换到数据库分镜tab时，如果还没有加载数据，则自动加载第一页
      if (tab === 'database' && this.databaseStoryboards.length === 0) {
        this.loadDatabaseStoryboards(1)
      }
    },
    
    setPrompt(type, text) {
      if (type === 'single') {
        this.singleForm.prompt = text
        this.currentTab = 'single'
      } else if (type === 'multiple') {
        this.multipleForm.prompt = text
      }
    },
    
    onSizeChange(type, e) {
      const index = e.detail.value
      if (type === 'single') {
        this.singleForm.sizeIndex = index
      } else if (type === 'multiple') {
        this.multipleForm.sizeIndex = index
      } else if (type === 'storyboard') {
        this.storyboardForm.sizeIndex = index
      }
    },
    
    onStyleChange(type, e) {
      const index = e.detail.value
      if (type === 'single') {
        this.singleForm.styleIndex = index
      }
    },
    
    onQualityChange(e) {
      this.singleForm.qualityIndex = e.detail.value
    },
    
    async generateSingle() {
      if (!this.singleForm.prompt.trim()) {
        uni.showToast({
          title: '请输入图片描述',
          icon: 'none'
        })
        return
      }
      
      this.isLoading = true
      this.singleResult = null
      
      try {
        const response = await uni.request({
          url: 'http://localhost:8000/api/v1/text-to-image/generate',
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            prompt: this.singleForm.prompt,
            size: this.sizeOptions[this.singleForm.sizeIndex].value,
            quality: this.qualityOptions[this.singleForm.qualityIndex].value,
            style: this.styleOptions[this.singleForm.styleIndex].value
          }
        })
        
        if (response.statusCode === 200 && response.data.ok && response.data.image) {
          this.singleResult = {
            success: true,
            prompt: this.singleForm.prompt,
            image: response.data.image
          }
          uni.showToast({
            title: '生成成功',
            icon: 'success'
          })
        } else {
          throw new Error(response.data.detail || '生成失败')
        }
      } catch (error) {
        this.singleResult = {
          success: false,
          error: error.message || '请求失败'
        }
        uni.showToast({
          title: '生成失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
      }
    },
    
    async generateMultiple() {
      if (!this.multipleForm.prompt.trim()) {
        uni.showToast({
          title: '请输入图片描述',
          icon: 'none'
        })
        return
      }
      
      if (this.multipleForm.count < 1 || this.multipleForm.count > 10) {
        uni.showToast({
          title: '生成数量必须在1-10之间',
          icon: 'none'
        })
        return
      }
      
      this.isLoading = true
      this.multipleResult = null
      
      try {
        const response = await uni.request({
          url: 'http://localhost:8000/api/v1/text-to-image/generate-multiple',
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            prompt: this.multipleForm.prompt,
            n: this.multipleForm.count,
            size: this.sizeOptionsMultiple[this.multipleForm.sizeIndex].value,
            quality: 'standard',
            style: 'vivid'
          }
        })
        
        if (response.statusCode === 200 && response.data.ok && response.data.images) {
          this.multipleResult = {
            success: true,
            count: response.data.count,
            images: response.data.images
          }
          uni.showToast({
            title: '生成成功',
            icon: 'success'
          })
        } else {
          throw new Error(response.data.detail || '生成失败')
        }
      } catch (error) {
        this.multipleResult = {
          success: false,
          error: error.message || '请求失败'
        }
        uni.showToast({
          title: '生成失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
      }
    },
    
    async generateStoryboard() {
      if (!this.storyboardForm.scenes.trim()) {
        uni.showToast({
          title: '请输入场景描述',
          icon: 'none'
        })
        return
      }
      
      const sceneLines = this.storyboardForm.scenes.split('\n').filter(line => line.trim())
      const scenes = sceneLines.map((line, i) => ({
        index: i + 1,
        description: line.trim()
      }))
      
      this.isLoading = true
      this.storyboardResult = null
      
      try {
        const response = await uni.request({
          url: 'http://localhost:8000/api/v1/text-to-image/storyboard',
          method: 'POST',
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            scenes: scenes,
            size: this.sizeOptionsStoryboard[this.storyboardForm.sizeIndex].value,
            style: 'vivid'
          }
        })
        
        if (response.statusCode === 200 && response.data.ok && response.data.storyboard) {
          this.storyboardResult = {
            success: true,
            success_count: response.data.success_count,
            total: response.data.total,
            storyboard: response.data.storyboard
          }
          uni.showToast({
            title: '生成成功',
            icon: 'success'
          })
        } else {
          throw new Error(response.data.detail || '生成失败')
        }
      } catch (error) {
        this.storyboardResult = {
          success: false,
          error: error.message || '请求失败'
        }
        uni.showToast({
          title: '生成失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
      }
    },
    
    async loadExamples() {
      try {
        const response = await uni.request({
          url: 'http://localhost:8000/api/v1/text-to-image/examples',
          method: 'GET'
        })
        
        if (response.statusCode === 200 && response.data.ok) {
          this.examplesData = response.data
        }
      } catch (error) {
        console.error('加载示例失败:', error)
      }
    },
    
    // 数据库分镜相关方法
    async loadDatabaseStoryboards(page = 1) {
      this.isLoading = true
      this.databaseStoryboards = []
      this.databaseResult = null
      this.currentPage = page
      
      const offset = (page - 1) * this.pageSize
      
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/storyboard-gen/list-storyboards?limit=${this.pageSize}&offset=${offset}`,
          method: 'GET'
        })
        
        if (response.statusCode === 200 && response.data.ok) {
          this.totalCount = response.data.count
          
          // 处理分镜数据，解析对话内容
          this.databaseStoryboards = response.data.storyboards.map(item => {
            let hasDialogue = false
            let dialoguePreview = '无'
            
            try {
              if (item.panel_elements) {
                const panelElements = typeof item.panel_elements === 'string' 
                  ? JSON.parse(item.panel_elements) 
                  : item.panel_elements
                
                if (Array.isArray(panelElements) && panelElements.length > 0) {
                  const dialogueItems = panelElements.filter(el => el.dialogue && el.dialogue.trim())
                  if (dialogueItems.length > 0) {
                    hasDialogue = true
                    dialoguePreview = dialogueItems.map(el => 
                      `${el.character_id || el.characterid ? '[角色] ' : ''}${el.dialogue}`
                    ).join(' | ')
                  }
                }
              }
            } catch (e) {
              console.error('解析 panel_elements 失败:', e)
            }
            
            return {
              ...item,
              hasDialogue,
              dialoguePreview
            }
          })
          
          uni.showToast({
            title: `加载成功（第${page}页）`,
            icon: 'success'
          })
        } else {
          throw new Error(response.data.detail || '加载失败')
        }
      } catch (error) {
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
        console.error('加载数据库分镜失败:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    async generateFromDatabase(storyboardId) {
      this.isLoading = true
      this.databaseResult = null
      
      try {
        const response = await uni.request({
          url: `http://localhost:8000/api/v1/storyboard-gen/generate-from-db/${storyboardId}?size=1024x1024`,
          method: 'POST'
        })
        
        if (response.statusCode === 200 && response.data.ok) {
          this.databaseResult = {
            success: true,
            message: response.data.message,
            image: response.data.image,
            has_dialogue: response.data.has_dialogue,
            dialogue_count: response.data.dialogue_count,
            dialogues: response.data.dialogues
          }
          
          uni.showToast({
            title: '生成成功',
            icon: 'success'
          })
        } else {
          throw new Error(response.data.detail || '生成失败')
        }
      } catch (error) {
        this.databaseResult = {
          success: false,
          error: error.message || '请求失败'
        }
        
        uni.showToast({
          title: '生成失败',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
      }
    },
    
    loadPreviousPage() {
      if (this.currentPage > 1) {
        this.loadDatabaseStoryboards(this.currentPage - 1)
      }
    },
    
    loadNextPage() {
      if (this.currentPage < this.totalPages) {
        this.loadDatabaseStoryboards(this.currentPage + 1)
      }
    },
    
    getGlobalIndex(index) {
      return (this.currentPage - 1) * this.pageSize + index + 1
    },
    
    truncate(str, length) {
      if (!str) return '-'
      return str.length > length ? str.substring(0, length) + '...' : str
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

.tabs {
  display: flex;
  gap: 20rpx;
  margin-bottom: 40rpx;
  border-bottom: 2rpx solid #f0f0f0;
  flex-wrap: wrap;
}

.tab {
  padding: 20rpx 40rpx;
  background: transparent;
  border: none;
  font-size: 28rpx;
  color: #666;
  border-bottom: 6rpx solid transparent;
  transition: all 0.3s;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: bold;
}

.tab-content {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  margin-bottom: 15rpx;
}

.info-desc {
  color: #424242;
  font-size: 26rpx;
  line-height: 1.6;
  display: block;
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

.form-textarea {
  width: 100%;
  min-height: 200rpx;
  padding: 24rpx;
  border: 4rpx solid #e0e0e0;
  border-radius: 16rpx;
  font-size: 28rpx;
  resize: vertical;
  box-sizing: border-box;
}

.form-textarea.large {
  min-height: 300rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  border: 4rpx solid #e0e0e0;
  border-radius: 16rpx;
  font-size: 28rpx;
  box-sizing: border-box;
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

.example-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.example-label {
  font-weight: 600;
  font-size: 26rpx;
  color: #333;
  margin-right: 20rpx;
}

.example-prompt {
  background: #f0f0f0;
  padding: 16rpx 30rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  cursor: pointer;
  transition: all 0.3s;
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

.image-placeholder {
  width: 100%;
  height: 400rpx;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 28rpx;
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

.examples-content {
  margin-top: 20rpx;
}

.example-category {
  margin-bottom: 60rpx;
}

.category-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #667eea;
  display: block;
  margin-bottom: 30rpx;
}

.tips-box {
  background: #fff3cd;
  padding: 40rpx;
  border-radius: 16rpx;
  margin-top: 60rpx;
}

.tips-title {
  color: #856404;
  font-size: 32rpx;
  font-weight: bold;
  display: block;
  margin-bottom: 20rpx;
}

.tips-list {
  margin-left: 40rpx;
}

.tip-item {
  font-size: 26rpx;
  color: #856404;
  line-height: 2;
  display: block;
}

/* 数据库分镜相关样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20rpx;
  margin: 30rpx 0;
  padding: 30rpx;
  background: #f8f9fa;
  border-radius: 16rpx;
  flex-wrap: wrap;
}

.pagination-btn {
  padding: 16rpx 32rpx;
  font-size: 24rpx;
  min-width: 160rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12rpx;
}

.pagination-btn:disabled {
  background: #ccc;
  opacity: 0.5;
}

.page-info {
  margin: 0 30rpx;
  font-size: 28rpx;
  color: #666;
  font-weight: bold;
}

.total-info {
  margin-left: 40rpx;
  font-size: 24rpx;
  color: #999;
}

.storyboard-list {
  margin-top: 40rpx;
}

.storyboard-item {
  background: #f8f9fa;
  padding: 30rpx;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
  border-left: 8rpx solid #667eea;
}

.storyboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.storyboard-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #667eea;
}

.storyboard-id {
  font-size: 24rpx;
  color: #999;
}

.storyboard-field {
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

.dialogue-text {
  color: #856404;
  font-size: 24rpx;
  line-height: 1.6;
  display: block;
  margin-bottom: 10rpx;
}

.dialogue-tip {
  font-size: 22rpx;
  color: #856404;
  display: block;
}

.generate-btn-small {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 20rpx 40rpx;
  border-radius: 12rpx;
  font-size: 26rpx;
  margin-top: 20rpx;
  width: 100%;
}

.generate-btn-small:disabled {
  background: #ccc;
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

.dialogue-item {
  background: white;
  padding: 20rpx;
  border-radius: 8rpx;
  margin: 16rpx 0;
  border-left: 8rpx solid #4CAF50;
}

.dialogue-speaker {
  font-weight: bold;
  color: #2e7d32;
  font-size: 26rpx;
  margin-right: 10rpx;
}

.dialogue-content {
  color: #333;
  font-size: 26rpx;
}

.image-title {
  font-weight: bold;
  font-size: 32rpx;
  color: #667eea;
  display: block;
  margin-bottom: 20rpx;
}

.success-tip {
  text-align: center;
  color: #4CAF50;
  margin-top: 20rpx;
  font-weight: bold;
  font-size: 26rpx;
  display: block;
}

/* 响应式设计 */
@media (min-width: 750rpx) {
  .image-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

