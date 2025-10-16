// 全局状态
const state = {
    uploadedFile: null,
    conversationHistory: [],
    isAnalyzing: false,
    // 录音相关
    mediaRecorder: null,
    audioChunks: [],
    recordingStartTime: null,
    recordingTimer: null,
    stream: null
};

// DOM元素
const elements = {
    textInput: document.getElementById('textInput'),
    audioInput: document.getElementById('audioInput'),
    uploadArea: document.getElementById('uploadArea'),
    fileInfo: document.getElementById('fileInfo'),
    fileName: document.getElementById('fileName'),
    removeFile: document.getElementById('removeFile'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    loading: document.getElementById('loading'),
    resultContent: document.getElementById('resultContent'),
    emptyState: document.getElementById('emptyState'),
    primaryEmotion: document.getElementById('primaryEmotion'),
    emotionsList: document.getElementById('emotionsList'),
    analysisText: document.getElementById('analysisText'),
    timestamp: document.getElementById('timestamp'),
    conversationHistory: document.getElementById('conversationHistory'),
    clearHistory: document.getElementById('clearHistory'),
    toast: document.getElementById('toast'),
    // 录音相关
    recordBtn: document.getElementById('recordBtn'),
    stopRecordBtn: document.getElementById('stopRecordBtn'),
    recordingInfo: document.getElementById('recordingInfo'),
    recordingTime: document.getElementById('recordingTime')
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadConversationHistory();
    checkHealth();
    checkRecordingSupport();
});

// 初始化事件监听
function initEventListeners() {
    // 录音按钮
    elements.recordBtn.addEventListener('click', startRecording);
    elements.stopRecordBtn.addEventListener('click', stopRecording);
    
    // 文件上传
    elements.uploadArea.addEventListener('click', () => {
        elements.audioInput.click();
    });
    
    elements.audioInput.addEventListener('change', handleFileSelect);
    
    // 拖拽上传
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    
    // 移除文件
    elements.removeFile.addEventListener('click', (e) => {
        e.stopPropagation();
        removeFile();
    });
    
    // 分析按钮
    elements.analyzeBtn.addEventListener('click', analyzeEmotion);
    
    // 清空历史
    elements.clearHistory.addEventListener('click', clearHistory);
}

// 健康检查
async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        console.log('服务器状态:', data);
    } catch (error) {
        console.error('服务器连接失败:', error);
        showToast('服务器连接失败，请检查后端服务', 'error');
    }
}

// ==================== 录音功能 ====================

// 检查录音功能支持
function checkRecordingSupport() {
    console.log('=== 录音功能诊断 ===');
    console.log('浏览器:', navigator.userAgent);
    console.log('协议:', location.protocol);
    console.log('主机:', location.hostname);
    console.log('端口:', location.port);
    console.log('完整URL:', location.href);
    console.log('navigator.mediaDevices:', navigator.mediaDevices);
    console.log('navigator.mediaDevices.getUserMedia:', navigator.mediaDevices?.getUserMedia);
    
    if (!navigator.mediaDevices) {
        console.error('❌ navigator.mediaDevices 不存在');
        elements.recordBtn.disabled = true;
        elements.recordBtn.querySelector('.record-text').textContent = '浏览器不支持录音';
        elements.recordBtn.style.opacity = '0.5';
        elements.recordBtn.style.cursor = 'not-allowed';
    } else if (!navigator.mediaDevices.getUserMedia) {
        console.error('❌ getUserMedia 不存在');
        elements.recordBtn.disabled = true;
        elements.recordBtn.querySelector('.record-text').textContent = '浏览器不支持录音';
    } else {
        console.log('✅ 录音功能可用');
    }
    
    // 检查是否为安全上下文
    if (window.isSecureContext) {
        console.log('✅ 安全上下文 (HTTPS 或 localhost)');
    } else {
        console.warn('⚠️ 非安全上下文，录音功能可能受限');
    }
    
    console.log('==================');
}

