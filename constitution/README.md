# 药品识别助手 - 视障版

专为视障人群设计的药品识别微信小程序，通过拍照功能自动识别药品信息并提供语音播报。

## 🌟 功能特点

- 📷 **智能拍照识别** - 自动拍摄药品标签进行文字识别
- 🔊 **语音播报** - 全程语音指导，专为视障用户优化
- 📋 **信息提取** - 智能提取药品名称、用法用量、注意事项等
- 📱 **无障碍设计** - 大按钮、高对比度、震动反馈
- 📚 **历史记录** - 保存识别历史，方便查看
- ⚙️ **个性化设置** - 可调节语音速度、音量等

## 🏗️ 项目结构

```
drug-recognition-backend/                 # 后端项目
│
├── app.py                               # Flask应用主入口
├── config.py                            # 配置文件
├── requirements.txt                     # Python依赖包列表
├── env.example                          # 环境变量示例文件
├── README.md                           # 项目说明文档
│
├── api/                                # API路由模块
│   ├── __init__.py
│   └── routes.py                       # 主要API路由
│
├── services/                           # 业务逻辑服务层
│   ├── __init__.py
│   ├── ocr_service.py                  # OCR服务封装
│   ├── drug_extractor.py               # 药品信息提取服务
│   └── image_processor.py              # 图像处理服务
│
├── utils/                              # 工具函数库
│   ├── __init__.py
│   └── logger.py                       # 日志配置工具
│
├── logs/                               # 日志文件目录
├── tmp/                                # 临时文件目录
│
└── miniprogram/                        # 微信小程序前端
    ├── app.json                        # 小程序配置
    ├── app.js                          # 全局逻辑
    └── pages/                          # 页面文件
        ├── index/                      # 首页
        ├── camera/                     # 拍照页面
        ├── result/                     # 结果页面
        ├── history/                    # 历史记录
        └── settings/                   # 设置页面
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 百度云OCR服务账号
- 微信开发者工具

### 后端部署

1. **克隆项目**
```bash
git clone <repository-url>
cd drug-recognition-backend
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，填写百度云OCR密钥
```

4. **启动服务**
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

### 前端开发

1. **打开微信开发者工具**
2. **导入项目** - 选择 `miniprogram` 目录
3. **配置服务器地址** - 修改 `app.js` 中的 `apiBaseUrl`
4. **预览测试** - 在开发者工具中预览

## 📖 API文档

### 健康检查
```
GET /api/health
```

### 药品识别
```
POST /api/recognize
Content-Type: multipart/form-data

参数:
- image: 图片文件 (PNG, JPG, JPEG, BMP)

响应:
{
  "success": true,
  "drug_info": {
    "drug_name": "药品名称",
    "usage": "用法",
    "dosage": "用量",
    "side_effects": "不良反应",
    "contraindications": "禁忌",
    "allergens": "过敏源",
    "storage": "贮藏",
    "manufacturer": "生产厂家",
    "expiry_date": "有效期",
    "batch_number": "批号",
    "raw_text": "原始文本",
    "confidence": 0.95
  },
  "ocr_confidence": 10,
  "processing_time": "2024-01-01T12:00:00"
}
```

### Base64识别
```
POST /api/recognize/base64
Content-Type: application/json

参数:
{
  "image": "base64编码的图片数据"
}
```

### 批量识别
```
POST /api/batch/recognize
Content-Type: multipart/form-data

参数:
- images: 多个图片文件 (最多5张)
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BAIDU_API_KEY` | 百度云OCR API Key | 必填 |
| `BAIDU_SECRET_KEY` | 百度云OCR Secret Key | 必填 |
| `DEBUG` | 调试模式 | False |
| `HOST` | 服务器地址 | 0.0.0.0 |
| `PORT` | 服务器端口 | 5000 |
| `LOG_LEVEL` | 日志级别 | INFO |

### 图像处理配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `MAX_IMAGE_WIDTH` | 最大图片宽度 | 1600 |
| `MAX_IMAGE_HEIGHT` | 最大图片高度 | 1600 |
| `CLAHE_CLIP_LIMIT` | 对比度增强参数 | 3.0 |
| `MAX_CONTENT_LENGTH` | 最大文件大小 | 16MB |

## 🎯 无障碍功能

### 语音播报
- 操作提示音
- 识别结果朗读
- 错误信息播报
- 可调节语速和音量

### 触觉反馈
- 按钮点击震动
- 操作确认震动
- 错误提示震动

### 视觉优化
- 高对比度配色
- 大尺寸按钮
- 清晰的文字提示
- 简洁的界面布局

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_ocr_service.py

# 生成覆盖率报告
python -m pytest --cov=. tests/
```

### 测试数据
测试图片放在 `tests/fixtures/sample_drug_images/` 目录下

## 📝 开发指南

### 添加新的药品信息提取规则

在 `services/drug_extractor.py` 中修改 `drug_keywords` 字典：

```python
self.drug_keywords = {
    'drug_names': ['片', '胶囊', '颗粒', ...],  # 添加新的药品类型
    'usage_keywords': ['口服', '外用', ...],    # 添加新的用法关键词
    # ... 其他关键词
}
```

### 自定义图像处理

在 `services/image_processor.py` 中修改预处理流程：

```python
def preprocess_image(self, image_path: str) -> str:
    # 添加自定义的图像处理步骤
    pass
```

### 添加新的API接口

在 `api/routes.py` 中添加新的路由：

```python
@api_bp.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    # 实现新的API逻辑
    pass
```

## 🚀 部署

### Docker部署

```bash
# 构建镜像
docker build -t drug-recognition .

# 运行容器
docker run -p 5000:5000 -e BAIDU_API_KEY=your_key drug-recognition
```

### 云服务器部署

1. 上传代码到服务器
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量
4. 使用gunicorn启动：`gunicorn -w 4 -b 0.0.0.0:5000 app:app`

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 百度智能云OCR服务
- 微信小程序平台
- 开源社区贡献者

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至：[your-email@example.com]
- 微信群：[群二维码]

---

**让药品信息触手可及，为视障人群提供更好的生活体验** 🌟

