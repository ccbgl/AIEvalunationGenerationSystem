<template>
  <div class="page">
    <Header />
    <main>
      <div class="search-row">
        <input v-model="q" :placeholder="$t('search_placeholder')" />
        <button @click="fetchShops">Search</button>
      </div>
      <div class="hero">
        <img src="/static/img/cover.jpg" alt="hero" />
      </div>
      <div>
        <ShopCard v-for="s in shops" :key="s.id" :shop="s" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Header from '../components/Header.vue'
import ShopCard from '../components/ShopCard.vue'
import api from '../api'

const q = ref('')
const shops = ref([])

async function fetchShops(){
  try{
    const res = await api.get('/api/shops')
    shops.value = res.data
  }catch(e){ console.warn(e) }
}

onMounted(()=>{
  fetchShops()
})
</script>

<style>
.page main{padding:12px}
.search-row{display:flex;gap:8px;margin-bottom:12px}
.search-row input{flex:1;padding:8px;border-radius:6px;border:1px solid #ddd}
.hero img{width:100%;height:140px;object-fit:cover;border-radius:8px;margin-bottom:12px}
</style>
