<!--主页-->
<template>
  <div class="home">
    <div class="welcome-section">
      <h1>欢迎使用小麦病害诊断系统</h1>
      <p class="user-welcome">{{ userInfo ? `${userInfo.account}，欢迎回来` : '' }}</p>
    </div>
    
    <div class="service-cards">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="service-card" @click.native="$router.push('/chat')">
            <i class="el-icon-chat-line-round"></i>
            <h3>智能诊断</h3>
            <p>通过AI对话，快速诊断小麦病害</p>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="service-card" @click.native="$router.push('/knowledge')">
            <i class="el-icon-connection"></i>
            <h3>知识图谱</h3>
            <p>查看完整的小麦病害知识体系</p>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="service-card" @click.native="showGuide = true">
            <i class="el-icon-document"></i>
            <h3>使用指南</h3>
            <p>了解系统的使用方法和注意事项</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <el-dialog
      title="系统操作指南"
      :visible.sync="showGuide"
      width="60%"
      :close-on-click-modal="false"
    >
      <div style="max-height:60vh;overflow:auto;text-align:left;">
        <h3>一、系统概述</h3>
        <p>本系统聚焦于小麦病害的诊断与知识管理，集成了用户登录注册、智能问答、知识图谱展示与交互、个人中心与历史记录管理等核心功能，旨在为用户提供便捷、准确的小麦病害诊断服务及全面的病害知识支持。</p>
        <h3>二、操作指南</h3>
        <h4>（一）用户登录与注册</h4>
        <b>注册流程</b>
        <ol>
          <li>打开系统登录页面，点击 "注册账号" 按钮。</li>
          <li>输入用户名（如 "202210331"）、密码及相关个人信息。</li>
          <li>点击 "注册" 完成注册 "</li>
        </ol>
        <b>登录操作</b>
        <ol>
          <li>返回登录页面，输入已注册的用户名和密码。</li>
          <li>点击 "登录"，进入系统主界面，显示 "[用户名]，欢迎回来"。</li>
          <li>支持 "账号登录" 和 "注册账号" 快捷切换。</li>
        </ol>
        <h4>（二）智能问答诊断</h4>
        <b>开启对话</b>
        <ol>
          <li>进入系统后，点击 "智能诊断" 模块，触发开场白："您好，需要我什么帮助吗？请告诉我小麦的发病情况，包括：1. 从哪个部位开始发病；2. 发病时的气象条件；3. 发病的生育期；4. 小麦的种植区"。</li>
        </ol>
        <b>信息输入</b>
        <ol>
          <li>单轮输入：按提示依次提供发病部位、气象条件、生育期、种植区等信息。例如，先告知 "发病部位为叶片"，系统将基于知识图谱索引推理，返回 3 个可能的病害信息（如小麦黑颖病、小麦黑节病、小麦黄矮病毒病），并提示补充其他信息。</li>
          <li>多轮对话：继续补充信息，如 "种植区为河北，气候为高温"，系统结合知识图谱和大模型进一步推理，精准定位病害（如小麦叶锈病），并详细展示病害特征、病原、防治措施等内容。</li>
        </ol>
        <b>交互规则</b>
        <ul>
          <li>系统支持自然语言输入，需确保信息描述清晰、准确。</li>
          <li>若信息不完整，系统将主动引导补充，直至完成诊断。</li>
        </ul>
        <h4>（三）知识图谱应用</h4>
        <b>图谱浏览</b>
        <ol>
          <li>点击 "知识图谱" 模块，进入可视化展示页面。</li>
          <li>图谱中黑色节点代表病害（如小麦灰霉病、麦链格孢叶枯病），绿色节点代表发病部位（如叶片、穗部、基部），黄棕色节点代表种植区（如重庆、浙江、冬麦区）。</li>
          <li>通过缩放、拖动操作浏览图谱整体结构，快速定位感兴趣的节点。</li>
        </ol>
        <b>节点交互</b>
        <ol>
          <li>点击任意节点（如 "小麦壳针孢叶枯病"），弹出子图及详细信息窗口，展示该病害的类型、别名、病原、症状、防治方法等内容。</li>
          <li>子图中可查看与该节点相关的其他节点（如发病部位 "叶片""穗部"、气象条件 "高湿""低温"），点击子图节点可进一步钻取关联信息。</li>
        </ol>
        <h4>（四）个人中心管理</h4>
        <b>历史记录查询</b>
        <ol>
          <li>在聊天界面左侧侧边栏点击 "历史信息"，右侧将显示所有过往对话记录，按时间顺序排列，每条记录标注消息数量和对话摘要。</li>
          <li>点击具体对话条目，可查看完整的问答内容，支持关键词搜索快速定位历史诊断记录。</li>
        </ol>
        <b>账户管理（管理员权限）</b>
        <ol>
          <li>管理员登录后，进入 "用户管理" 模块，可查看所有用户列表（显示 ID、账号、角色、创建时间）。</li>
          <li>选中目标用户，点击 "删除" 按钮，系统提示 "删除成功"，同时清除该用户的个人信息及历史记录。</li>
        </ol>
        <h3>三、注意事项</h3>
        <b>数据安全</b>
        <ul>
          <li>请妥善保管个人账号密码，避免泄露。</li>
          <li>管理员执行删除操作时需谨慎，删除后数据不可恢复。</li>
        </ul>
        <b>诊断准确性</b>
        <ul>
          <li>智能问答结果基于知识图谱和大模型推理，仅供参考。实际病害诊断需结合田间实地观察和专业农技人员意见。</li>
          <li>输入信息越详细（如具体生育期阶段、病害发展进程等），诊断结果越精准。</li>
        </ul>
        <b>系统维护</b>
        <ul>
          <li>如遇系统卡顿、页面异常等问题，可尝试刷新页面或重新登录。</li>
          <li>定期检查知识图谱内容，确保数据更新及时，如有错误或遗漏可通过 "反馈" 功能提交问题。</li>
        </ul>
        <h3>四、联系支持</h3>
        <ul>
          <li>如需获取更多帮助或反馈系统问题，可通过以下方式联系我们：</li>
          <li>客服电话：177xxxx2715 </li>
          <li>官方邮箱：bobo@qq.com</li>
        </ul>
        <p style="color:#888;font-size:13px;">通过本行动指南，用户可快速掌握系统操作流程，充分利用各项功能实现高效的小麦病害诊断与知识管理。</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="showGuide = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      userInfo: null,
      showGuide: false
    }
  },
  created() {
    const userStr = localStorage.getItem('userInfo')
    if (userStr) {
      this.userInfo = JSON.parse(userStr)
    }
  }
}
</script>

<style scoped>
.home {
  padding: 0;
}

.welcome-section {
  text-align: center;
  margin-bottom: 60px;
  padding: 0 40px;
}

.welcome-section h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 10px;
}

.user-welcome {
  font-size: 18px;
  color: #409EFF;
}

.service-cards {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

.service-card {
  text-align: center;
  padding: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.service-card i {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 20px;
}

.service-card h3 {
  font-size: 20px;
  color: #303133;
  margin-bottom: 10px;
}

.service-card p {
  color: #909399;
  font-size: 14px;
}
</style>
