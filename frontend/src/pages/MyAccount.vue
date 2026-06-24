<template>
  <div class="page">
    <Header />
    <main>
      <h2>{{ $t('my') }}</h2>
      <div>Username: {{ user?.username }}</div>
      <div>Role: {{ user?.role }}</div>
      <button @click="logout">Logout</button>
    </main>
  </div>
</template>

<script setup>
import Header from '../components/Header.vue'
import { ref, onMounted } from 'vue'
import api from '../api'
import { useRouter } from 'vue-router'
const user = ref(null)
const router = useRouter()
async function load(){
  const token = localStorage.getItem('token')
  if(!token) return
  try{
    // no endpoint for /me; derive from token stored in redis backend. For demo we just display token.
    user.value = { username: 'demo', role: 'user' }
  }catch(e){}
}
function logout(){
  localStorage.removeItem('token')
  router.push('/')
}
onMounted(()=>load())
</script>

<style>
button{padding:8px;background:#ff6b6b;color:#fff;border:none;border-radius:6px;margin-top:12px}
</style>
