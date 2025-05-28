<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <h2>小麦病害诊断系统</h2>
        <p>欢迎{{ activeTab === 'login' ? '登录' : '注册' }}</p>
      </div>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="账号登录" name="login">
          <el-form 
            :model="loginForm" 
            :rules="loginRules"
            ref="loginForm" 
            label-width="0px"
            class="login-form"
          >
            <el-form-item prop="account">
              <el-input 
                v-model="loginForm.account"
                prefix-icon="el-icon-user"
                placeholder="请输入账号"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                prefix-icon="el-icon-lock"
                type="password"
                placeholder="请输入密码"
                @keyup.enter.native="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                :loading="loading"
                class="submit-button"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册账号" name="register">
          <el-form
            :model="registerForm"
            :rules="registerRules"
            ref="registerForm"
            label-width="0px"
            class="register-form"
          >
            <el-form-item prop="account">
              <el-input
                v-model="registerForm.account"
                prefix-icon="el-icon-user"
                placeholder="请输入账号(9位)"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                prefix-icon="el-icon-lock"
                type="password"
                placeholder="请输入密码(6-20位)"
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                prefix-icon="el-icon-lock"
                type="password"
                placeholder="请确认密码"
              />
            </el-form-item>

            <el-form-item prop="role">
              <el-radio-group v-model="registerForm.role">
                <el-radio label="user">普通用户</el-radio>
                <el-radio label="admin">管理员</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                class="submit-button"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'LoginView',
  data() {
    // 密码确认验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      activeTab: 'login',
      loading: false,
      loginForm: {
        account: '',
        password: ''
      },
      registerForm: {
        account: '',
        password: '',
        confirmPassword: '',
        role: 'user'
      },
      loginRules: {
        account: [
          { required: true, message: '请输入账号', trigger: 'blur' },
          { min: 9, max: 9, message: '账号必须是9位', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      },
      registerRules: {
        account: [
          { required: true, message: '请输入账号', trigger: 'blur' },
          { min: 9, max: 9, message: '账号必须是9位', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择用户角色', trigger: 'change' }
        ]
      }
    }
  },
  methods: {
    handleTabClick() {
      // 切换标签时重置表单
      this.loading = false
      if (this.activeTab === 'login') {
        this.$refs.loginForm?.resetFields()
      } else {
        this.$refs.registerForm?.resetFields()
      }
    },
    
    async handleLogin() {
      try {
        await this.$refs.loginForm.validate()
        this.loading = true
        
        const response = await request.post('/api/users/login/', this.loginForm)
        
        if (response.data.token) {
          // 保存token
          localStorage.setItem('token', response.data.token)
          // 通过Vuex同步用户信息
          this.$store.dispatch('user/login', {
            id: response.data.id,
            account: response.data.account,
            role: response.data.role
          })
          // 直接跳转到首页
          this.$router.push('/home')
        }
      } catch (error) {
        this.$message.error(error.response?.data?.error || '登录失败')
      } finally {
        this.loading = false
      }
    },
    
    async handleRegister() {
      try {
        await this.$refs.registerForm.validate()
        this.loading = true
        
        await request.post('/api/users/register/', {
          account: this.registerForm.account,
          password: this.registerForm.password,
          role: this.registerForm.role
        })
        
        this.$message.success('注册成功，请登录')
        this.activeTab = 'login'
        this.loginForm.account = this.registerForm.account
      } catch (error) {
        this.$message.error(error.response?.data?.error || '注册失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1abc9c 0%, #8e44ad 100%);
}

.login-card {
  width: 400px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0;
  color: #409EFF;
  font-size: 24px;
}

.login-header p {
  margin: 10px 0 0;
  color: #909399;
  font-size: 16px;
}

.login-form, .register-form {
  margin-top: 20px;
}

.submit-button {
  width: 100%;
}

.el-tabs {
  margin-top: 20px;
}

.el-radio-group {
  width: 100%;
  display: flex;
  justify-content: space-around;
}
</style>
