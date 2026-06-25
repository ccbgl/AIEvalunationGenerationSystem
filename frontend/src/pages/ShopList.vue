<template>
  <div class="page">
    <Header />
    <main>
      <div class="search-row">
        <input v-model="q" :placeholder="$t('search_placeholder')" />
        <select v-model="sort" @change="fetchShops">
        <option value="recommended">{{ $t('recommended') }}</option>
        <option value="good_rate">{{ $t('opt_good_rate') }}</option>
        <option value="avg_cost">{{ $t('opt_avg_cost') }}</option>
        <option value="name">{{ $t('opt_name') }}</option>
        </select>
        <button @click="fetchShops">{{ $t('search') }}</button>
      </div>
      <div class="hero">
        <img src="/static/img/cover.jpg" alt="hero" />
      </div>
      <div>
        <ShopCard v-for="s in shops" :key="s.id" :shop="s" />
      </div>

      <div class="pagination">
      <label>{{ $t('page_size') }}:
          <select v-model.number="page_size" @change="onPageSizeChange">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </label>

      <button :disabled="page<=1" @click="changePage(page-1)">{{ $t('prev') }}</button>
      <span>{{ $t('page_label') }} {{ page }} / {{ totalPages }} (Total: {{ total }})</span>
      <button :disabled="page>=totalPages" @click="changePage(page+1)">{{ $t('next') }}</button>

      <label>{{ $t('jump_to') }}:
          <input type="number" v-model.number="jumpTo" min="1" :max="totalPages" />
        </label>
      <button @click="goToJump">{{ $t('go') }}</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Header from '../components/Header.vue'
import ShopCard from '../components/ShopCard.vue'
import api from '../api'

const q = ref('')
const sort = ref(localStorage.getItem('shop_sort') || 'recommended')
const shops = ref([])
const page = ref(1)
const page_size = ref(Number(localStorage.getItem('shop_page_size')) || 10)
const total = ref(0)
const jumpTo = ref(1)

const totalPages = computed(()=> Math.max(1, Math.ceil(total.value / page_size.value)))

async function fetchShops(){
  try{
    // persist sort preference
    localStorage.setItem('shop_sort', sort.value)
    localStorage.setItem('shop_page_size', String(page_size.value))
    const res = await api.get('/api/shops', { params: { q: q.value || undefined, sort: sort.value || undefined, page: page.value, page_size: page_size.value } })
    shops.value = res.data.items
    total.value = res.data.total
    // sync jumpTo
    jumpTo.value = page.value
  }catch(e){ console.warn(e) }
}

function changePage(p){
  if(p<1) p=1
  if(p>totalPages.value) p=totalPages.value
  page.value = p
  fetchShops()
}

function onPageSizeChange(){
  page.value = 1
  fetchShops()
}

function goToJump(){
  let p = Number(jumpTo.value) || 1
  if(p < 1) p = 1
  if(p > totalPages.value) p = totalPages.value
  page.value = p
  fetchShops()
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
