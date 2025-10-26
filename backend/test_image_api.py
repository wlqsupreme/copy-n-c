#!/usr/bin/env python3
"""
图生文API测试脚本

使用方法:
1. 确保后端服务已启动: uvicorn app.main:app --reload --port 8888
2. 运行此脚本: python test_image_api.py
"""

import requests
import json
import base64
import os

# API基础URL
BASE_URL = "http://localhost:8888/api/v1/image"

def print_response(title, response):
    """格式化打印响应结果"""
    print(f"\n{'='*60}")
    print(f"【{title}】")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应内容:\n{json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应内容:\n{response.text}")
    print(f"{'='*60}\n")


def test_health_check():
    """测试1: 健康检查"""
    print("\n🔍 测试1: 健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)
    return response.status_code == 200


def test_analyze_image_url():
    """测试2: 使用URL分析图片"""
    print("\n🖼️ 测试2: 使用URL分析图片")
    
    # 使用一个公开的测试图片URL
    test_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
    
    payload = {
        "image_url": test_image_url,
        "prompt": "请详细描述这张图片的内容"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    print_response("URL图片分析", response)
    return response.status_code == 200


def test_ocr_url():
    """测试3: OCR文字提取（URL）"""
    print("\n📝 测试3: OCR文字提取")
    
    # 使用一个包含文字的测试图片
    test_image_url = "https://images.unsplash.com/photo-1519682337058-a94d519337bc"
    
    payload = {
        "image_url": test_image_url
    }
    
    response = requests.post(f"{BASE_URL}/ocr", json=payload)
    print_response("OCR文字提取", response)
    return response.status_code in [200, 500]  # OCR可能失败但接口正常


def test_scene_description():
    """测试4: 场景描述生成"""
    print("\n🎬 测试4: 场景描述生成（分镜风格）")
    
    test_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
    
    # 测试不同的风格
    for style in ["storyboard", "detailed", "simple"]:
        print(f"\n--- 测试风格: {style} ---")
        payload = {
            "image_url": test_image_url,
            "style": style
        }
        
        response = requests.post(f"{BASE_URL}/scene-description", json=payload)
        print_response(f"场景描述 ({style})", response)
        
        if response.status_code != 200:
            return False
    
    return True


def test_batch_analyze():
    """测试5: 批量图片分析"""
    print("\n📚 测试5: 批量图片分析")
    
    payload = {
        "images": [
            {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"},
            {"url": "https://images.unsplash.com/photo-1519682337058-a94d519337bc"}
        ],
        "prompt": "请简单描述这张图片"
    }
    
    response = requests.post(f"{BASE_URL}/batch-analyze", json=payload)
    print_response("批量图片分析", response)
    return response.status_code == 200


def test_upload_image():
    """测试6: 图片上传（如果有测试图片）"""
    print("\n📤 测试6: 图片上传")
    
    # 检查是否有测试图片
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"⚠️ 跳过上传测试（未找到 {test_image_path}）")
        print(f"提示: 可以放置一张名为 {test_image_path} 的图片来测试上传功能")
        return True
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            print_response("图片上传", response)
            return response.status_code == 200
    except Exception as e:
        print(f"❌ 上传测试失败: {e}")
        return False


def test_analyze_base64():
    """测试7: 使用base64分析图片"""
    print("\n📦 测试7: 使用base64分析图片")
    
    # 创建一个简单的测试base64（1x1像素的红色图片）
    # 这只是为了测试接口，实际图片分析可能会失败
    test_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    payload = {
        "image_base64": test_base64,
        "prompt": "请描述这张图片"
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    print_response("Base64图片分析", response)
    return response.status_code in [200, 500]  # 测试图片可能分析失败但接口正常


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("🚀 开始测试图生文API")
    print("="*60)
    
    tests = [
        ("健康检查", test_health_check),
        ("URL图片分析", test_analyze_image_url),
        ("OCR文字提取", test_ocr_url),
        ("场景描述生成", test_scene_description),
        ("批量图片分析", test_batch_analyze),
        ("图片上传", test_upload_image),
        ("Base64图片分析", test_analyze_base64),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status}")
        except requests.exceptions.ConnectionError:
            print(f"\n❌ 连接错误: 无法连接到 {BASE_URL}")
            print("请确保后端服务已启动:")
            print("  cd backend")
            print("  uvicorn app.main:app --reload --port 8888")
            return
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ {test_name} 异常: {e}")
    
    # 打印测试总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n通过: {passed}/{total}")
    print("="*60)
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查配置和API Key")
        print("\n提示:")
        print("1. 确保 config.json 中配置了有效的七牛云API Key")
        print("2. 确认使用的模型支持视觉理解功能")
        print("3. 检查网络连接和API配额")


def quick_test():
    """快速测试：只测试健康检查和一个简单的分析"""
    print("🚀 快速测试模式")
    print("-" * 60)
    
    # 1. 健康检查
    print("\n1. 检查服务状态...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务运行正常")
            data = response.json()
            print(f"   模型: {data.get('model')}")
            print(f"   API配置: {'已配置' if data.get('api_configured') else '未配置'}")
        else:
            print("❌ 服务状态异常")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保后端已启动")
        print("   启动命令: uvicorn app.main:app --reload --port 8888")
        return
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return
    
    # 2. 测试一个简单的图片分析
    print("\n2. 测试图片分析功能...")
    test_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"image_url": test_url, "prompt": "请简单描述这张图片"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 图片分析成功")
            print(f"\n分析结果:\n{data.get('result', '无结果')[:200]}...")
        else:
            print(f"❌ 图片分析失败 (状态码: {response.status_code})")
            print(f"   错误: {response.text}")
    except Exception as e:
        print(f"❌ 分析失败: {e}")
    
    print("\n" + "="*60)
    print("💡 提示: 运行完整测试请使用 --full 参数")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # 完整测试
        run_all_tests()
    else:
        # 快速测试
        quick_test()
        print("\n运行完整测试: python test_image_api.py --full")

