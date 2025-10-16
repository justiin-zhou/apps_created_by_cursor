// API 基础 URL
const API_BASE_URL = 'http://localhost:8000';

// ==================== 工具函数 ====================

// 显示 Loading
function showLoading(text = '处理中...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    loadingText.textContent = text;
    overlay.classList.add('show');
}

// 隐藏 Loading
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('show');
}

// 显示 Toast 通知
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 复制到剪贴板
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('已复制到剪贴板', 'success');
    }).catch(() => {
        showToast('复制失败', 'error');
    });
}

// 下载文本文件
function downloadText(elementId, filename) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    showToast('文件已下载', 'success');
}

// ==================== 标签页切换 ====================

// 初始化标签页
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        // 移除所有 active 类
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // 添加 active 类
        button.classList.add('active');
        const tabId = button.dataset.tab;
        document.getElementById(`${tabId}-tab`).classList.add('active');
    });
});

// 结果标签页切换
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('result-tab')) {
        const parent = e.target.closest('.result-section');
        parent.querySelectorAll('.result-tab').forEach(tab => tab.classList.remove('active'));
        parent.querySelectorAll('.result-tab-content').forEach(content => content.classList.remove('active'));
        
        e.target.classList.add('active');
        const resultId = e.target.dataset.result;
        parent.querySelector(`#result-${resultId}`).classList.add('active');
    }
});

// ==================== 文件上传 ====================

// 设置拖放上传
function setupDragDrop(areaId, inputId) {
    const area = document.getElementById(areaId);
    const input = document.getElementById(inputId);
    
    if (!area) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, () => {
            area.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, () => {
            area.classList.remove('drag-over');
        });
    });
    
    area.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            showToast(`已选择文件: ${files[0].name}`, 'success');
        }
    });
}

setupDragDrop('upload-area', 'audio-file');
setupDragDrop('upload-area-full', 'audio-file-full');

// 文件选择提示
document.getElementById('audio-file')?.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        showToast(`已选择文件: ${e.target.files[0].name}`, 'success');
    }
});

document.getElementById('audio-file-full')?.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        showToast(`已选择文件: ${e.target.files[0].name}`, 'success');
    }
});

// ==================== API 调用 ====================

