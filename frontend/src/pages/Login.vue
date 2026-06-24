<template>
  <div class="page">
    <Header />
    <main>
      <h2>Login</h2>
      <form @submit.prevent="onLogin">
        <input v-model="username" placeholder="username" />
        <input v-model="password" type="password" placeholder="password" />
        <button type="submit">Login</button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
import Header from '../components/Header.vue'
import { useRouter } from 'vue-router'
const username = ref('')
const password = ref('')
const router = useRouter()
async function onLogin(){
  try{
    const res = await api.post('/api/auth/login', { username: username.value, password: password.value })
    const token = res.data.token
    localStorage.setItem('token', token)
    alert('login ok')
    router.push('/')
  }catch(e){ alert('login failed') }
}
</script>

<style>
input{display:block;padding:8px;margin:8px 0;border-radius:6px;border:1px solid #ddd}
button{padding:8px;background:#ff6b6b;color:#fff;border:none;border-radius:6px}
</style>
