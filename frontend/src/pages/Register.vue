<template>
  <div class="page">
    <Header />
    <main>
      <h2>{{ $t('register') }}</h2>
      <form @submit.prevent="onRegister">
        <input v-model="username" :placeholder="$t('username')" />
        <input v-model="password" type="password" :placeholder="$t('password')" />
        <button type="submit">{{ $t('register') }}</button>
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
async function onRegister(){
  try{
    const res = await api.post('/api/auth/register', { username: username.value, password: password.value })
    const token = res.data.token
    if(token){
      localStorage.setItem('token', token)
      // store returned user if present
      if(res.data.user){
        localStorage.setItem('user', JSON.stringify(res.data.user))
      }else{
        // fallback: fetch /me
        try{
          const me = await api.get('/api/auth/me')
          if(me && me.data){ localStorage.setItem('user', JSON.stringify(me.data)) }
        }catch(e){ console.warn('fetch me failed', e) }
      }
      alert(t('register_ok'))
      router.push('/')
    }else{
      alert(t('registered_please_login'))
      router.push('/login')
    }
  }catch(e){
    const detail = e?.response?.data?.detail
    if(detail === 'username exists'){
      alert(t('username_exists'))
    }else{
      alert(t('register_failed'))
    }
  }
}
</script>

<style>
input{display:block;padding:8px;margin:8px 0;border-radius:6px;border:1px solid #ddd}
button{padding:8px;background:#ff6b6b;color:#fff;border:none;border-radius:6px}
</style>
