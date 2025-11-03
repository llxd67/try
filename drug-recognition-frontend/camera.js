"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  data() {
    return {
      statusMessage: "请对准药品标签",
      lightStatus: null,
      flashMode: "off",
      apiBaseUrl: "http://172.23.238.36:5000/api",
      isProcessing: false,
      cameraReady: false
    };
  },
  onLoad() {
    this.initCamera();
    this.testServerConnection();
  },
  methods: {
    testServerConnection() {
      common_vendor.index.__f__("log", "at pages/camera/camera.vue:66", "=== 测试服务器连接 ===");
      common_vendor.index.request({
        url: "http://172.23.238.36:5000/api/health",
        method: "GET",
        success: (res) => {
          common_vendor.index.__f__("log", "at pages/camera/camera.vue:71", "✅ 服务器连接成功:", res.data);
          this.statusMessage = "服务器连接正常，可以开始识别";
          this.speak("服务器连接正常");
        },
        fail: (error) => {
          common_vendor.index.__f__("error", "at pages/camera/camera.vue:76", "❌ 服务器连接失败:", error);
          this.statusMessage = "服务器连接失败，请检查网络";
          this.speak("无法连接到识别服务");
          common_vendor.index.showModal({
            title: "连接问题",
            content: "无法连接到识别服务器，请确保：\n1. 后端服务正在运行\n2. 手机和电脑在同一网络\n3. 使用正确的IP地址",
            showCancel: false,
            confirmText: "知道了"
          });
        }
      });
    },
    // 初始化相机
    async initCamera() {
      try {
        const authResult = await this.checkCameraAuth();
        if (!authResult) {
          this.statusMessage = "需要相机权限才能使用此功能";
          this.speak("需要相机权限才能使用此功能");
          return;
        }
        this.statusMessage = "相机正在启动，请稍候...";
        this.speak("相机正在启动，请稍候");
        setTimeout(() => {
          this.statusMessage = "相机已就绪，请对准药品标签";
          this.speak("相机已就绪，请对准药品标签");
        }, 2e3);
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/camera/camera.vue:111", "相机初始化失败:", error);
        this.statusMessage = "相机启动失败";
        this.speak("相机启动失败");
      }
    },
    // 检查相机权限
    checkCameraAuth() {
      return new Promise((resolve) => {
        common_vendor.index.authorize({
          scope: "scope.camera",
          success: () => {
            common_vendor.index.__f__("log", "at pages/camera/camera.vue:123", "相机权限已授权");
            resolve(true);
          },
          fail: () => {
            common_vendor.index.__f__("log", "at pages/camera/camera.vue:127", "相机权限被拒绝");
            common_vendor.index.showModal({
              title: "需要相机权限",
              content: "此功能需要相机权限来拍摄药品照片，请在设置中开启",
              confirmText: "去设置",
              success: (res) => {
                if (res.confirm) {
                  common_vendor.index.openSetting({
                    success: (settingRes) => {
                      if (settingRes.authSetting["scope.camera"]) {
                        resolve(true);
                      } else {
                        resolve(false);
                      }
                    }
                  });
                } else {
                  resolve(false);
                }
              }
            });
          }
        });
      });
    },
    // 语音播报
    speak(text) {
      if (typeof common_vendor.wx$1 !== "undefined" && common_vendor.wx$1.createInnerAudioContext) {
        common_vendor.index.__f__("log", "at pages/camera/camera.vue:159", "语音播报:", text);
      }
      common_vendor.index.vibrateShort({
        success: () => {
          common_vendor.index.__f__("log", "at pages/camera/camera.vue:165", "震动反馈已发送");
        },
        fail: (error) => {
          common_vendor.index.__f__("log", "at pages/camera/camera.vue:168", "震动反馈失败:", error);
        }
      });
      common_vendor.index.showToast({
        title: text,
        icon: "none",
        duration: 2e3
      });
    },
    // 拍照
    async capturePhoto() {
      if (this.isProcessing)
        return;
      this.isProcessing = true;
      this.statusMessage = "正在拍照...";
      this.speak("正在拍照");
      const ctx = common_vendor.index.createCameraContext();
      ctx.takePhoto({
        quality: "high",
        success: (res) => {
          this.statusMessage = "正在分析图像...";
          this.speak("正在分析图像");
          this.analyzeImage(res.tempImagePath);
        },
        fail: (error) => {
          this.isProcessing = false;
          this.statusMessage = "拍照失败，请重试";
          this.speak("拍照失败，请重试");
          common_vendor.index.__f__("error", "at pages/camera/camera.vue:201", "拍照失败:", error);
        }
      });
    },
    // 分析图像
    async analyzeImage(imagePath) {
      try {
        common_vendor.index.__f__("log", "at pages/camera/camera.vue:209", "=== 开始分析图像 ===");
        const analysisResult = await this.analyzeImageQuality(imagePath);
        common_vendor.index.__f__("log", "at pages/camera/camera.vue:213", "图像分析结果:", analysisResult);
        if (!analysisResult) {
          throw new Error("分析结果为空");
        }
        if (analysisResult.guidance && analysisResult.guidance.action === "retake") {
          this.statusMessage = analysisResult.guidance.message || "请重新拍照";
          this.isProcessing = false;
          this.speak("请重新拍照");
          return;
        }
        if (analysisResult.guidance && analysisResult.guidance.action === "flash") {
          this.statusMessage = analysisResult.guidance.message || "光线不足";
          this.flashMode = "on";
          this.speak("光线不足，开启闪光灯");
          setTimeout(() => {
            this.capturePhoto();
          }, (analysisResult.guidance.wait_time || 3) * 1e3);
          return;
        }
        this.statusMessage = "正在识别药品信息...";
        this.speak("正在识别药品信息");
        await this.recognizeDrug(imagePath);
      } catch (error) {
        this.isProcessing = false;
        this.statusMessage = "分析失败，请重试";
        this.speak("分析失败，请重试");
        common_vendor.index.__f__("error", "at pages/camera/camera.vue:245", "图像分析失败:", error);
      }
    },
    // 分析图像质量
    async analyzeImageQuality(imagePath) {
      common_vendor.index.__f__("log", "at pages/camera/camera.vue:251", "=== 开始图像质量分析 ===");
      return new Promise((resolve, reject) => {
        common_vendor.index.uploadFile({
          url: `${this.apiBaseUrl}/analyze-image`,
          filePath: imagePath,
          name: "image",
          success: (res) => {
            common_vendor.index.__f__("log", "at pages/camera/camera.vue:259", "✅ 图像分析请求成功");
            common_vendor.index.__f__("log", "at pages/camera/camera.vue:260", "响应状态码:", res.statusCode);
            common_vendor.index.__f__("log", "at pages/camera/camera.vue:261", "完整响应:", res);
            common_vendor.index.__f__("log", "at pages/camera/camera.vue:262", "响应数据:", res.data);
            try {
              const data = JSON.parse(res.data);
              common_vendor.index.__f__("log", "at pages/camera/camera.vue:266", "解析后的JSON:", data);
              if (data.analysis) {
                common_vendor.index.__f__("log", "at pages/camera/camera.vue:269", "分析结果:", data.analysis);
                resolve(data.analysis);
              } else {
                common_vendor.index.__f__("error", "at pages/camera/camera.vue:272", "分析结果不存在");
                reject(new Error("分析结果不存在"));
              }
            } catch (error) {
              common_vendor.index.__f__("error", "at pages/camera/camera.vue:276", "❌ 解析JSON失败:", error);
              common_vendor.index.__f__("error", "at pages/camera/camera.vue:277", "原始数据:", res.data);
              reject(error);
            }
          },
          fail: (error) => {
            common_vendor.index.__f__("error", "at pages/camera/camera.vue:282", "❌ 图像分析请求失败:", error);
            reject(error);
          }
        });
      });
    },
    // 识别药品
    async recognizeDrug(imagePath) {
      try {
        common_vendor.index.__f__("log", "at pages/camera/camera.vue:292", "=== 开始药品识别 ===");
        const result = await new Promise((resolve, reject) => {
          common_vendor.index.uploadFile({
            url: `${this.apiBaseUrl}/recognize`,
            filePath: imagePath,
            name: "image",
            success: (res) => {
              common_vendor.index.__f__("log", "at pages/camera/camera.vue:300", "✅ 药品识别请求成功");
              common_vendor.index.__f__("log", "at pages/camera/camera.vue:301", "响应状态码:", res.statusCode);
              common_vendor.index.__f__("log", "at pages/camera/camera.vue:302", "响应数据:", res.data);
              try {
                const data = JSON.parse(res.data);
                common_vendor.index.__f__("log", "at pages/camera/camera.vue:306", "解析后的识别结果:", data);
                resolve(data);
              } catch (error) {
                common_vendor.index.__f__("error", "at pages/camera/camera.vue:309", "❌ 解析识别结果失败:", error);
                reject(error);
              }
            },
            fail: (error) => {
              common_vendor.index.__f__("error", "at pages/camera/camera.vue:314", "❌ 药品识别请求失败:", error);
              reject(error);
            }
          });
        });
        common_vendor.index.__f__("log", "at pages/camera/camera.vue:320", "最终识别结果:", result);
        if (result && result.success) {
          common_vendor.index.__f__("log", "at pages/camera/camera.vue:323", "识别成功，准备跳转");
          common_vendor.index.navigateTo({
            url: `/pages/result/result?data=${encodeURIComponent(JSON.stringify(result))}`
          });
        } else {
          const errorMsg = (result == null ? void 0 : result.error) || "识别失败";
          this.statusMessage = errorMsg;
          this.speak("识别失败");
          this.isProcessing = false;
          common_vendor.index.__f__("error", "at pages/camera/camera.vue:333", "识别失败:", errorMsg);
        }
      } catch (error) {
        this.isProcessing = false;
        this.statusMessage = "识别失败，请重试";
        this.speak("识别失败，请重试");
        common_vendor.index.__f__("error", "at pages/camera/camera.vue:340", "药品识别失败:", error);
      }
    },
    // 相机初始化完成
    onCameraInit() {
      this.cameraReady = true;
      this.statusMessage = "相机已就绪，请对准药品标签";
      this.speak("相机已就绪，请对准药品标签");
    },
    // 相机错误
    onCameraError(error) {
      this.cameraReady = false;
      this.statusMessage = "相机启动失败";
      this.speak("相机启动失败");
      common_vendor.index.__f__("error", "at pages/camera/camera.vue:356", "相机错误:", error);
    },
    // 切换闪光灯
    toggleFlash() {
      this.flashMode = this.flashMode === "on" ? "off" : "on";
    },
    // 返回
    goBack() {
      common_vendor.index.navigateBack();
    }
  }
};
if (!Array) {
  const _component_cover_text = common_vendor.resolveComponent("cover-text");
  _component_cover_text();
}
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: common_vendor.o((...args) => $options.capturePhoto && $options.capturePhoto(...args)),
    b: $data.statusMessage
  }, $data.statusMessage ? {
    c: common_vendor.t($data.statusMessage)
  } : {}, {
    d: $data.lightStatus
  }, $data.lightStatus ? {
    e: common_vendor.t($data.lightStatus.message),
    f: common_vendor.n($data.lightStatus.class)
  } : {}, {
    g: common_vendor.o((...args) => $options.onCameraError && $options.onCameraError(...args)),
    h: common_vendor.o((...args) => $options.onCameraInit && $options.onCameraInit(...args)),
    i: common_vendor.o((...args) => $options.goBack && $options.goBack(...args)),
    j: common_vendor.t($data.flashMode === "on" ? "关闭闪光灯" : "开启闪光灯"),
    k: common_vendor.o((...args) => $options.toggleFlash && $options.toggleFlash(...args))
  });
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-7b8d50ad"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/camera/camera.js.map