// 开始录音
async function startRecording() {
    try {
        // 检查浏览器支持
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showToast('您的浏览器不支持录音功能，请使用最新版 Chrome、Firefox 或 Edge', 'error');
            console.error('MediaDevices API not supported');
            return;
        }

        // 检查是否为安全上下文
        if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            showToast('录音功能需要 HTTPS 或在 localhost 使用', 'error');
            console.error('Not in secure context:', location.protocol, location.hostname);
            return;
        }
        
        // 请求麦克风权限
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,  // 回声消除
                noiseSuppression: true,  // 降噪
                sampleRate: 44100        // 采样率
            } 
        });
        
        state.stream = stream;
        state.audioChunks = [];
        
        // 创建 MediaRecorder
        const options = {
            mimeType: 'audio/webm;codecs=opus'
        };
        
        // 检查浏览器支持
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'audio/webm';
        }
        
        state.mediaRecorder = new MediaRecorder(stream, options);
        
        // 数据可用时收集
        state.mediaRecorder.addEventListener('dataavailable', event => {
            if (event.data.size > 0) {
                state.audioChunks.push(event.data);
            }
        });
        
        // 录音停止时处理
        state.mediaRecorder.addEventListener('stop', handleRecordingStop);
        
        // 开始录音
        state.mediaRecorder.start();
        
        // 更新UI
        elements.recordBtn.classList.add('recording');
        elements.recordBtn.querySelector('.record-text').textContent = '录音中...';
        elements.recordingInfo.style.display = 'block';
        
        // 开始计时
        state.recordingStartTime = Date.now();
        updateRecordingTime();
        state.recordingTimer = setInterval(updateRecordingTime, 100);
        
        showToast('开始录音', 'success');
        
    } catch (error) {
        console.error('录音失败:', error);
        if (error.name === 'NotAllowedError') {
            showToast('请允许使用麦克风权限', 'error');
        } else if (error.name === 'NotFoundError') {
            showToast('未找到麦克风设备', 'error');
        } else {
            showToast('录音启动失败: ' + error.message, 'error');
        }
    }
}

// 停止录音
function stopRecording() {
    if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
        state.mediaRecorder.stop();
        
        // 停止所有音轨
        if (state.stream) {
            state.stream.getTracks().forEach(track => track.stop());
        }
        
        // 清除计时器
        if (state.recordingTimer) {
            clearInterval(state.recordingTimer);
            state.recordingTimer = null;
        }
        
        // 更新UI
        elements.recordBtn.classList.remove('recording');
        elements.recordBtn.querySelector('.record-text').textContent = '点击开始录音';
        elements.recordingInfo.style.display = 'none';
        
        showToast('录音已停止', 'success');
    }
}

