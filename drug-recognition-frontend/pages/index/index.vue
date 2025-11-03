<template>
	<view class="container">
		<view class="header">
			<image class="logo" src="/static/logo.png"></image>
			<text class="app-title">药品识别助手</text>
			<text class="app-subtitle">专为视障人群优化</text>
		</view>
		
		<view class="main-content">
			<view class="start-button" @click="startRecognition">
				<view class="button-icon">📷</view>
				<text class="button-text">开始识别药品</text>
				<text class="button-desc">点击开始拍照识别</text>
			</view>
		</view>
		
		<view class="footer">
			<text class="footer-text">将药品标签对准相机即可开始识别</text>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				
			}
		},
		onLoad() {
			console.log('药品识别助手首页加载')
			// 自动语音播报欢迎信息
			this.speak('欢迎使用药品识别助手')
		},
		methods: {
			startRecognition() {
				// 添加震动反馈
				uni.vibrateShort()
				// 语音提示
				this.speak('正在打开相机')
				// 跳转到相机页面
				uni.navigateTo({
					url: '/pages/camera/camera'
				})
			},
			// 语音播报
			speak(text) {
				// 简单的震动反馈
				uni.vibrateShort({
					success: () => {
						console.log('语音播报:', text)
					}
				})
			}
		}
	}
</script>

<style>
	.container {
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		padding: 40rpx;
	}
	
	.header {
		text-align: center;
		margin-top: 100rpx;
		margin-bottom: 80rpx;
	}
	
	.logo {
		height: 120rpx;
		width: 120rpx;
		margin-bottom: 30rpx;
		border-radius: 20rpx;
	}
	
	.app-title {
		display: block;
		font-size: 48rpx;
		font-weight: bold;
		color: #ffffff;
		margin-bottom: 20rpx;
	}
	
	.app-subtitle {
		display: block;
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.8);
	}
	
	.main-content {
		display: flex;
		justify-content: center;
		align-items: center;
		margin-bottom: 80rpx;
		min-height: 400rpx;
	}
	
	.start-button {
		background: rgba(255, 255, 255, 0.95);
		border-radius: 30rpx;
		padding: 60rpx 80rpx;
		text-align: center;
		box-shadow: 0 12rpx 48rpx rgba(0, 0, 0, 0.15);
		transition: all 0.3s ease;
		border: 4rpx solid rgba(255, 255, 255, 0.3);
		min-width: 400rpx;
	}
	
	.start-button:active {
		transform: scale(0.95);
		box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.2);
	}
	
	.button-icon {
		font-size: 80rpx;
		margin-bottom: 30rpx;
	}
	
	.button-text {
		display: block;
		font-size: 40rpx;
		font-weight: bold;
		color: #333333;
		margin-bottom: 20rpx;
	}
	
	.button-desc {
		display: block;
		font-size: 28rpx;
		color: #666666;
	}
	
	.footer {
		text-align: center;
	}
	
	.footer-text {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.7);
	}
</style>
