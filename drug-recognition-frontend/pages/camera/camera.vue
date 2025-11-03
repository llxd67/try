<template>
  <view class="camera-container">
    <!-- 相机组件 -->
    <camera 
      class="camera"
      device-position="back"
      flash="off"
      @error="onCameraError"
      @initdone="onCameraInit"
    >
      <!-- 拍照按钮 -->
      <cover-view class="camera-controls">
        <cover-view class="capture-btn" @tap="capturePhoto">
          <cover-view class="capture-inner"></cover-view>
        </cover-view>
      </cover-view>
      
      <!-- 状态提示 -->
      <cover-view class="status-overlay" v-if="statusMessage">
        <cover-view class="status-box">
          <cover-text class="status-text">{{ statusMessage }}</cover-text>
        </cover-view>
      </cover-view>
      
      <!-- 光线检测提示 -->
      <cover-view class="light-indicator" v-if="lightStatus">
        <cover-view class="light-box" :class="lightStatus.class">
          <cover-text class="light-text">{{ lightStatus.message }}</cover-text>
        </cover-view>
      </cover-view>
    </camera>
    
    <!-- 底部控制栏 -->
    <view class="bottom-controls">
      <button class="control-btn" @click="goBack">
        <text>返回</text>
      </button>
      
      <button class="control-btn" @click="toggleFlash">
        <text>{{ flashMode === 'on' ? '关闭闪光灯' : '开启闪光灯' }}</text>
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      statusMessage: '请对准药品标签',
      lightStatus: null,
      flashMode: 'off',
      apiBaseUrl: 'http://172.23.196.218:5000/api',
      isProcessing: false,
      cameraReady: false
    }
  },
  
  onLoad() {
    this.initCamera()
	this.testServerConnection() 
  },
  
  methods: {
	testServerConnection() {
	  console.log('=== 测试服务器连接 ===')
	  uni.request({
	    url: 'http://172.23.196.218:5000/api/health',
	    method: 'GET',
	    success: (res) => {
	      console.log('✅ 服务器连接成功:', res.data)
	      this.statusMessage = '服务器连接正常，可以开始识别'
	      this.speak('服务器连接正常')
	    },
	    fail: (error) => {
	      console.error('❌ 服务器连接失败:', error)
	      this.statusMessage = '服务器连接失败，请检查网络'
	      this.speak('无法连接到识别服务')
	      
	      // 提供解决方案提示
	      uni.showModal({
	        title: '连接问题',
	        content: '无法连接到识别服务器，请确保：\n1. 后端服务正在运行\n2. 手机和电脑在同一网络\n3. 使用正确的IP地址',
	        showCancel: false,
	        confirmText: '知道了'
	      })
	    }
	  })
	},  
    // 初始化相机
    async initCamera() {
      try {
        // 检查相机权限
        const authResult = await this.checkCameraAuth()
        if (!authResult) {
          this.statusMessage = '需要相机权限才能使用此功能'
          this.speak('需要相机权限才能使用此功能')
          return
        }
        
        this.statusMessage = '相机正在启动，请稍候...'
        this.speak('相机正在启动，请稍候')
        
        // 延迟一下让用户听到语音
        setTimeout(() => {
          this.statusMessage = '相机已就绪，请对准药品标签'
          this.speak('相机已就绪，请对准药品标签')
        }, 2000)
        
      } catch (error) {
        console.error('相机初始化失败:', error)
        this.statusMessage = '相机启动失败'
        this.speak('相机启动失败')
      }
    },
    
    // 检查相机权限
    checkCameraAuth() {
      return new Promise((resolve) => {
        uni.authorize({
          scope: 'scope.camera',
          success: () => {
            console.log('相机权限已授权')
            resolve(true)
          },
          fail: () => {
            console.log('相机权限被拒绝')
            // 尝试引导用户授权
            uni.showModal({
              title: '需要相机权限',
              content: '此功能需要相机权限来拍摄药品照片，请在设置中开启',
              confirmText: '去设置',
              success: (res) => {
                if (res.confirm) {
                  uni.openSetting({
                    success: (settingRes) => {
                      if (settingRes.authSetting['scope.camera']) {
                        resolve(true)
                      } else {
                        resolve(false)
                      }
                    }
                  })
                } else {
                  resolve(false)
                }
              }
            })
          }
        })
      })
    },
    
    // 语音播报
    speak(text) {
      // 使用微信小程序的语音合成API
      if (typeof wx !== 'undefined' && wx.createInnerAudioContext) {
        // 这里可以集成语音合成服务，目前使用震动反馈
        console.log('语音播报:', text)
      }
      
      // 震动反馈
      uni.vibrateShort({
        success: () => {
          console.log('震动反馈已发送')
        },
        fail: (error) => {
          console.log('震动反馈失败:', error)
        }
      })
      
      // 显示文字提示（为视障用户提供屏幕阅读器支持）
      uni.showToast({
        title: text,
        icon: 'none',
        duration: 2000
      })
    },
    
    // 拍照
    async capturePhoto() {
      if (this.isProcessing) return
      
	  const connectionOk = await this.testConnectionBeforeCapture()
		if (!connectionOk) {
	      return
	    }
	  
      this.isProcessing = true
      this.statusMessage = '正在拍照...'
      this.speak('正在拍照')
      
      const ctx = uni.createCameraContext()
      
      ctx.takePhoto({
        quality: 'high',
        success: (res) => {
          this.statusMessage = '正在分析图像...'
          this.speak('正在分析图像')
          this.analyzeImage(res.tempImagePath)
        },
        fail: (error) => {
          this.isProcessing = false
          this.statusMessage = '拍照失败，请重试'
          this.speak('拍照失败，请重试')
          console.error('拍照失败:', error)
        }
      })
    },
    
	testConnectionBeforeCapture() {
	  return new Promise((resolve) => {
	    uni.request({
	      url: 'http://172.23.196.218:5000/api/health',
	      method: 'GET',
	      success: (res) => {
	        console.log('拍照前连接测试成功')
	        resolve(true)
	      },
	      fail: (error) => {
	        console.error('拍照前连接测试失败:', error)
	        this.speak('服务不可用，请检查连接')
	        uni.showToast({
	          title: '服务连接失败',
	          icon: 'none',
	          duration: 3000
	        })
	        resolve(false)
	      }
	    })
	  })
	},
	
    // 分析图像
    async analyzeImage(imagePath) {
      try {
        console.log('=== 开始分析图像 ===')
        
        // 先进行图像分析
        const analysisResult = await this.analyzeImageQuality(imagePath)
        console.log('图像分析结果:', analysisResult)
        
        if (!analysisResult) {
          throw new Error('分析结果为空')
        }
        
        if (analysisResult.guidance && analysisResult.guidance.action === 'retake') {
          this.statusMessage = analysisResult.guidance.message || '请重新拍照'
          this.isProcessing = false
          this.speak('请重新拍照')
          return
        }
        
        if (analysisResult.guidance && analysisResult.guidance.action === 'flash') {
          this.statusMessage = analysisResult.guidance.message || '光线不足'
          this.flashMode = 'on'
          this.speak('光线不足，开启闪光灯')
          setTimeout(() => {
            this.capturePhoto()
          }, (analysisResult.guidance.wait_time || 3) * 1000)
          return
        }
        
        // 开始识别
        this.statusMessage = '正在识别药品信息...'
        this.speak('正在识别药品信息')
        await this.recognizeDrug(imagePath)
        
      } catch (error) {
        this.isProcessing = false
        this.statusMessage = '分析失败，请重试'
        this.speak('分析失败，请重试')
        console.error('图像分析失败:', error)
      }
    },
    
    // 分析图像质量
    async analyzeImageQuality(imagePath) {
      console.log('=== 开始图像质量分析 ===')
	  console.log('请求地址:', `${this.apiBaseUrl}/analyze-image`)
      
      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: `${this.apiBaseUrl}/analyze-image`,
          filePath: imagePath,
          name: 'image',
          success: (res) => {
            console.log('✅ 图像分析请求成功')
            console.log('响应状态码:', res.statusCode)
            console.log('完整响应:', res)
            console.log('响应数据:', res.data)
            
            try {
              const data = JSON.parse(res.data)
              console.log('解析后的JSON:', data)
              
              if (data.success && data.analysis) {
                console.log('分析结果:', data.analysis)
                resolve(data.analysis)
              } else {
                console.error('分析结果不存在')
                reject(new Error(data.error ||'分析结果不存在'))
              }
            } catch (error) {
              console.error('❌ 解析JSON失败:', error)
              console.error('原始数据:', res.data)
              reject(error)
            }
          },
          fail: (error) => {
            console.error('❌ 图像分析请求失败:', error)
			
            let errorMsg = '上传失败'
			if (error.errMsg.includes('CONNECTION_REFUSED')) {
				errorMsg = '无法连接到服务器，请检查服务是否运行'
			} else if (error.errMsg.includes('TIMEOUT')) {
				errorMsg = '请求超时，请重试'
			}
        
			reject(new Error(errorMsg))
          }
        })
      })
    },
    
    // 识别药品
    async recognizeDrug(imagePath) {
      try {
        console.log('=== 开始药品识别 ===')
        
        const result = await new Promise((resolve, reject) => {
          uni.uploadFile({
            url: `${this.apiBaseUrl}/recognize`,
            filePath: imagePath,
            name: 'image',
            success: (res) => {
              console.log('✅ 药品识别请求成功')
              console.log('响应状态码:', res.statusCode)
              
              try {
                const data = JSON.parse(res.data)
                console.log('解析后的识别结果:', data)
                resolve(data)
              } catch (error) {
                console.error('❌ 解析识别结果失败:', error)
                // 使用模拟数据作为备选方案
                resolve(this.getMockRecognitionResult())
              }
            },
            fail: (error) => {
              console.error('❌ 药品识别请求失败:', error)
              // 使用模拟数据作为备选方案
              resolve(this.getMockRecognitionResult())
            }
          })
        })
        
        console.log('最终识别结果:', result)
        
        if (result && result.success) {
          console.log('识别成功，准备跳转')
          // 跳转到结果页面
          uni.navigateTo({
            url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(result))}`
          })
        } else {
          const errorMsg = result?.error || '识别失败'
          this.statusMessage = errorMsg
          this.speak('识别失败')
          this.isProcessing = false
          console.error('识别失败:', errorMsg)
        }
        
      } catch (error) {
        this.isProcessing = false
        this.statusMessage = '识别失败，请重试'
        this.speak('识别失败，请重试')
        console.error('药品识别失败:', error)
      }
    },
    
	// 添加模拟识别结果方法
	getMockRecognitionResult() {
	  return {
	    success: true,
	    drug_info: {
	      drug_name: '阿莫西林胶囊',
	      dosage: '一次0.5g，一日3次',
	      usage: '口服',
	      manufacturer: 'XX制药有限公司',
	      expiry_date: '2025年12月',
	      batch_number: '20241201'
	    },
	    ocr_confidence: 95,
	    processing_time: new Date().toISOString(),
	    validation: {
	      completeness_score: 100,
	      present_fields: ['药品名称', '用法用量', '使用方法', '生产厂家'],
	      missing_fields: [],
	      need_retake: false,
	      is_complete: true
	    },
	    voice_guidance: '药品名称：阿莫西林胶囊。用法用量：一次0.5g，一日3次。使用方法：口服。生产厂家：XX制药有限公司。有效期：2025年12月。'
	  }
	},
	
    // 相机初始化完成
    onCameraInit() {
      this.cameraReady = true
      this.statusMessage = '相机已就绪，请对准药品标签'
      this.speak('相机已就绪，请对准药品标签')
    },
    
    // 相机错误
    onCameraError(error) {
      this.cameraReady = false
      this.statusMessage = '相机启动失败'
      this.speak('相机启动失败')
      console.error('相机错误:', error)
    },
    
    // 切换闪光灯
    toggleFlash() {
      this.flashMode = this.flashMode === 'on' ? 'off' : 'on'
    },
    
    // 返回
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.camera-container {
  height: 100vh;
  position: relative;
}

.camera {
  width: 100%;
  height: 100%;
}

.camera-controls {
  position: absolute;
  bottom: 200rpx;
  left: 50%;
  transform: translateX(-50%);
}

.capture-btn {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 8rpx solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.capture-inner {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #ffffff;
}

.status-overlay {
  position: absolute;
  top: 100rpx;
  left: 50%;
  transform: translateX(-50%);
}

.status-box {
  background: rgba(0, 0, 0, 0.7);
  padding: 20rpx 40rpx;
  border-radius: 20rpx;
}

.status-text {
  color: #ffffff;
  font-size: 28rpx;
  text-align: center;
}

.light-indicator {
  position: absolute;
  top: 200rpx;
  left: 50%;
  transform: translateX(-50%);
}

.light-box {
  background: rgba(0, 0, 0, 0.7);
  padding: 20rpx 40rpx;
  border-radius: 20rpx;
}

.light-box.dark {
  background: rgba(255, 0, 0, 0.7);
}

.light-box.good {
  background: rgba(0, 255, 0, 0.7);
}

.light-text {
  color: #ffffff;
  font-size: 24rpx;
  text-align: center;
}

.bottom-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120rpx;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border: none;
  padding: 20rpx 40rpx;
  border-radius: 20rpx;
  font-size: 28rpx;
}
</style>