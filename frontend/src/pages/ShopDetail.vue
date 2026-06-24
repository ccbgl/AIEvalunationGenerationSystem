<template>
  <div class="page"><Header />
    <main>
      <div v-if="!shop">Loading...</div>
      <div v-else>
        <h2>{{ shop.shop_name }}</h2>
        <img :src="shop.cover_image || '/static/img/cover.jpg'" alt="cover" style="width:100%;height:160px;object-fit:cover;border-radius:8px"/>
        <div class="meta">{{ shop.description }}</div>
        <div class="actions">
          <router-link to="/">Back</router-link>
          <router-link to="/ai">AI Generate</router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Header from '../components/Header.vue'
import api from '../api'

const route = useRoute()
const shop = ref(null)

async function load(){
  try{
    const res = await api.get(`/api/shops/${route.params.id}`)
    shop.value = res.data
  }catch(e){ console.warn(e) }
}

onMounted(()=>load())
</script>

<style>
.meta{margin:8px 0;color:#555}
.actions{display:flex;gap:8px;margin-top:12px}
</style>
