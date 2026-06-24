<template>
  <div class="page">
    <h1>Shops</h1>
    <div v-for="shop in shops" :key="shop.id" class="shop-card">
      <router-link :to="`/shop/${shop.id}`">{{ shop.shop_name }} - {{ shop.good_rate }}%</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const shops = ref([])
onMounted(async ()=>{
  try{
    const res = await axios.get('/api/shops')
    shops.value = res.data
  }catch(e){
    console.warn('fetch shops failed', e)
  }
})
</script>

<style>
.shop-card { padding: 8px; border-bottom: 1px solid #eee }
</style>
