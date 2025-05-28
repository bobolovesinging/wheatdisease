<template>
  <div id="app">
    <nav class="top-nav">
      <div class="nav-content">
        <router-link to="/" class="nav-item">首页</router-link>
        <router-link to="/chat" class="nav-item">智能诊断</router-link>
        <router-link to="/knowledge" class="nav-item">知识图谱</router-link>
        <router-link 
          v-if="userInfo && userInfo.role === 'admin'" 
          to="/user-manage" 
          class="nav-item"
        >用户管理</router-link>
      </div>
      <div class="user-section">
        <template v-if="!userInfo">
          <router-link to="/login" class="nav-item">登录</router-link>
        </template>
        <template v-else>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ userInfo.account }}
              <i class="el-icon-arrow-down"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="logout">
                <i class="el-icon-switch-button"></i> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </template>
      </div>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
export default {
  name: 'App',
  computed: {
    ...mapGetters('user', ['userInfo'])
  },
  methods: {
    ...mapActions('user', ['logout']),
    handleCommand(command) {
      if (command === 'logout') {
        this.logout()
        if (this.$route.path !== '/login') {
          this.$router.push('/login')
        }
        this.$message.success('已退出登录')
      }
    }
  }
};
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  color: #2c3e50;
  height: 100vh;
  padding-top: 60px;
}

.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: #409EFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
}

.nav-content {
  display: flex;
  gap: 20px;
}

.nav-item {
  color: #fff;
  text-decoration: none;
  font-size: 16px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.user-info:hover {
  opacity: 0.9;
}

.el-dropdown-menu__item i {
  margin-right: 5px;
}
</style>
