"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  data() {
    return {
      resultData: null,
      // 完整的识别结果数据
      drugInfo: null,
      // 药品信息
      confidence: 0,
      // 识别置信度
      voiceGuidance: "",
      // 语音播报文本
      showDebug: false,
      // 是否显示调试信息
      rawText: ""
      // 原始文本（如果需要的话）
    };
  },
  onLoad(options) {
    common_vendor.index.__f__("log", "at pages/result/result.vue:125", "结果页面参数:", options);
    if (options.data) {
      try {
        const resultData = JSON.parse(decodeURIComponent(options.data));
        common_vendor.index.__f__("log", "at pages/result/result.vue:131", "识别结果数据:", resultData);
        this.resultData = resultData;
        this.drugInfo = resultData.drug_info || {};
        this.confidence = resultData.ocr_confidence || 0;
        this.voiceGuidance = resultData.voice_guidance || "";
        this.rawText = this.extractRawText(this.drugInfo);
        common_vendor.index.__f__("log", "at pages/result/result.vue:142", "解析后的药品信息:", this.drugInfo);
        common_vendor.index.__f__("log", "at pages/result/result.vue:143", "语音播报文本:", this.voiceGuidance);
        setTimeout(() => {
          this.readAloud();
        }, 1e3);
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/result/result.vue:151", "解析结果数据失败:", error);
        common_vendor.index.showToast({
          title: "数据解析失败",
          icon: "error",
          duration: 2e3
        });
      }
    } else {
      common_vendor.index.__f__("warn", "at pages/result/result.vue:159", "没有接收到数据");
      common_vendor.index.showToast({
        title: "未接收到识别数据",
        icon: "error",
        duration: 2e3
      });
    }
  },
  methods: {
    // 提取原始文本
    extractRawText(drugInfo) {
      if (!drugInfo)
        return "";
      const parts = [];
      if (drugInfo.drug_name)
        parts.push(`药品名称：${drugInfo.drug_name}`);
      if (drugInfo.dosage)
        parts.push(`用法用量：${drugInfo.dosage}`);
      if (drugInfo.usage)
        parts.push(`使用方法：${drugInfo.usage}`);
      if (drugInfo.expiry_date)
        parts.push(`有效期：${drugInfo.expiry_date}`);
      if (drugInfo.manufacturer)
        parts.push(`生产厂家：${drugInfo.manufacturer}`);
      if (drugInfo.batch_number)
        parts.push(`批号：${drugInfo.batch_number}`);
      if (drugInfo.storage)
        parts.push(`贮藏：${drugInfo.storage}`);
      return parts.join("；");
    },
    // 语音播报
    readAloud() {
      if (!this.voiceGuidance) {
        this.voiceGuidance = this.generateVoiceGuidance();
      }
      common_vendor.index.__f__("log", "at pages/result/result.vue:192", "语音播报内容:", this.voiceGuidance);
      if (typeof common_vendor.wx$1 !== "undefined" && common_vendor.wx$1.createInnerAudioContext) {
        common_vendor.index.vibrateLong({
          success: () => {
            common_vendor.index.__f__("log", "at pages/result/result.vue:200", "震动反馈 - 模拟语音播报");
          }
        });
      }
      common_vendor.index.showToast({
        title: "语音播报中...",
        icon: "none",
        duration: 3e3
      });
      common_vendor.index.__f__("log", "at pages/result/result.vue:214", "语音内容:", this.voiceGuidance);
    },
    // 生成语音指导文本
    generateVoiceGuidance() {
      if (!this.drugInfo)
        return "";
      const parts = [];
      if (this.drugInfo.drug_name)
        parts.push(`药品名称：${this.drugInfo.drug_name}`);
      if (this.drugInfo.dosage)
        parts.push(`用法用量：${this.drugInfo.dosage}`);
      if (this.drugInfo.usage)
        parts.push(`使用方法：${this.drugInfo.usage}`);
      if (this.drugInfo.manufacturer)
        parts.push(`生产厂家：${this.drugInfo.manufacturer}`);
      if (this.drugInfo.expiry_date)
        parts.push(`有效期至：${this.drugInfo.expiry_date}`);
      if (parts.length === 0)
        return "未识别到药品信息";
      return `识别成功。${parts.join("。")}。请遵医嘱使用。`;
    },
    // 保存结果
    saveResult() {
      if (!this.drugInfo || !this.drugInfo.drug_name) {
        common_vendor.index.showToast({
          title: "没有可保存的药品信息",
          icon: "error",
          duration: 2e3
        });
        return;
      }
      try {
        const history = common_vendor.index.getStorageSync("drug_history") || [];
        const newRecord = {
          id: Date.now(),
          drugInfo: this.drugInfo,
          timestamp: (/* @__PURE__ */ new Date()).toISOString(),
          confidence: this.confidence,
          voiceGuidance: this.voiceGuidance
        };
        history.unshift(newRecord);
        common_vendor.index.setStorageSync("drug_history", history.slice(0, 50));
        common_vendor.index.showToast({
          title: "保存成功",
          icon: "success",
          duration: 2e3
        });
        common_vendor.index.__f__("log", "at pages/result/result.vue:264", "保存的记录:", newRecord);
      } catch (error) {
        common_vendor.index.__f__("error", "at pages/result/result.vue:266", "保存失败:", error);
        common_vendor.index.showToast({
          title: "保存失败",
          icon: "error",
          duration: 2e3
        });
      }
    },
    // 重新拍照
    retakePhoto() {
      common_vendor.index.navigateBack({
        delta: 1
      });
    },
    // 切换调试信息显示
    toggleDebug() {
      this.showDebug = !this.showDebug;
    }
  },
  // 长按卡片显示调试信息
  onReady() {
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return common_vendor.e({
    a: $data.confidence > 0
  }, $data.confidence > 0 ? {
    b: common_vendor.t($data.confidence)
  } : {}, {
    c: $data.drugInfo && $data.drugInfo.drug_name
  }, $data.drugInfo && $data.drugInfo.drug_name ? common_vendor.e({
    d: common_vendor.t($data.drugInfo.drug_name),
    e: $data.resultData && $data.resultData.success
  }, $data.resultData && $data.resultData.success ? {} : {}, {
    f: $data.drugInfo.dosage
  }, $data.drugInfo.dosage ? {
    g: common_vendor.t($data.drugInfo.dosage)
  } : {}, {
    h: $data.drugInfo.usage
  }, $data.drugInfo.usage ? {
    i: common_vendor.t($data.drugInfo.usage)
  } : {}, {
    j: $data.drugInfo.expiry_date
  }, $data.drugInfo.expiry_date ? {
    k: common_vendor.t($data.drugInfo.expiry_date)
  } : {}, {
    l: $data.drugInfo.manufacturer
  }, $data.drugInfo.manufacturer ? {
    m: common_vendor.t($data.drugInfo.manufacturer)
  } : {}, {
    n: $data.drugInfo.batch_number
  }, $data.drugInfo.batch_number ? {
    o: common_vendor.t($data.drugInfo.batch_number)
  } : {}, {
    p: $data.drugInfo.storage
  }, $data.drugInfo.storage ? {
    q: common_vendor.t($data.drugInfo.storage)
  } : {}) : {}, {
    r: $data.voiceGuidance
  }, $data.voiceGuidance ? {
    s: common_vendor.t($data.voiceGuidance)
  } : {}, {
    t: $data.voiceGuidance
  }, $data.voiceGuidance ? {
    v: common_vendor.o((...args) => $options.readAloud && $options.readAloud(...args))
  } : {}, {
    w: $data.drugInfo && $data.drugInfo.drug_name
  }, $data.drugInfo && $data.drugInfo.drug_name ? {
    x: common_vendor.o((...args) => $options.saveResult && $options.saveResult(...args))
  } : {}, {
    y: common_vendor.o((...args) => $options.retakePhoto && $options.retakePhoto(...args)),
    z: $data.showDebug && $data.resultData
  }, $data.showDebug && $data.resultData ? {
    A: common_vendor.t(JSON.stringify($data.resultData, null, 2))
  } : {});
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render], ["__scopeId", "data-v-b615976f"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/result/result.js.map
