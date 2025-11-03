#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的后端测试 - 不依赖flask_cors
"""

from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
import requests
import json
import os
from datetime import datetime
import logging

# 创建Flask应用
app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 百度云OCR配置
BAIDU_OCR_CONFIG = {
    'api_key': 'qLXk73B8ErRa9QuslGZCpSRl',
    'secret_key': 'WU1UYgSrYkFbgCV2io1BBX4SfTW8mu5f',
    'token_url': 'https://aip.baidubce.com/oauth/2.0/token',
    'ocr_url': 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic'
}

# 全局变量存储access_token
baidu_access_token = None
token_expire_time = None

def get_access_token():
    """获取百度云OCR的access_token"""
    global baidu_access_token, token_expire_time

    # 检查token是否过期
    if baidu_access_token and token_expire_time and datetime.now() < token_expire_time:
        return baidu_access_token

    try:
        # 请求获取access_token
        token_url = BAIDU_OCR_CONFIG['token_url']
        params = {
            'grant_type': 'client_credentials',
            'client_id': BAIDU_OCR_CONFIG['api_key'],
            'client_secret': BAIDU_OCR_CONFIG['secret_key']
        }

        response = requests.post(token_url, params=params)
        result = response.json()

        if 'access_token' in result:
            baidu_access_token = result['access_token']
            from datetime import timedelta
            token_expire_time = datetime.now() + timedelta(days=29, hours=23)
            logger.info("百度云OCR token获取成功")
            return baidu_access_token
        else:
            logger.error(f"获取百度云OCR token失败: {result}")
            return None

    except Exception as e:
        logger.error(f"获取百度云OCR token异常: {str(e)}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Drug Recognition API - 简化版',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'message': '服务器运行正常'
    })

@app.route('/api/test', methods=['GET'])
def test_api():
    """测试接口"""
    return jsonify({
        'success': True,
        'message': 'API测试成功',
        'timestamp': datetime.now().isoformat(),
        'python_version': '3.x',
        'flask_version': '2.x'
    })

@app.route('/api/ocr-test', methods=['POST'])
def test_ocr():
    """测试OCR功能"""
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传图片文件'
            }), 400

        image_file = request.files['image']
        
        # 保存临时文件
        temp_dir = 'tmp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        temp_image_path = os.path.join(temp_dir, f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
        image_file.save(temp_image_path)
        
        logger.info(f"图片保存成功: {temp_image_path}")
        
        # 测试图像处理
        img = cv2.imread(temp_image_path)
        if img is not None:
            height, width = img.shape[:2]
            image_info = {
                'width': width,
                'height': height,
                'channels': img.shape[2] if len(img.shape) == 3 else 1,
                'file_size': os.path.getsize(temp_image_path)
            }
        else:
            image_info = {'error': '无法读取图片'}
        
        # 清理临时文件
        try:
            os.remove(temp_image_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': '图像处理测试成功',
            'image_info': image_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"OCR测试异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'测试失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 启动简化版药品识别API服务器...")
    print("📍 访问地址: http://localhost:5000")
    print("🔍 健康检查: http://localhost:5000/api/health")
    print("🧪 测试接口: http://localhost:5000/api/test")
    print("📷 OCR测试: POST http://localhost:5000/api/ocr-test")
    print("按 Ctrl+C 停止服务器")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")













