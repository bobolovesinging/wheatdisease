<template>
  <!-- 消息项容器，根据发送者设置不同的样式类 -->
  <div :class="['message-item', msg.sender]">
    <!-- 头像区域 -->
    <div class="avatar">
      <el-avatar 
        :size="40" 
        :icon="msg.sender === 'bot' ? 'el-icon-service' : 'el-icon-user'" 
      />
    </div>
    <!-- 消息内容区域 -->
    <div class="message-content">
      <span>{{ msg.text }}</span>
      <!-- 添加交互按钮 -->
      <div v-if="msg.sender === 'bot' && showInteractionButtons" class="interaction-buttons">
        <el-button 
          size="small" 
          type="primary" 
          @click="handleInteraction('继续')"
        >继续</el-button>
        <el-button 
          size="small" 
          type="success" 
          @click="handleInteraction('深入')"
        >深入</el-button>
        <el-button 
          size="small" 
          type="warning" 
          @click="handleInteraction('切换话题')"
        >切换话题</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MessageItem',
  // 接收消息对象作为属性
  props: ['msg'],
  data() {
    return {
      showInteractionButtons: false
    }
  },
  mounted() {
    // 检查消息是否包含交互选项
    if (this.msg.sender === 'bot' && this.msg.text.includes('[继续]')) {
      this.showInteractionButtons = true;
    }
  },
  methods: {
    handleInteraction(choice) {
      this.$emit('interaction', choice);
    }
  }
};
</script>

<style scoped>
/* 消息项基础样式 */
.message-item {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

/* 消息内容样式 */
.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
}

/* 用户消息样式 */
.user {
  flex-direction: row-reverse;  /* 用户消息靠右显示 */
}

.user .message-content {
  background: #409EFF;
  color: white;
  border-radius: 8px 8px 0 8px;  /* 特殊的气泡形状 */
}

/* 机器人消息样式 */
.bot .message-content {
  background: #fff;
  color: #333;
  border-radius: 8px 8px 8px 0;  /* 特殊的气泡形状 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.interaction-buttons {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.interaction-buttons .el-button {
  padding: 6px 12px;
}
</style>