// 更新录音时间显示
function updateRecordingTime() {
    if (!state.recordingStartTime) return;
    
    const elapsed = Date.now() - state.recordingStartTime;
    const seconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    
    elements.recordingTime.textContent = 
        `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// 处理录音停止
async function handleRecordingStop() {
    if (state.audioChunks.length === 0) {
        showToast('录音数据为空', 'error');
        return;
    }
    
    // 创建音频 Blob
    const audioBlob = new Blob(state.audioChunks, { type: 'audio/webm' });
    
    // 转换为 WAV 格式（更通用）
    try {
        showToast('正在处理录音...', 'warning');
        
        // 创建 File 对象
        const audioFile = new File([audioBlob], `recording_${Date.now()}.webm`, {
            type: 'audio/webm'
        });
        
        // 上传录音文件
        await uploadRecordedAudio(audioFile);
        
    } catch (error) {
        console.error('处理录音失败:', error);
        showToast('处理录音失败: ' + error.message, 'error');
    }
}

// 上传录音文件
async function uploadRecordedAudio(audioFile) {
    try {
        const formData = new FormData();
        formData.append('file', audioFile);
        
        showToast('正在上传录音...', 'warning');
        
        const response = await fetch('/api/upload_audio', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('录音上传失败');
        }
        
        const data = await response.json();
        state.uploadedFile = data.file_path;
        
        // 显示文件信息
        elements.fileName.textContent = `录音文件 (${formatFileSize(data.file_size)})`;
        elements.fileInfo.style.display = 'flex';
        elements.uploadArea.querySelector('.upload-content').style.display = 'none';
        
        showToast('录音上传成功！', 'success');
        console.log('录音上传成功:', data);
        
    } catch (error) {
        console.error('上传录音失败:', error);
        showToast('录音上传失败: ' + error.message, 'error');
    }
}

// 文件选择处理
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        validateAndUploadFile(file);
    }
}

// 拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    elements.uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file) {
        validateAndUploadFile(file);
    }
}

// 验证并上传文件
async function validateAndUploadFile(file) {
    // 检查文件类型
    const allowedTypes = ['.mp3', '.wav', '.m4a', '.ogg', '.flac'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
        showToast('不支持的文件格式，请上传音频文件', 'error');
        return;
    }
    
    // 检查文件大小 (50MB)
    if (file.size > 50 * 1024 * 1024) {
        showToast('文件过大，最大支持50MB', 'error');
        return;
    }
    
    // 显示文件信息
    elements.fileName.textContent = file.name;
    elements.fileInfo.style.display = 'flex';
    elements.uploadArea.querySelector('.upload-content').style.display = 'none';
    
    // 上传文件
    try {
        showToast('正在上传文件...', 'warning');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload_audio', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('文件上传失败');
        }
        
        const data = await response.json();
        state.uploadedFile = data.file_path;
        
        showToast('文件上传成功！', 'success');
        console.log('上传成功:', data);
        
    } catch (error) {
        console.error('上传失败:', error);
        showToast('文件上传失败: ' + error.message, 'error');
        removeFile();
    }
}

// 移除文件
function removeFile() {
    state.uploadedFile = null;
    elements.audioInput.value = '';
    elements.fileInfo.style.display = 'none';
    elements.uploadArea.querySelector('.upload-content').style.display = 'block';
}

// 分析情绪
async function analyzeEmotion() {
    // 验证输入
    const text = elements.textInput.value.trim();
    const audioUrl = state.uploadedFile;
    
    if (!text && !audioUrl) {
        showToast('请输入文本或上传音频', 'warning');
        return;
    }
    
    if (state.isAnalyzing) {
        return;
    }
    
    // 设置加载状态
    state.isAnalyzing = true;
    elements.analyzeBtn.disabled = true;
    elements.loading.style.display = 'flex';
    elements.resultContent.style.display = 'none';
    elements.emptyState.style.display = 'none';
    
    try {
        // 构建请求
        const requestData = {
            text: text || null,
            audio_url: audioUrl || null,
            conversation_history: state.conversationHistory
        };
        
        console.log('发送请求:', requestData);
        
        // 发送请求
        const response = await fetch('/api/emotion_detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '分析失败');
        }
        
        const result = await response.json();
        console.log('分析结果:', result);
        
        // 显示结果
        displayResult(result);
        
        // 更新对话历史
        if (text) {
            addToHistory('user', text);
            addToHistory('assistant', `识别到主要情绪: ${result.primary_emotion}`);
        }
        
        showToast('分析完成！', 'success');
        
    } catch (error) {
        console.error('分析失败:', error);
        showToast('分析失败: ' + error.message, 'error');
        elements.emptyState.style.display = 'flex';
    } finally {
        state.isAnalyzing = false;
        elements.analyzeBtn.disabled = false;
        elements.loading.style.display = 'none';
    }
}

// 显示结果
function displayResult(result) {
    // 主要情绪
    elements.primaryEmotion.textContent = result.primary_emotion;
    
    // 情绪列表
    elements.emotionsList.innerHTML = '';
    result.emotions.forEach(emotion => {
        const item = document.createElement('div');
        item.className = 'emotion-item';
        item.innerHTML = `
            <div class="emotion-header">
                <span class="emotion-name">${emotion.emotion}</span>
                <span class="emotion-confidence">${(emotion.confidence * 100).toFixed(0)}%</span>
            </div>
            <div class="emotion-reason">${emotion.reason}</div>
        `;
        elements.emotionsList.appendChild(item);
    });
    
    // 综合分析
    elements.analysisText.textContent = result.analysis;
    
    // 时间戳
    const timestamp = new Date(result.timestamp).toLocaleString('zh-CN');
    elements.timestamp.textContent = `分析时间: ${timestamp}`;
    
    // 显示结果区域
    elements.resultContent.style.display = 'block';
    elements.emptyState.style.display = 'none';
}

// 添加到对话历史
function addToHistory(role, content) {
    state.conversationHistory.push({ role, content });
    
    // 只保留最近10条
    if (state.conversationHistory.length > 10) {
        state.conversationHistory = state.conversationHistory.slice(-10);
    }
    
    // 保存到本地存储
    saveConversationHistory();
    
    // 更新显示
    updateHistoryDisplay();
}

// 更新历史显示
function updateHistoryDisplay() {
    if (state.conversationHistory.length === 0) {
        elements.conversationHistory.innerHTML = '<p class="empty-hint">暂无对话历史</p>';
        return;
    }
    
    elements.conversationHistory.innerHTML = '';
    state.conversationHistory.forEach(item => {
        const div = document.createElement('div');
        div.className = 'history-item';
        const roleText = item.role === 'user' ? '用户' : '助手';
        div.innerHTML = `
            <span class="history-role">${roleText}:</span>
            <span>${item.content}</span>
        `;
        elements.conversationHistory.appendChild(div);
    });
    
    // 滚动到底部
    elements.conversationHistory.scrollTop = elements.conversationHistory.scrollHeight;
}

// 清空历史
function clearHistory() {
    if (confirm('确定要清空对话历史吗？')) {
        state.conversationHistory = [];
        saveConversationHistory();
        updateHistoryDisplay();
        showToast('历史已清空', 'success');
    }
}

// 保存对话历史到本地存储
function saveConversationHistory() {
    try {
        localStorage.setItem('conversationHistory', JSON.stringify(state.conversationHistory));
    } catch (error) {
        console.error('保存历史失败:', error);
    }
}

// 加载对话历史
function loadConversationHistory() {
    try {
        const saved = localStorage.getItem('conversationHistory');
        if (saved) {
            state.conversationHistory = JSON.parse(saved);
            updateHistoryDisplay();
        }
    } catch (error) {
        console.error('加载历史失败:', error);
    }
}

// 显示Toast通知
function showToast(message, type = 'success') {
    elements.toast.textContent = message;
    elements.toast.className = `toast ${type}`;
    elements.toast.classList.add('show');
    
    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

// 工具函数：格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

