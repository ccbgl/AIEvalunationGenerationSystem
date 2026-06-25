<template>
  <div class="page">
    <Header />
    <main>
      <h2>{{ $t('login') }}</h2>
      <form @submit.prevent="onLogin">
        <input v-model="username" :placeholder="$t('username')" />
        <input v-model="password" type="password" :placeholder="$t('password')" />
        <button type="submit">{{ $t('login') }}</button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'
import Header from '../components/Header.vue'
import { useRouter } from 'vue-router'
const { t } = useI18n()
const username = ref('')
const password = ref('')
const router = useRouter()
async function onLogin(){
  try{
    const res = await api.post('/api/auth/login', { username: username.value, password: password.value })
    const token = res.data.token
    if(!token) throw new Error('no token')
    localStorage.setItem('token', token)
    // fetch current user and store
    try{
      const me = await api.get('/api/auth/me')
      if(me && me.data){ localStorage.setItem('user', JSON.stringify(me.data)) }
    }catch(e){ console.warn('fetch me failed', e) }
    alert(t('login_ok'))
    router.push('/')
  }catch(e){
    const detail = e?.response?.data?.detail
    if(detail === 'invalid credentials'){
      alert(t('invalid_credentials'))
    }else{
      alert(t('login_failed'))
    }
  }
}
</script>

<style>
input{display:block;padding:8px;margin:8px 0;border-radius:6px;border:1px solid #ddd}
button{padding:8px;background:#ff6b6b;color:#fff;border:none;border-radius:6px}
</style>
