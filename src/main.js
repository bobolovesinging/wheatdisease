import Vue from 'vue'
import App from './App.vue'
import './styles/index.css'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import axios from 'axios'

Vue.use(ElementUI)

// 配置axios默认值
axios.defaults.baseURL = 'http://127.0.0.1:8000'  // 修改为Django服务器地址
axios.defaults.headers.post['Content-Type'] = 'application/json'

// 将axios添加到Vue实例
Vue.prototype.$axios = axios

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
