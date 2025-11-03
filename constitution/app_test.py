"""
简单的药品识别测试后端
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置应用
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'tmp'

# 确保临时目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Drug Recognition API',
        'version': '1.0.0',
        'message': '服务正常运行'
    })

@app.route('/api/recognize', methods=['POST'])
def recognize_drug():
    """药品识别接口 - 测试版本"""
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传图片文件',
                'error_code': 'NO_IMAGE',
                'voice_guidance': '请重新拍照'
            }), 400

        image_file = request.files['image']
        
        # 验证文件
        if not image_file.filename:
            return jsonify({
                'success': False,
                'error': '文件名为空',
                'error_code': 'EMPTY_FILENAME',
                'voice_guidance': '请重新拍照'
            }), 400

        # 保存文件
        filename = image_file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        
        # 模拟药品识别结果
        drug_info = {
            'drug_name': '阿莫西林胶囊',
            'dosage': '一次0.5g，一日3次',
            'usage': '口服',
            'manufacturer': 'XX制药有限公司',
            'expiry_date': '2025年12月',
            'batch_number': '20241201'
        }
        
        validation_result = {
            'completeness_score': 100,
            'present_fields': ['药品名称', '用法用量', '使用方法', '生产厂家'],
            'missing_fields': [],
            'need_retake': False,
            'is_complete': True
        }
        
        voice_guidance = "药品名称：阿莫西林胶囊。用法用量：一次0.5g，一日3次。使用方法：口服。生产厂家：XX制药有限公司。有效期：2025年12月。"
        
        return jsonify({
            'success': True,
            'drug_info': drug_info,
            'ocr_confidence': 95,
            'processing_time': '2024-01-01T12:00:00',
            'image_processed': True,
            'validation': validation_result,
            'voice_guidance': voice_guidance
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}',
            'error_code': 'INTERNAL_ERROR',
            'voice_guidance': '识别出错，请重试'
        }), 500

if __name__ == '__main__':
    print("=" * 50)
    print("药品识别测试后端启动中...")
    print("服务地址: http://0.0.0.0:5000")
    print("健康检查: http://0.0.0.0:5000/api/health")
    print("识别接口: http://0.0.0.0:5000/api/recognize")
    print("=" * 50)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except Exception as e:
        print(f"应用启动失败: {str(e)}")
        raise
