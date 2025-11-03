<template>
  <view class="result-container">
    <!-- 顶部状态栏 -->
    <view class="status-bar">
      <text class="status-title">识别结果</text>
      <text class="confidence" v-if="confidence > 0">置信度: {{ confidence }}%</text>
    </view>
    
    <!-- 药品信息卡片 -->
    <view class="drug-card" v-if="drugInfo && drugInfo.drug_name">
      <view class="card-header">
        <text class="drug-name">{{ drugInfo.drug_name }}</text>
        <view class="status-badge success" v-if="resultData && resultData.success">
          <text>识别成功</text>
        </view>
      </view>
      
      <view class="drug-details">
        <view class="detail-item" v-if="drugInfo.dosage">
          <view class="item-header">
            <text class="icon">💊</text>
            <text class="label">用法用量</text>
          </view>
          <text class="value">{{ drugInfo.dosage }}</text>
        </view>
        
        <view class="detail-item" v-if="drugInfo.usage">
          <view class="item-header">
            <text class="icon">📝</text>
            <text class="label">使用方法</text>
          </view>
          <text class="value">{{ drugInfo.usage }}</text>
        </view>
        
        <view class="detail-item" v-if="drugInfo.expiry_date">
          <view class="item-header">
            <text class="icon">📅</text>
            <text class="label">有效期</text>
          </view>
          <text class="value">{{ drugInfo.expiry_date }}</text>
        </view>
        
        <view class="detail-item" v-if="drugInfo.manufacturer">
          <view class="item-header">
            <text class="icon">🏭</text>
            <text class="label">生产厂家</text>
          </view>
          <text class="value">{{ drugInfo.manufacturer }}</text>
        </view>
        
        <view class="detail-item" v-if="drugInfo.batch_number">
          <view class="item-header">
            <text class="icon">🔢</text>
            <text class="label">产品批号</text>
          </view>
          <text class="value">{{ drugInfo.batch_number }}</text>
        </view>
        
        <view class="detail-item" v-if="drugInfo.storage">
          <view class="item-header">
            <text class="icon">🌡️</text>
            <text class="label">贮藏方式</text>
          </view>
          <text class="value">{{ drugInfo.storage }}</text>
        </view>
      </view>
    </view>
    
    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">🔍</text>
      <text class="empty-text">未识别到药品信息</text>
      <text class="empty-desc">请重新拍摄清晰的药品标签</text>
    </view>
    
    <!-- 语音播报区域 -->
    <view class="voice-section" v-if="voiceGuidance">
      <view class="section-header">
        <text class="section-title">语音播报</text>
        <text class="section-desc">为视障用户提供语音指导</text>
      </view>
      <text class="voice-text">{{ voiceGuidance }}</text>
    </view>
    
    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="action-btn primary" @click="readAloud" v-if="voiceGuidance">
        <text class="btn-icon">🔊</text>
        <text class="btn-text">语音播报</text>
      </button>
      
      <button class="action-btn secondary" @click="saveResult" v-if="drugInfo && drugInfo.drug_name">
        <text class="btn-icon">💾</text>
        <text class="btn-text">保存记录</text>
      </button>
      
      <button class="action-btn secondary" @click="retakePhoto">
        <text class="btn-icon">📷</text>
        <text class="btn-text">重新拍照</text>
      </button>
    </view>
    
    <!-- 调试信息（开发时使用） -->
    <view class="debug-info" v-if="showDebug && resultData">
      <text class="debug-title">调试信息</text>
      <text class="debug-content">{{ JSON.stringify(resultData, null, 2) }}</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      resultData: null,        // 完整的识别结果数据
      drugInfo: null,          // 药品信息
      confidence: 0,           // 识别置信度
      voiceGuidance: '',       // 语音播报文本
      showDebug: false,        // 是否显示调试信息
      rawText: ''              // 原始文本（如果需要的话）
    }
  },
  
  onLoad(options) {
    console.log('结果页面参数:', options)
    
    if (options.data) {
      try {
        // 解析传递过来的数据
        const resultData = JSON.parse(decodeURIComponent(options.data))
        console.log('识别结果数据:', resultData)
        
        // 设置数据
        this.resultData = resultData
        this.drugInfo = resultData.drug_info || {}
        this.confidence = resultData.ocr_confidence || 0
        this.voiceGuidance = resultData.voice_guidance || ''
        
        // 提取原始文本（如果需要）
        this.rawText = this.extractRawText(this.drugInfo)
        
        console.log('解析后的药品信息:', this.drugInfo)
        console.log('语音播报文本:', this.voiceGuidance)
        
        // 自动语音播报（可选）
        setTimeout(() => {
          this.readAloud()
        }, 1000)
        
      } catch (error) {
        console.error('解析结果数据失败:', error)
        uni.showToast({
          title: '数据解析失败',
          icon: 'error',
          duration: 2000
        })
      }
    } else {
      console.warn('没有接收到数据')
      uni.showToast({
        title: '未接收到识别数据',
        icon: 'error',
        duration: 2000
      })
    }
  },
  
  methods: {
    // 提取原始文本
    extractRawText(drugInfo) {
      if (!drugInfo) return ''
      
      const parts = []
      if (drugInfo.drug_name) parts.push(`药品名称：${drugInfo.drug_name}`)
      if (drugInfo.dosage) parts.push(`用法用量：${drugInfo.dosage}`)
      if (drugInfo.usage) parts.push(`使用方法：${drugInfo.usage}`)
      if (drugInfo.expiry_date) parts.push(`有效期：${drugInfo.expiry_date}`)
      if (drugInfo.manufacturer) parts.push(`生产厂家：${drugInfo.manufacturer}`)
      if (drugInfo.batch_number) parts.push(`批号：${drugInfo.batch_number}`)
      if (drugInfo.storage) parts.push(`贮藏：${drugInfo.storage}`)
      
      return parts.join('；')
    },
    
    // 语音播报
    readAloud() {
      if (!this.voiceGuidance) {
        // 如果没有语音指导文本，就从药品信息生成
        this.voiceGuidance = this.generateVoiceGuidance()
      }
      
      console.log('语音播报内容:', this.voiceGuidance)
      
      // 使用微信小程序的语音合成（如果可用）
      if (typeof wx !== 'undefined' && wx.createInnerAudioContext) {
        // 这里可以集成真实的TTS服务
        // 目前使用震动和文字提示模拟
        uni.vibrateLong({
          success: () => {
            console.log('震动反馈 - 模拟语音播报')
          }
        })
      }
      
      // 显示文字提示
      uni.showToast({
        title: '语音播报中...',
        icon: 'none',
        duration: 3000
      })
      
      // 为视障用户朗读（通过屏幕阅读器）
      // 在实际应用中，这里应该调用TTS API
      console.log('语音内容:', this.voiceGuidance)
    },
    
    // 生成语音指导文本
    generateVoiceGuidance() {
      if (!this.drugInfo) return ''
      
      const parts = []
      if (this.drugInfo.drug_name) parts.push(`药品名称：${this.drugInfo.drug_name}`)
      if (this.drugInfo.dosage) parts.push(`用法用量：${this.drugInfo.dosage}`)
      if (this.drugInfo.usage) parts.push(`使用方法：${this.drugInfo.usage}`)
      if (this.drugInfo.manufacturer) parts.push(`生产厂家：${this.drugInfo.manufacturer}`)
      if (this.drugInfo.expiry_date) parts.push(`有效期至：${this.drugInfo.expiry_date}`)
      
      if (parts.length === 0) return '未识别到药品信息'
      
      return `识别成功。${parts.join('。')}。请遵医嘱使用。`
    },
    
    // 保存结果
    saveResult() {
      if (!this.drugInfo || !this.drugInfo.drug_name) {
        uni.showToast({
          title: '没有可保存的药品信息',
          icon: 'error',
          duration: 2000
        })
        return
      }
      
      try {
        // 保存到本地存储
        const history = uni.getStorageSync('drug_history') || []
        const newRecord = {
          id: Date.now(),
          drugInfo: this.drugInfo,
          timestamp: new Date().toISOString(),
          confidence: this.confidence,
          voiceGuidance: this.voiceGuidance
        }
        
        history.unshift(newRecord)
        uni.setStorageSync('drug_history', history.slice(0, 50)) // 最多保存50条
        
        uni.showToast({
          title: '保存成功',
          icon: 'success',
          duration: 2000
        })
        
        console.log('保存的记录:', newRecord)
      } catch (error) {
        console.error('保存失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'error',
          duration: 2000
        })
      }
    },
    
    // 重新拍照
    retakePhoto() {
      uni.navigateBack({
        delta: 1
      })
    },
    
    // 切换调试信息显示
    toggleDebug() {
      this.showDebug = !this.showDebug
    }
  },
  
  // 长按卡片显示调试信息
  onReady() {
    // 添加长按事件监听（可选）
  }
}
</script>

