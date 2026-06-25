<template>
  <header class="app-header">
    <div class="brand"><router-link to="/">{{ $t('brand') }}</router-link></div>
    <nav>
      <router-link to="/">{{ $t('shops') }}</router-link>
      <router-link to="/ai">{{ $t('ai_generate') }}</router-link>
      <router-link v-if="!logged" to="/login">{{ $t('login') }}</router-link>
      <router-link v-if="!logged" to="/register">{{ $t('register') }}</router-link>
      <router-link v-if="logged" to="/me">{{ $t('my') }}</router-link>
      <span v-if="logged" class="username">{{ username }}</span>
      <a v-if="logged" href="#" @click.prevent="doLogout">{{ $t('logout') || 'Logout' }}</a>
      <select v-model="lang" @change="onLangChange">
        <option value="zh">中文</option>
        <option value="en">English</option>
      </select>
    </nav>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import { useRouter } from 'vue-router'
const { locale } = useI18n()
const lang = ref(locale.value)
const logged = computed(()=> !!localStorage.getItem('token'))
const username = computed(()=>{
  const u = localStorage.getItem('user')
  if(!u) return ''
  try{ return JSON.parse(u).username }catch{ return '' }
})
const router = useRouter()
function onLangChange(){ locale.value = lang.value }
async function doLogout(){
  const token = localStorage.getItem('token')
  try{
    if(token){ await api.post('/api/auth/logout') }
  }catch(e){ console.warn('logout failed', e) }
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.app-header{display:flex;align-items:center;justify-content:space-between;padding:12px;background:#fff;border-bottom:1px solid #f0f0f0}
.brand a{font-weight:700;color:#ff6b6b;text-decoration:none}
nav a{margin-left:12px;color:#333;text-decoration:none}
select{margin-left:12px}
</style>
