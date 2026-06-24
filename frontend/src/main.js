import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ShopList from './pages/ShopList.vue'
import ShopDetail from './pages/ShopDetail.vue'
import AIGenerate from './pages/AIGenerate.vue'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import MyAccount from './pages/MyAccount.vue'
import './assets/styles.css'
import i18n from './i18n'

const routes = [
  { path: '/', component: ShopList },
  { path: '/shop/:id', component: ShopDetail },
  { path: '/ai', component: AIGenerate },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/me', component: MyAccount }
]

const router = createRouter({ history: createWebHistory(), routes })

createApp(App).use(router).use(i18n).mount('#app')