<style scoped>
.result-container {
  padding: 40rpx;
  min-height: 100vh;
  background: #f5f5f5;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.status-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333333;
}

.confidence {
  font-size: 24rpx;
  color: #666666;
  background: #e8f5e8;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.drug-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 2rpx solid #e0e0e0;
}

.drug-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333333;
  flex: 1;
  margin-right: 20rpx;
}

.status-badge {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: bold;
}

.status-badge.success {
  background: #e8f5e8;
  color: #4CAF50;
}

.drug-details {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.icon {
  font-size: 28rpx;
}

.label {
  font-size: 28rpx;
  font-weight: bold;
  color: #666666;
}

.value {
  font-size: 28rpx;
  color: #333333;
  line-height: 1.5;
  margin-left: 43rpx; /* 对齐文本 */
}

.empty-state {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 80rpx 40rpx;
  text-align: center;
  margin-bottom: 40rpx;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 20rpx;
}

.empty-text {
  display: block;
  font-size: 32rpx;
  color: #333333;
  margin-bottom: 10rpx;
  font-weight: bold;
}

.empty-desc {
  display: block;
  font-size: 26rpx;
  color: #666666;
}

.voice-section {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
}

.section-header {
  margin-bottom: 20rpx;
  padding-bottom: 15rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #333333;
  margin-bottom: 5rpx;
}

.section-desc {
  display: block;
  font-size: 24rpx;
  color: #666666;
}

.voice-text {
  font-size: 26rpx;
  color: #333333;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.action-btn {
  height: 88rpx;
  border-radius: 44rpx;
  border: none;
  font-size: 30rpx;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15rpx;
}

.action-btn.primary {
  background: #4CAF50;
  color: white;
}

.action-btn.secondary {
  background: #ffffff;
  color: #333333;
  border: 2rpx solid #e0e0e0;
}

.btn-icon {
  font-size: 32rpx;
}

.debug-info {
  background: #f8f8f8;
  border-radius: 10rpx;
  padding: 20rpx;
  margin-top: 40rpx;
  border: 1rpx dashed #cccccc;
}

.debug-title {
  display: block;
  font-size: 24rpx;
  color: #666666;
  margin-bottom: 10rpx;
  font-weight: bold;
}

.debug-content {
  font-size: 20rpx;
  color: #999999;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>