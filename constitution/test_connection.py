"""
测试后端连接
"""

import requests
import json

def test_connection():
    """测试后端连接"""
    try:
        # 测试健康检查接口
        print("测试健康检查接口...")
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 测试识别接口（模拟）
        print("\n测试识别接口...")
        test_data = {'test': 'data'}
        response = requests.post('http://127.0.0.1:5000/api/recognize', 
                                data=test_data, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：无法连接到后端服务")
        print("请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == '__main__':
    test_connection()


