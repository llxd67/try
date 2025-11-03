"use strict";
const common_vendor = require("../../common/vendor.js");
const common_assets = require("../../common/assets.js");
const _sfc_main = {
  data() {
    return {};
  },
  onLoad() {
    common_vendor.index.__f__("log", "at pages/index/index.vue:31", "一拍明药首页加载");
    this.speak("欢迎使用一拍明药");
  },
  methods: {
    startRecognition() {
      common_vendor.index.vibrateShort();
      this.speak("正在打开相机");
      common_vendor.index.navigateTo({
        url: "/pages/camera/camera"
      });
    },
    // 语音播报
    speak(text) {
      common_vendor.index.vibrateShort({
        success: () => {
          common_vendor.index.__f__("log", "at pages/index/index.vue:51", "语音播报:", text);
        }
      });
    }
  }
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  return {
    a: common_assets._imports_0,
    b: common_vendor.o((...args) => $options.startRecognition && $options.startRecognition(...args))
  };
}
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["render", _sfc_render]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/index/index.js.map
