<template>
  <div class="shop-card">
    <img :src="shop.cover_image || '/static/img/cover.jpg'" alt="cover" />
    <div class="meta">
      <h3>{{ shop.shop_name }}</h3>
      <div class="info">Avg: ${{ shop.avg_cost }} · Good rate: {{ shop.good_rate }}%</div>
      <router-link :to="`/shop/${shop.id}`">View</router-link>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ shop: Object })
</script>

<style scoped>
.shop-card{display:flex;padding:12px;border-bottom:1px solid #eee}
.shop-card img{width:80px;height:80px;object-fit:cover;border-radius:8px}
.meta{margin-left:12px}
.meta h3{margin:0;font-size:16px}
.info{color:#888;font-size:13px;margin:6px 0}
</style>
