<!-- 聊天框组件 -->
<template>
  <div class="chat-box">
    <!-- v-for 用来遍历 messages 数组中的每条消息 -->
    <div v-for="msg in messages" :key="msg.id" :class="['message', msg.sender]">
      <!-- 每条消息显示在一个 <p> 标签中 -->
      <p>{{ msg.text }}</p>
    </div>
    
    <!-- 传递 sendMessage 方法给 InputBar 组件，处理消息发送 -->
    <InputBar @sendMessage="sendMessage" />
  </div>
</template>


<script>
import InputBar from './InputBar.vue';  // 导入子组件 InputBar

export default {
  components: { InputBar },  // 注册子组件
  data() {
    return {
      messages: []  // 存储聊天记录的数组
    };
  },
  methods: {
    // 处理用户消息的方法
    sendMessage(text) {
      // 用户消息添加到 messages 数组，并使用当前时间戳作为 id
      this.messages.push({ id: Date.now(), text, sender: 'user' });
      // 获取机器人的回复
      this.getBotReply(text);
    },
    // 异步获取机器人回复的函数
    async getBotReply(text) {
      // 发送 POST 请求到后端的 API，传递用户消息并等待响应
      let response = await this.$axios.post('/api/chat', { message: text });
      // 机器人回复添加到 messages 数组
      this.messages.push({ id: Date.now(), text: response.data.reply, sender: 'bot' });
    }
  }
};
</script>


<style>
.chat-box {
  max-width: 600px;
  margin: auto;
}
.message {
  padding: 10px;
  margin: 5px;
  border-radius: 5px;
}
.user {
  background: #cce5ff;
  text-align: right;
}
.bot {
  background: #f8f9fa;
  text-align: left;
}
</style>