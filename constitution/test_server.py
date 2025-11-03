"""
简单的测试服务器 - 用于测试连接
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    print("收到健康检查请求")
    return jsonify({
        'status': 'healthy',
        'service': 'Test Server',
        'version': '1.0.0',
        'message': '测试服务器正常运行'
    })

# 测试识别接口
@app.route('/api/recognize', methods=['POST'])
def test_recognize():
    """测试识别接口"""
    print("收到识别请求")
    print(f"请求方法: {request.method}")
    print(f"请求头: {dict(request.headers)}")
    print(f"请求文件: {list(request.files.keys())}")
    
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            print("没有上传图片文件")
            return jsonify({
                'success': False,
                'error': '没有上传图片文件',
                'error_code': 'NO_IMAGE',
                'voice_guidance': '请重新拍照'
            }), 400

        image_file = request.files['image']
        print(f"收到图片文件: {image_file.filename}")
        
        # 模拟识别结果
        mock_result = {
            'success': True,
            'drug_info': {
                'drug_name': '测试药品',
                'dosage': '一次一片，一日三次',
                'usage': '口服',
                'manufacturer': '测试制药厂',
                'expiry_date': '2025-12-31'
            },
            'ocr_confidence': 95,
            'processing_time': '2024-01-01T12:00:00',
            'validation': {
                'completeness_score': 100,
                'present_fields': ['药品名称', '用法用量', '使用方法', '生产厂家'],
                'missing_fields': [],
                'need_retake': False,
                'is_complete': True
            },
            'voice_guidance': '识别成功。药品名称：测试药品。用法用量：一次一片，一日三次。使用方法：口服。生产厂家：测试制药厂。'
        }
        
        print("返回模拟识别结果")
        return jsonify(mock_result)
        
    except Exception as e:
        print(f"识别过程出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}',
            'error_code': 'INTERNAL_ERROR',
            'voice_guidance': '识别出错，请重试'
        }), 500

if __name__ == '__main__':
    """启动应用"""
    print("正在启动测试服务器...")
    print("服务地址: http://0.0.0.0:5000")
    print("健康检查: http://0.0.0.0:5000/api/health")
    
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

