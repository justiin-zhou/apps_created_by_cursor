"""
使用示例
演示如何使用会议助手API
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"


def example_1_text_transcription():
    """
    示例1: 使用文本进行转写
    适用场景: 已有会议文字记录，需要格式化和优化
    """
    print("\n" + "="*60)
    print("示例 1: 文本转写")
    print("="*60)
    
    meeting_text = """
    今天的团队会议主要讨论了三个议题。
    
    首先是关于新产品的开发进度，张经理报告说目前完成了70%，
    预计下个月底可以上线。
    
    其次，市场部李总提出了新的营销方案，建议增加社交媒体投放预算。
    大家讨论后决定先进行小规模测试。
    
    最后确定了下次会议时间为下周三下午3点。
    """
    
    response = requests.post(
        f"{BASE_URL}/api/transcribe",
        data={
            "text_content": meeting_text,
            "language": "zh"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 转写成功！")
        print(f"\n格式化后的内容:\n{result['formatted_transcription']}")
        return result['formatted_transcription']
    else:
        print(f"❌ 转写失败: {response.json()}")
        return None


def example_2_generate_summary(transcription):
    """
    示例2: 生成会议纪要
    """
    print("\n" + "="*60)
    print("示例 2: 生成会议纪要")
    print("="*60)
    
    if not transcription:
        print("跳过：没有转写内容")
        return None
    
    response = requests.post(
        f"{BASE_URL}/api/summary",
        json={"transcription": transcription}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 纪要生成成功！")
        print(f"\n会议纪要:\n{result['summary']}")
        return result['summary']
    else:
        print(f"❌ 纪要生成失败: {response.json()}")
        return None


def example_3_qa(meeting_content):
    """
    示例3: 会议内容问答
    """
    print("\n" + "="*60)
    print("示例 3: 会议内容问答")
    print("="*60)
    
    if not meeting_content:
        print("跳过：没有会议内容")
        return
    
    questions = [
        "会议讨论了哪些主要议题？",
        "新产品的开发进度如何？",
        "下次会议什么时候？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        
        response = requests.post(
            f"{BASE_URL}/api/qa",
            json={
                "meeting_content": meeting_content,
                "question": question
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"回答: {result['answer']}\n")
        else:
            print(f"❌ 问答失败: {response.json()}\n")


def example_4_full_process():
    """
    示例4: 完整流程处理（转写 + 纪要）
    """
    print("\n" + "="*60)
    print("示例 4: 完整流程处理")
    print("="*60)
    
    meeting_text = """
    产品评审会议记录
    
    时间：2024年1月15日 14:00
    参会人：产品经理王磊、技术负责人李娜、设计师张萌
    
    王磊：大家好，今天我们评审用户反馈系统的设计方案。
    
    张萌：我已经准备好了原型图，主要包括三个模块：反馈提交、
    反馈查看、反馈统计。界面采用简洁风格，符合我们的品牌调性。
    
    李娜：从技术角度看，这个方案可行。我建议使用微服务架构，
    便于后期扩展。开发周期大约需要两周。
    
    王磊：很好。那我们确定下来，李娜下周一开始开发，张萌继续
    优化细节交互。目标是本月底完成并上线。
    
    李娜：没问题。
    
    张萌：收到。
    
    王磊：今天就到这里，散会。
    """
    
    response = requests.post(
        f"{BASE_URL}/api/process-full",
        data={
            "text_content": meeting_text,
            "language": "zh"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 完整处理成功！")
        print(f"\n📝 转写状态: {result['transcription']['status']}")
        print(f"📋 纪要状态: {result['summary']['status']}")
        print(f"\n会议纪要:\n{result['summary']['summary']}")
    else:
        print(f"❌ 处理失败: {response.json()}")


def example_5_audio_transcription():
    """
    示例5: 音频文件转写（需要实际音频文件）
    """
    print("\n" + "="*60)
    print("示例 5: 音频文件转写")
    print("="*60)
    
    # 注意：需要替换为实际的音频文件路径
    audio_file_path = "meeting.mp3"
    
    print(f"尝试上传音频文件: {audio_file_path}")
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = requests.post(
                f"{BASE_URL}/api/transcribe",
                files={"audio_file": audio_file},
                data={"language": "zh"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ 音频转写成功！")
                print(f"\n转写文本:\n{result['formatted_transcription']}")
            else:
                print(f"❌ 转写失败: {response.json()}")
    except FileNotFoundError:
        print(f"⚠️  未找到音频文件: {audio_file_path}")
        print("   提示: 请将音频文件放在当前目录，或修改文件路径")


def main():
    """
    运行所有示例
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║              会议助手 API 使用示例                        ║
    ╚══════════════════════════════════════════════════════════╝
    
    本脚本演示如何使用会议助手API的各项功能
    
    前提条件:
    1. 服务器正在运行 (python server.py)
    2. 已配置 .env 文件中的 OPENAI_API_KEY
    """)
    
    try:
        # 检查服务器是否运行
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✓ 服务器状态: {response.json()['status']}\n")
        
        # 运行示例
        transcription = example_1_text_transcription()
        summary = example_2_generate_summary(transcription)
        example_3_qa(transcription)
        example_4_full_process()
        # example_5_audio_transcription()  # 需要音频文件，默认注释
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成！")
        print("="*60)
        print("""
提示：
- 查看 README.md 了解更多使用方法
- 访问 http://localhost:8000/docs 查看完整API文档
- 运行 python test_client.py 进行功能测试
        """)
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 错误: 无法连接到服务器 {BASE_URL}")
        print("\n请先启动服务器:")
        print("   python server.py")
        print("\n或者:")
        print("   bash start.sh")
    except Exception as e:
        print(f"\n❌ 运行出错: {str(e)}")


if __name__ == "__main__":
    main()

