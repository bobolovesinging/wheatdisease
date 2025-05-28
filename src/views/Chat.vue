<template>
  <!-- 聊天界面容器 -->
  <div class="chat-layout">
    <!-- 侧边栏 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="createNewSession">
          <i class="el-icon-plus"></i>
          新对话
        </button>
      </div>
      <div class="history-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          :class="['history-item', { active: session.id === currentSessionId }]"
          @click="loadSession(session.id)"
        >
          <div class="history-item-content">
            <div class="history-title">
              <span v-if="!editingTitle || editingSessionId !== session.id">{{ session.title || '新对话' }}</span>
              <el-input
                v-else
                v-model="editingTitle"
                size="small"
                @blur="saveTitle(session.id)"
                @keyup.enter="saveTitle(session.id)"
                ref="titleInput"
              ></el-input>
            </div>
            <div class="history-preview">
              共{{ session.message_count || 0 }}条消息
            </div>
          </div>
          <div class="history-actions">
            <button class="edit-btn" @click.stop="startEditTitle(session)">
              <i class="el-icon-edit"></i>
            </button>
            <button class="clear-btn" @click.stop="clearHistory(session.id)">
              <i class="el-icon-delete"></i>
            </button>
          </div>
        </div>
        <button v-if="sessionHasMore" @click="loadSessionList(false)">查看更多</button>
      </div>
    </div>

    <!-- 主聊天区域 -->
    <div class="chat-main">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-title">小麦病害智能诊断</div>
      </div>

      <!-- 消息列表 -->
      <div class="messages-container" ref="messageContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-item', msg.role === 'user' ? 'user-message' : 'assistant-message']"
        >
          <div class="message-avatar">
            <i :class="msg.role === 'user' ? 'el-icon-user' : 'el-icon-service'"></i>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
          </div>
        </div>
        
        <!-- 加载动画 -->
        <div v-if="loading" class="loading-container">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-wrapper">
          <textarea
            v-model="inputMessage"
            class="message-input"
            :rows="1"
            placeholder="请描述小麦的症状..."
            @keydown.enter.prevent="sendMessage"
            @input="autoResize"
            ref="messageInput"
            :disabled="loading"
          ></textarea>
          <button 
            class="send-button"
            @click="sendMessage"
            :disabled="loading || !inputMessage.trim()"
          >
            <i class="el-icon-s-promotion"></i>
            发送
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'ChatView',
  data() {
    return {
      messages: [],
      inputMessage: '',
      loading: false,
      currentResponse: '',
      currentSessionId: null,
      sessions: [],
      editingTitle: '',
      editingSessionId: null,
      sessionPage: 1,
      sessionPageSize: 10,
      sessionHasMore: true,
      printBuffer: '',   // 打字缓冲区
      typing: false,     // 是否正在打字
      historyLoaded: false,  // 是否已加载过历史
      hasMoreHistory: false, // 是否还有更多历史
      historyOffset: 0,      // 历史分页偏移
      historyLimit: 3        // 每次加载几条
    }
  },
  async created() {
    // 立即显示欢迎词
    this.messages.push({
      role: 'assistant',
      content: '您好，需要我什么帮助吗？请告诉我小麦的发病情况，包括：\n1. 从哪个部位开始发病\n2. 发病时的气象条件\n3. 发病的生育期\n4. 小麦的种植区'
    });
    // 加载左侧会话列表
    await this.loadSessionList(true);
  },
  methods: {
    formatMessage(text) {
      if (!text) return '';       
      // 先处理可能的HTML标签
      const escapedText = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
      // 处理换行符
      const formattedText = escapedText
        .replace(/\\n/g, '\n')  // 处理显式的换行符标记
        .split('\n')            // 将文本按换行符分割
        .join('<br>');          // 用<br>标签重新连接
      console.log('最终格式化文本:', formattedText);
      return formattedText;
    },
    autoResize(e) {
      const textarea = e.target
      textarea.style.height = 'auto'
      textarea.style.height = textarea.scrollHeight + 'px'
    },
    async loadSessionList(reset = false) {
      if (reset) {
        this.sessionPage = 1;
        this.sessions = [];
        this.sessionHasMore = true;
      }
      try {
        const response = await request.get('/api/chat/get_session_list/', {
          params: {
            page: this.sessionPage,
            size: this.sessionPageSize
          }
        });
        if (response.data && response.data.sessions) {
          if (reset) {
            this.sessions = response.data.sessions;
          } else {
            // 合并去重
            const newSessions = response.data.sessions;
            const allSessions = this.sessions.concat(newSessions);
            this.sessions = Array.from(new Map(allSessions.map(s => [s.id, s])).values());
          }
          if (response.data.sessions.length < this.sessionPageSize) {
            this.sessionHasMore = false;
          }
        } else {
          this.sessionHasMore = false;
        }
      } catch (error) {
        this.$message.error('加载历史会话失败');
      }
    },
    async loadSession(sessionId) {
      this.currentSessionId = sessionId;
      this.messages = [];
      try {
        const res = await request.get('/api/chat/get_history/', {
          params: { session_id: sessionId }
        });
        if (res.data && res.data.messages) {
          this.messages = res.data.messages;
        }
      } catch (e) {
        this.$message.error('加载历史消息失败');
      }
    },
    async createNewSession() {
      try {
        this.loading = true;
        const response = await request.post('/api/chat/create_session/');
        if (response.data && response.data.session_id) {
          this.currentSessionId = response.data.session_id;
          this.messages = [];
          this.currentResponse = '';
          await this.loadSessionList(true);
        } else {
          throw new Error('创建会话失败：服务器返回数据格式错误');
        }
      } catch (error) {
        this.$message.error('创建新会话失败');
      } finally {
        this.loading = false;
      }
    },
    async loadHistory(reset = false) {
      if (!this.currentSessionId) return;
      if (reset) {
        this.historyOffset = 0;
        this.hasMoreHistory = false;
      }
      try {
        const response = await request.get('/api/chat/get_history/', {
          params: {
            session_id: this.currentSessionId,
            offset: this.historyOffset,
            limit: this.historyLimit
          }
        });
        if (response.data && response.data.messages) {
          // 只追加，不清空
          if (reset) {
            this.messages = this.messages.slice(0, 1); // 保留欢迎词
          }
          // 追加历史消息到欢迎词后面
          this.messages.splice(1, 0, ...response.data.messages);
          this.historyOffset += response.data.messages.length;
          this.hasMoreHistory = response.data.messages.length === this.historyLimit;
        }
      } catch (error) {
        this.$message.error('加载历史记录失败');
      }
    },
    async loadMoreHistory() {
      await this.loadHistory(false);
    },
    async sendMessage() {
      if (!this.inputMessage.trim() || this.loading) return;
      if (!this.currentSessionId) {
        await this.createNewSession();
        if (!this.currentSessionId) {
          this.$message.error('会话创建失败，请重试');
          return;
        }
        await this.loadSessionList(true);
      }
      const message = this.inputMessage.trim();
      this.inputMessage = '';
      // 只本地 push 用户消息
      this.messages.push({ role: 'user', content: message });
      this.loading = true;
      const token = localStorage.getItem('token');
      this.printBuffer = '';
      this.typing = false;
      const eventSource = new EventSource(
        `/api/chat/stream_chat/?message=${encodeURIComponent(message)}&session_id=${this.currentSessionId}&token=${token}`
      );
      let assistantIndex = this.messages.length;
      this.messages.push({ role: 'assistant', content: '' });
      eventSource.onmessage = (event) => {
        const data = event.data;
        if (data === '[DONE]') {
          this.loading = false;
          eventSource.close();
          return;
        }
        this.printBuffer += data;
        if (!this.typing) {
          this.typing = true;
          this.typeWriter(assistantIndex);
        }
      };
      eventSource.onerror = () => {
        eventSource.close();
        this.loading = false;
        this.$message.error('连接错误，请重试');
      };
    },
    typeWriter(index) {
      if (!this.printBuffer || this.printBuffer.length === 0) {
        this.typing = false;
        return;
      }
      this.messages[index].content += this.printBuffer[0];
      this.printBuffer = this.printBuffer.slice(1);
      setTimeout(() => {
        this.typeWriter(index);
      }, 30);
    },
    scrollToBottom() {
      const container = this.$refs.messageContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    async clearHistory(sessionId) {
      try {
        await this.$confirm('确定要清除此对话记录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await request.post('/api/chat/clear_history/', {
          session_id: sessionId
        })
        
        if (response.data.status === 'success') {
          if (sessionId === this.currentSessionId) {
            this.messages = []
            this.currentResponse = ''
          }
          await this.loadHistory()
          this.$message.success('历史记录已清除')
        } else {
          this.$message.error(response.data.message || '清除历史记录失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('清除历史记录失败:', error)
          this.$message.error('清除历史记录失败: ' + (error.response?.data?.message || error.message))
        }
      }
    },
    async saveTitle(sessionId) {
      if (!this.editingTitle.trim()) {
        this.editingTitle = '';
        this.editingSessionId = null;
        return;
      }

      try {
        const response = await request.post('/api/chat/update_session_title/', {
          session_id: sessionId,
          title: this.editingTitle.trim()
        });

        if (response.data.status === 'success') {
          // 更新本地会话列表中的标题
          const session = this.sessions.find(s => s.id === sessionId);
          if (session) {
            session.title = this.editingTitle.trim();
          }
          this.$message.success('标题更新成功');
        } else {
          this.$message.error(response.data.message || '更新标题失败');
        }
      } catch (error) {
        console.error('更新标题失败:', error);
        this.$message.error('更新标题失败: ' + (error.response?.data?.message || error.message));
      }

      this.editingTitle = '';
      this.editingSessionId = null;
    },

    startEditTitle(session) {
      this.editingTitle = session.title || '新对话';
      this.editingSessionId = session.id;
      this.$nextTick(() => {
        if (this.$refs.titleInput) {
          this.$refs.titleInput.focus();
        }
      });
    },
  },
  watch: {
    messages: {
      handler() {
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: calc(100vh - 60px); /* 减去导航栏的高度 */
  background-color: #f0f2f5;
  position: relative;
}

.chat-sidebar {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #eaeaea;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  height: 100%; /* 确保侧边栏填满高度 */
  overflow: hidden; /* 防止内容溢出 */
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.new-chat-btn {
  width: 100%;
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.new-chat-btn:hover {
  background-color: #40a9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.2);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.history-item {
  padding: 14px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid transparent;
}

.history-item:hover {
  background-color: #f5f5f5;
  border-color: #e6e6e6;
}

.history-item.active {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.history-item-content {
  flex: 1;
  overflow: hidden;
  margin-right: 8px;
}

.history-title {
  font-weight: 500;
  margin-bottom: 4px;
  color: #333;
}

.history-preview {
  font-size: 12px;
  color: #8c8c8c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-actions {
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  gap: 8px;
}

.history-item:hover .history-actions {
  opacity: 1;
}

.edit-btn {
  padding: 6px;
  background: transparent;
  border: none;
  color: #1890ff;
  cursor: pointer;
  transition: all 0.3s;
}

.edit-btn:hover {
  color: #40a9ff;
  transform: scale(1.1);
}

.clear-btn {
  padding: 6px;
  background: transparent;
  border: none;
  color: #ff4d4f;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-btn:hover {
  color: #ff7875;
  transform: scale(1.1);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  height: 100%; /* 确保主区域填满高度 */
  overflow: hidden; /* 防止内容溢出 */
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #fff;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: #f8f9fa;
}

.message-item {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 12px;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
}

.assistant-message .message-avatar {
  background: linear-gradient(135deg, #52c41a, #389e0d);
  color: white;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;        /* 保留空白符和换行符 */
  word-wrap: break-word;        /* 允许长单词换行 */
  word-break: break-word;       /* 在合适的位置换行 */
}

.user-message .message-text {
  background: #e6f7ff;
  border-top-right-radius: 4px;
}

.assistant-message .message-text {
  background: #fff;
  border-top-left-radius: 4px;
}

.input-container {
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0; /* 防止输入区域被压缩 */
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background-color: #f8f9fa;
  border-radius: 12px;
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  resize: none;
  min-height: 24px;
  max-height: 120px;
  line-height: 1.6;
  font-size: 14px;
  padding: 8px;
}

.send-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.send-button:disabled {
  background: #d9d9d9;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #1890ff;
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
