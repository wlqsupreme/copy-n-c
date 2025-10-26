#!/usr/bin/env python3
"""
文生图API测试脚本

使用方法:
1. 确保后端服务已启动: uvicorn app.main:app --reload --port 8888
2. 运行此脚本: python test_text_to_image.py
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8888/api/v1/text-to-image"

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


def test_get_options():
    """测试2: 获取生成选项"""
    print("\n⚙️ 测试2: 获取生成选项")
    response = requests.get(f"{BASE_URL}/options")
    print_response("生成选项", response)
    return response.status_code == 200


def test_get_examples():
    """测试3: 获取提示词示例"""
    print("\n💡 测试3: 获取提示词示例")
    response = requests.get(f"{BASE_URL}/examples")
    print_response("提示词示例", response)
    return response.status_code == 200


def test_generate_single_image():
    """测试4: 生成单张图片"""
    print("\n🎨 测试4: 生成单张图片")
    
    payload = {
        "prompt": "一只可爱的橘猫坐在窗台上，阳光洒在它身上，温暖的画面，高质量插图",
        "size": "1024x1024",
        "quality": "standard",
        "style": "vivid"
    }
    
    print(f"📝 提示词: {payload['prompt']}")
    print(f"⏳ 生成中，请稍候（可能需要10-30秒）...")
    
    try:
        response = requests.post(f"{BASE_URL}/generate", json=payload, timeout=120)
        print_response("单张图片生成", response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('image', {}).get('url'):
                print(f"🖼️ 图片URL: {data['image']['url']}")
                print(f"✨ 优化后的提示词: {data['image'].get('revised_prompt', '无')}")
                return True
        return False
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，生成图片可能需要更长时间")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_generate_multiple_images():
    """测试5: 生成多张图片"""
    print("\n🎨 测试5: 生成多张图片（2张）")
    
    payload = {
        "prompt": "科幻城市夜景，霓虹灯闪烁，未来感十足",
        "n": 2,
        "size": "512x512",  # 使用小尺寸加快速度
        "quality": "standard",
        "style": "vivid"
    }
    
    print(f"📝 提示词: {payload['prompt']}")
    print(f"🔢 数量: {payload['n']} 张")
    print(f"⏳ 生成中，请稍候（可能需要20-60秒）...")
    
    try:
        response = requests.post(f"{BASE_URL}/generate-multiple", json=payload, timeout=180)
        print_response("多张图片生成", response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('images'):
                print(f"✅ 成功生成 {len(data['images'])} 张图片:")
                for i, img in enumerate(data['images'], 1):
                    print(f"   {i}. {img.get('url')}")
                return True
        return False
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，生成多张图片需要较长时间")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_storyboard_images():
    """测试6: 分镜配图生成"""
    print("\n🎬 测试6: 分镜配图生成")
    
    payload = {
        "scenes": [
            {"index": 1, "description": "清晨的城市街道，阳光透过高楼"},
            {"index": 2, "description": "主角走进咖啡店，温馨的氛围"}
        ],
        "size": "512x512",  # 使用小尺寸加快速度
        "style": "vivid"
    }
    
    print(f"🎞️ 场景数量: {len(payload['scenes'])}")
    print(f"⏳ 生成中，请稍候（可能需要30-90秒）...")
    
    try:
        response = requests.post(f"{BASE_URL}/storyboard", json=payload, timeout=180)
        print_response("分镜配图生成", response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('storyboard'):
                print(f"✅ 分镜配图完成，成功: {data['success_count']}/{data['total']}")
                for scene in data['storyboard']:
                    status = "✅" if scene.get('url') else "❌"
                    print(f"   {status} 场景 {scene['index']}: {scene.get('url', '失败')}")
                return True
        return False
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，生成分镜配图需要较长时间")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("🚀 开始测试文生图API")
    print("="*60)
    
    tests = [
        ("健康检查", test_health_check),
        ("获取生成选项", test_get_options),
        ("获取提示词示例", test_get_examples),
        ("生成单张图片", test_generate_single_image),
        ("生成多张图片", test_generate_multiple_images),
        ("分镜配图生成", test_storyboard_images),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"开始测试: {test_name}")
            print('='*60)
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
        print("⚠️ 部分测试失败")
        print("\n💡 提示:")
        print("1. 确保 config.json 中配置了有效的七牛云API Key")
        print("2. 确认使用的模型支持文生图功能")
        print("3. 图片生成需要较长时间，请耐心等待")
        print("4. 检查网络连接和API配额")


def quick_test():
    """快速测试：只测试健康检查和获取选项"""
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
            print(f"   主接入点: {data.get('api_base')}")
            print(f"   备接入点: {data.get('backup_api_base')}")
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
    
    # 2. 获取选项
    print("\n2. 获取生成选项...")
    try:
        response = requests.get(f"{BASE_URL}/options", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取选项")
            print(f"   支持的尺寸: {', '.join(data['options']['sizes'])}")
            print(f"   支持的风格: {', '.join(data['options']['styles'])}")
            print(f"   支持的质量: {', '.join(data['options']['qualities'])}")
        else:
            print("❌ 获取选项失败")
    except Exception as e:
        print(f"❌ 获取选项失败: {e}")
    
    # 3. 获取示例
    print("\n3. 获取提示词示例...")
    try:
        response = requests.get(f"{BASE_URL}/examples", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功获取示例")
            print("\n📝 示例提示词（人物类）:")
            for example in data['examples']['人物'][:2]:
                print(f"   • {example}")
        else:
            print("❌ 获取示例失败")
    except Exception as e:
        print(f"❌ 获取示例失败: {e}")
    
    print("\n" + "="*60)
    print("💡 提示:")
    print("  • 运行完整测试（包括图片生成）: python test_text_to_image.py --full")
    print("  • 图片生成需要10-30秒，完整测试需要2-5分钟")
    print("  • 在浏览器中测试: 打开 backend/test_text_to_image_ui.html")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # 完整测试（包括图片生成）
        print("\n⚠️ 注意: 完整测试包括图片生成，可能需要2-5分钟")
        input("按Enter键继续，或Ctrl+C取消...")
        run_all_tests()
    else:
        # 快速测试（不生成图片）
        quick_test()

