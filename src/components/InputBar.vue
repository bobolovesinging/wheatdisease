<!--输入框组件-->
<template>
  <!-- 输入栏容器 -->
  <div class="input-bar">
    <!-- 文本输入框 -->
    <el-input
      v-model="message"
      placeholder="请输入您要咨询的问题..."
      :rows="3"
      type="textarea"
      resize="none"
      @keyup.enter.native="handleSend"
      :disabled="disabled"
    >
    </el-input>
    
    <!-- 发送按钮 -->
    <el-button 
      type="primary" 
      :disabled="disabled || !message.trim()" 
      @click="handleSend"
      icon="el-icon-s-promotion"
    >
      发送
    </el-button>
  </div>
</template>

<script>
export default {
  name: 'InputBar',
  
  // 组件属性定义
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  
  // 组件数据
  data() {
    return { 
      message: ''  // 输入框的文本内容
    };
  },
  
  methods: {
    /**
     * 处理消息发送
     * 验证消息不为空且组件未禁用时发送消息
     */
    handleSend() {
      if (this.disabled || !this.message.trim()) return;
      
      this.$emit('sendMessage', this.message);
      this.message = '';  // 清空输入框
    }
  }
};
</script>

<style scoped>
/* 输入栏容器样式 */
.input-bar {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

/* 输入框样式 */
.el-input {
  flex: 1;  /* 输入框占据剩余空间 */
}

/* 发送按钮样式 */
.el-button {
  height: 80px;
  width: 100px;
}
</style>