// 1. 会议转写
document.getElementById('transcribe-btn')?.addEventListener('click', async () => {
    const audioFile = document.getElementById('audio-file').files[0];
    const meetingText = document.getElementById('meeting-text').value.trim();
    
    if (!audioFile && !meetingText) {
        showToast('请上传音频文件或输入文本', 'error');
        return;
    }
    
    const formData = new FormData();
    if (audioFile) {
        formData.append('audio_file', audioFile);
    }
    if (meetingText) {
        formData.append('text_content', meetingText);
    }
    formData.append('language', 'zh');
    
    try {
        showLoading('正在转写会议内容...');
        const response = await fetch(`${API_BASE_URL}/api/transcribe`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('转写失败');
        }
        
        const result = await response.json();
        
        // 显示结果
        document.getElementById('transcribe-output').textContent = result.formatted_transcription;
        document.getElementById('transcribe-result').style.display = 'block';
        
        // 滚动到结果
        document.getElementById('transcribe-result').scrollIntoView({ behavior: 'smooth' });
        
        showToast('转写完成！', 'success');
    } catch (error) {
        showToast(`转写失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// 2. 生成纪要
document.getElementById('summary-btn')?.addEventListener('click', async () => {
    const transcription = document.getElementById('summary-text').value.trim();
    
    if (!transcription) {
        showToast('请输入会议转写内容', 'error');
        return;
    }
    
    try {
        showLoading('正在生成会议纪要...');
        const response = await fetch(`${API_BASE_URL}/api/summary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ transcription })
        });
        
        if (!response.ok) {
            throw new Error('生成纪要失败');
        }
        
        const result = await response.json();
        
        // 显示结果
        document.getElementById('summary-output').innerHTML = formatMarkdown(result.summary);
        document.getElementById('summary-result').style.display = 'block';
        
        // 滚动到结果
        document.getElementById('summary-result').scrollIntoView({ behavior: 'smooth' });
        
        showToast('纪要生成完成！', 'success');
    } catch (error) {
        showToast(`生成纪要失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// 3. 智能问答
async function askQuestion() {
    const meetingContent = document.getElementById('qa-context').value.trim();
    const question = document.getElementById('question-input').value.trim();
    
    if (!meetingContent) {
        showToast('请先输入会议内容', 'error');
        return;
    }
    
    if (!question) {
        showToast('请输入问题', 'error');
        return;
    }
    
    // 添加问题消息
    addMessage(question, 'question');
    document.getElementById('question-input').value = '';
    
    try {
        showLoading('AI 正在思考...');
        const response = await fetch(`${API_BASE_URL}/api/qa`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                meeting_content: meetingContent,
                question: question
            })
        });
        
        if (!response.ok) {
            throw new Error('问答失败');
        }
        
        const result = await response.json();
        
        // 添加回答消息
        addMessage(result.answer, 'answer');
    } catch (error) {
        addMessage(`抱歉，出现错误: ${error.message}`, 'answer');
    } finally {
        hideLoading();
    }
}

// 添加聊天消息
function addMessage(text, type) {
    const chatMessages = document.getElementById('chat-messages');
    
    // 移除欢迎消息
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = text;
    
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 设置快速提问
function setQuestion(question) {
    document.getElementById('question-input').value = question;
    document.getElementById('question-input').focus();
}

// 4. 完整流程处理
document.getElementById('full-process-btn')?.addEventListener('click', async () => {
    const audioFile = document.getElementById('audio-file-full').files[0];
    const meetingText = document.getElementById('full-text').value.trim();
    
    if (!audioFile && !meetingText) {
        showToast('请上传音频文件或输入文本', 'error');
        return;
    }
    
    const formData = new FormData();
    if (audioFile) {
        formData.append('audio_file', audioFile);
    }
    if (meetingText) {
        formData.append('text_content', meetingText);
    }
    formData.append('language', 'zh');
    
    try {
        showLoading('正在处理会议（转写 + 纪要）...');
        const response = await fetch(`${API_BASE_URL}/api/process-full`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('处理失败');
        }
        
        const result = await response.json();
        
        // 显示转写结果
        document.getElementById('full-transcribe-output').textContent = 
            result.transcription.formatted_transcription;
        
        // 显示纪要结果
        document.getElementById('full-summary-output').innerHTML = 
            formatMarkdown(result.summary.summary);
        
        document.getElementById('full-result').style.display = 'block';
        
        // 滚动到结果
        document.getElementById('full-result').scrollIntoView({ behavior: 'smooth' });
        
        showToast('处理完成！', 'success');
    } catch (error) {
        showToast(`处理失败: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// ==================== 辅助函数 ====================

// 将转写结果用于纪要
function useForSummary() {
    const transcription = document.getElementById('transcribe-output').textContent;
    document.getElementById('summary-text').value = transcription;
    
    // 切换到纪要标签
    document.querySelectorAll('.tab-button')[1].click();
    
    showToast('已导入转写内容到纪要生成', 'success');
}

// 下载完整结果
function downloadFullResults() {
    const transcription = document.getElementById('full-transcribe-output').textContent;
    const summary = document.getElementById('full-summary-output').textContent;
    
    const content = `会议转写\n${'='.repeat(50)}\n\n${transcription}\n\n\n会议纪要\n${'='.repeat(50)}\n\n${summary}`;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'meeting-complete-results.txt';
    a.click();
    URL.revokeObjectURL(url);
    
    showToast('完整结果已下载', 'success');
}

// 简单的 Markdown 格式化
function formatMarkdown(text) {
    return text
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/^(\d+)\. (.*$)/gim, '<li>$2</li>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^(.+)$/gim, '<p>$1</p>')
        .replace(/<\/li>\s*<p>/g, '</li>')
        .replace(/<\/p>\s*<li>/g, '<li>');
}

// ==================== 页面加载完成 ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('会议助手前端已加载');
    
    // 检查服务器连接
    fetch(`${API_BASE_URL}/health`)
        .then(response => response.json())
        .then(data => {
            console.log('服务器连接正常:', data);
        })
        .catch(error => {
            console.error('无法连接到服务器:', error);
            showToast('警告：无法连接到服务器，请确保后端服务正在运行', 'error');
        });
});

// ==================== 导航滚动 ====================

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        }
        
        // 更新导航激活状态
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
    });
});

