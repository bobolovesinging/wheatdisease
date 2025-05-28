import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue';
import Chat from '../views/Chat.vue';
import Knowledge from '../views/Knowledge.vue';
import Login from '../views/Login.vue';
import UserManage from '../views/UserManage.vue';

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: Knowledge
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/user-manage',
    name: 'UserManage',
    component: UserManage
  }
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
});

export default router;