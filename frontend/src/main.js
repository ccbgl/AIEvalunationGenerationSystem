import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ShopList from './pages/ShopList.vue'
import ShopDetail from './pages/ShopDetail.vue'
import AIGenerate from './pages/AIGenerate.vue'

const routes = [
  { path: '/', component: ShopList },
  { path: '/shop/:id', component: ShopDetail },
  { path: '/ai', component: AIGenerate }
]

const router = createRouter({ history: createWebHistory(), routes })

createApp(App).use(router).mount('#app')
