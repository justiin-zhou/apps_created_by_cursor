"""
测试客户端
用于测试会议助手API的各个功能
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"

# 测试会议内容
TEST_MEETING_CONTENT = """
各位同事大家好，现在开始我们的产品规划会议。

张三：大家好，今天我们主要讨论下一季度的产品路线图。首先，我们收到了很多用户反馈，
希望能够增加移动端的功能。

李四：是的，根据数据分析，60%的用户访问来自移动设备，但我们的移动端体验确实还有
很大提升空间。我建议我们优先开发移动端的核心功能。

王五：我同意。不过我们也需要考虑资源分配的问题。目前团队有10个开发人员，如果全部
投入移动端开发，Web端的维护会受影响。

张三：这是个好问题。我的建议是，分配6个人做移动端开发，4个人继续维护Web端和处理
bug修复。移动端开发预计需要3个月时间。

李四：时间表听起来合理。那关于具体要开发哪些功能呢？

王五：我列了一个清单：1. 用户登录和注册 2. 核心业务功能 3. 消息推送 4. 离线模式。
这些是最基础的。

张三：很好。我们就按这个方向推进。行动项：李四负责移动端架构设计，下周五前完成；
王五负责功能详细说明文档，下周三前完成；我来协调资源和排期。

大家还有其他问题吗？没有的话，我们今天就到这里。

李四：没有了，谢谢。

王五：好的，散会。
"""


def test_health():
    """测试健康检查"""
    print("\n" + "="*50)
    print("测试1: 健康检查")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_transcribe():
    """测试会议转写"""
    print("\n" + "="*50)
    print("测试2: 会议转写")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/transcribe",
        data={
            "text_content": TEST_MEETING_CONTENT,
            "language": "zh"
        }
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"\n原始转写文本长度: {len(result['raw_transcription'])} 字符")
        print(f"\n格式化转写:\n{result['formatted_transcription'][:500]}...")
        return result['formatted_transcription']
    else:
        print(f"错误: {result}")
        return None


def test_summary(transcription):
    """测试会议纪要生成"""
    print("\n" + "="*50)
    print("测试3: 生成会议纪要")
    print("="*50)
    
    if not transcription:
        print("跳过：没有可用的转写文本")
        return None
    
    response = requests.post(
        f"{BASE_URL}/api/summary",
        json={
            "transcription": transcription
        }
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"\n会议纪要:\n{result['summary']}")
        return result['summary']
    else:
        print(f"错误: {result}")
        return None


def test_qa(meeting_content):
    """测试会议问答"""
    print("\n" + "="*50)
    print("测试4: 会议问答")
    print("="*50)
    
    if not meeting_content:
        print("跳过：没有可用的会议内容")
        return
    
    questions = [
        "会议的主要决策是什么？",
        "移动端开发需要多长时间？",
        "李四负责什么任务？"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        
        response = requests.post(
            f"{BASE_URL}/api/qa",
            json={
                "meeting_content": meeting_content,
                "question": question
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"回答: {result['answer']}")
        else:
            print(f"错误: {response.json()}")
        
        print("-" * 50)


def test_full_process():
    """测试完整流程"""
    print("\n" + "="*50)
    print("测试5: 完整流程处理")
    print("="*50)
    
    response = requests.post(
        f"{BASE_URL}/api/process-full",
        data={
            "text_content": TEST_MEETING_CONTENT,
            "language": "zh"
        }
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n转写状态: {result['transcription']['status']}")
        print(f"纪要状态: {result['summary']['status']}")
        print(f"\n会议纪要（前500字）:\n{result['summary']['summary'][:500]}...")
    else:
        print(f"错误: {response.json()}")


def main():
    """运行所有测试"""
    print("""
    ╔══════════════════════════════════════════════╗
    ║        会议助手 API 测试客户端               ║
    ╚══════════════════════════════════════════════╝
    
    测试服务器: {0}
    """.format(BASE_URL))
    
    try:
        # 测试1: 健康检查
        test_health()
        
        # 测试2: 转写
        transcription = test_transcribe()
        
        # 测试3: 生成纪要
        summary = test_summary(transcription)
        
        # 测试4: 问答
        test_qa(transcription)
        
        # 测试5: 完整流程
        test_full_process()
        
        print("\n" + "="*50)
        print("✅ 所有测试完成！")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 错误: 无法连接到服务器 {BASE_URL}")
        print("请确保服务器正在运行: python server.py")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")


if __name__ == "__main__":
    main()

