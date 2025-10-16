"""
情绪识别系统使用示例
"""
import asyncio
from crew.emotion_crew import EmotionDetectionCrew
from models import EmotionDetectRequest

def example_text_only():
    """示例1: 仅文本情绪识别"""
    print("\n" + "="*50)
    print("示例1: 文本情绪识别")
    print("="*50 + "\n")
    
    # 创建Crew实例
    crew = EmotionDetectionCrew()
    
    # 创建请求
    request = EmotionDetectRequest(
        text="今天真的太开心了！工作进展顺利，还收到了好消息，感觉一切都很美好！",
        conversation_history=[]
    )
    
    # 执行分析
    print("正在分析情绪...")
    result = crew.analyze_emotion(request)
    
    # 打印结果
    print(f"\n✅ 分析成功: {result.success}")
    print(f"🎯 主要情绪: {result.primary_emotion}")
    print(f"\n📊 识别出的情绪:")
    for emotion in result.emotions:
        print(f"  - {emotion.emotion} (置信度: {emotion.confidence:.2%})")
        print(f"    理由: {emotion.reason}")
    print(f"\n💭 综合分析:\n{result.analysis}")
    print(f"\n⏰ 时间: {result.timestamp}")

def example_with_history():
    """示例2: 带对话历史的情绪识别"""
    print("\n" + "="*50)
    print("示例2: 结合对话历史的情绪识别")
    print("="*50 + "\n")
    
    # 创建Crew实例
    crew = EmotionDetectionCrew()
    
    # 创建带历史的请求
    request = EmotionDetectRequest(
        text="但是现在我又有点担心...",
        conversation_history=[
            {"role": "user", "content": "我今天升职了！"},
            {"role": "assistant", "content": "恭喜你！这是个好消息！"},
            {"role": "user", "content": "是啊，我很开心"},
        ]
    )
    
    # 执行分析
    print("正在分析情绪（考虑对话历史）...")
    result = crew.analyze_emotion(request)
    
    # 打印结果
    print(f"\n✅ 分析成功: {result.success}")
    print(f"🎯 主要情绪: {result.primary_emotion}")
    print(f"\n📊 识别出的情绪:")
    for emotion in result.emotions:
        print(f"  - {emotion.emotion} (置信度: {emotion.confidence:.2%})")
        print(f"    理由: {emotion.reason}")
    print(f"\n💭 综合分析:\n{result.analysis}")

def example_negative_emotion():
    """示例3: 负面情绪识别"""
    print("\n" + "="*50)
    print("示例3: 负面情绪识别")
    print("="*50 + "\n")
    
    # 创建Crew实例
    crew = EmotionDetectionCrew()
    
    # 创建请求
    request = EmotionDetectRequest(
        text="真的很生气！为什么总是这样对我？我受够了这种不公平的对待！",
        conversation_history=[]
    )
    
    # 执行分析
    print("正在分析情绪...")
    result = crew.analyze_emotion(request)
    
    # 打印结果
    print(f"\n✅ 分析成功: {result.success}")
    print(f"🎯 主要情绪: {result.primary_emotion}")
    print(f"\n📊 识别出的情绪:")
    for emotion in result.emotions:
        print(f"  - {emotion.emotion} (置信度: {emotion.confidence:.2%})")
        print(f"    理由: {emotion.reason}")
    print(f"\n💭 综合分析:\n{result.analysis}")

def example_mixed_emotions():
    """示例4: 混合情绪识别"""
    print("\n" + "="*50)
    print("示例4: 混合情绪识别")
    print("="*50 + "\n")
    
    # 创建Crew实例
    crew = EmotionDetectionCrew()
    
    # 创建请求
    request = EmotionDetectRequest(
        text="虽然很难过失去了这个机会，但我也为自己的努力感到骄傲。我知道未来还会有更多机会，只是现在心里有点失落。",
        conversation_history=[]
    )
    
    # 执行分析
    print("正在分析情绪...")
    result = crew.analyze_emotion(request)
    
    # 打印结果
    print(f"\n✅ 分析成功: {result.success}")
    print(f"🎯 主要情绪: {result.primary_emotion}")
    print(f"\n📊 识别出的情绪:")
    for emotion in result.emotions:
        print(f"  - {emotion.emotion} (置信度: {emotion.confidence:.2%})")
        print(f"    理由: {emotion.reason}")
    print(f"\n💭 综合分析:\n{result.analysis}")

def main():
    """运行所有示例"""
    print("\n" + "🎭"*25)
    print("智能情绪识别系统 - 使用示例")
    print("🎭"*25)
    
    try:
        # 检查配置
        from config import Config
        Config.validate()
        print("\n✅ 配置验证通过\n")
        
        # 运行示例
        examples = [
            ("示例1: 文本情绪识别", example_text_only),
            ("示例2: 结合对话历史", example_with_history),
            ("示例3: 负面情绪识别", example_negative_emotion),
            ("示例4: 混合情绪识别", example_mixed_emotions),
        ]
        
        for i, (name, func) in enumerate(examples, 1):
            print(f"\n{'='*60}")
            print(f"运行 {name}")
            print(f"{'='*60}")
            
            try:
                func()
            except Exception as e:
                print(f"\n❌ 示例{i}执行失败: {e}")
                import traceback
                traceback.print_exc()
            
            if i < len(examples):
                input("\n按Enter键继续下一个示例...")
        
        print("\n" + "="*60)
        print("✅ 所有示例运行完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

