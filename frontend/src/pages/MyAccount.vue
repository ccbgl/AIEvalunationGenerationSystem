<template>
  <div class="page">
    <Header />
    <main>
      <h2>{{ $t('my') }}</h2>
      <div v-if="!loaded">Loading...</div>
      <div v-else>
        <div class="user-card">
          <div><strong>{{ user.username }}</strong> <span class="role">({{ user.role }})</span></div>
          <button @click="logout">{{ $t('logout') || 'Logout' }}</button>
        </div>

        <section class="section">
          <h3>My Collections</h3>
          <div v-if="collections.length===0">No collections</div>
          <ul>
            <li v-for="c in collections" :key="c.shop_id">
              <router-link :to="`/shop/${c.shop_id}`">{{ c.shop_name }}</router-link>
              <button @click="uncollect(c.shop_id)">Uncollect</button>
            </li>
          </ul>
        </section>

        <section class="section">
          <h3>Browse History</h3>
          <div v-if="history.length===0">No history</div>
          <ul>
            <li v-for="h in history" :key="h.id">
              <router-link :to="`/shop/${h.shop_id}`">{{ h.shop_name }}</router-link>
              <small>{{ formatTime(h.browse_time) }}</small>
              <button @click="deleteHistory(h.id)">Delete</button>
            </li>
          </ul>
          <div v-if="history.length>0"><button @click="clearHistory">Clear All History</button></div>
        </section>

        <section class="section">
          <h3>My Evaluations</h3>
          <div v-if="evaluations.length===0">No evaluations</div>
          <ul>
            <li v-for="e in evaluations" :key="e.id">
              <div><strong>Shop {{ e.shop_id }}</strong> · {{ e.level }} · {{ e.create_time }}</div>
              <div>{{ e.content }}</div>
            </li>
          </ul>

          <div class="pagination-controls">
            <label>Page size:
              <select v-model.number="page_size" @change="onPageSizeChange">
                <option :value="5">5</option>
                <option :value="10">10</option>
                <option :value="20">20</option>
              </select>
            </label>

            <button :disabled="page<=1" @click="changePage(page-1)">Prev</button>
            <span>Page {{ page }} / {{ totalPages }}</span>
            <button :disabled="page>=totalPages" @click="changePage(page+1)">Next</button>

            <label>Jump to:
              <input type="number" v-model.number="jumpTo" min="1" :max="totalPages" />
            </label>
            <button @click="goToJump">Go</button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import Header from '../components/Header.vue'
import api from '../api'
import { useRouter } from 'vue-router'

const user = ref(null)
const collections = ref([])
const history = ref([])
const evaluations = ref([])
const loaded = ref(false)
const router = useRouter()

// pagination state
const page = ref(1)
const page_size = ref(5)
const total = ref(0)
const jumpTo = ref(1)

const totalPages = computed(()=> Math.max(1, Math.ceil(total.value / page_size.value)))

function formatTime(ts){
  try{
    return new Date(ts).toLocaleString()
  }catch(e){ return ts }
}

async function load(){
  const token = localStorage.getItem('token')
  if(!token){
    router.push('/login')
    return
  }
  try{
    const me = await api.get('/api/auth/me')
    user.value = me.data
  }catch(e){
    localStorage.removeItem('token')
    router.push('/login')
    return
  }

  // load collections
  try{
    const res = await api.get('/api/collection')
    collections.value = res.data
  }catch(e){ console.warn('collections err', e) }

  // load history
  try{
    const res = await api.get('/api/history')
    history.value = res.data
  }catch(e){ console.warn('history err', e) }

  // load evaluations paginated
  await loadEvaluations()

  loaded.value = true
}

async function loadEvaluations(){
  try{
    const res = await api.get('/api/evaluations/user_paginated', { params: { page: page.value, page_size: page_size.value } })
    evaluations.value = res.data.items
    total.value = res.data.total
    // sync jumpTo with current page
    jumpTo.value = page.value
  }catch(e){ console.warn('evaluations err', e); evaluations.value = []; total.value = 0 }
}

function logout(){
  localStorage.removeItem('token')
  router.push('/login')
}

async function uncollect(shop_id){
  try{
    await api.delete('/api/collection', { params: { shop_id } })
    collections.value = collections.value.filter(c => c.shop_id !== shop_id)
  }catch(e){ alert('uncollect failed') }
}

async function deleteHistory(id){
  try{
    await api.delete(`/api/history/${id}`)
    history.value = history.value.filter(h => h.id !== id)
  }catch(e){ alert('delete failed') }
}

async function clearHistory(){
  try{
    await api.delete('/api/history')
    history.value = []
  }catch(e){ alert('clear failed') }
}

function changePage(p){
  if(p<1) p=1
  if(p>totalPages.value) p=totalPages.value
  page.value = p
  loadEvaluations()
}

function onPageSizeChange(){
  page.value = 1
  loadEvaluations()
}

function goToJump(){
  let p = Number(jumpTo.value) || 1
  if(p < 1) p = 1
  if(p > totalPages.value) p = totalPages.value
  page.value = p
  loadEvaluations()
}

onMounted(()=> load())
</script>

<style scoped>
.user-card{display:flex;justify-content:space-between;align-items:center;padding:8px;border:1px solid #eee;border-radius:6px;margin-bottom:12px}
.section{margin-top:16px}
.section ul{list-style:none;padding:0}
.section li{padding:8px;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center}
button{padding:6px 10px;border-radius:6px;border:none;background:#ff6b6b;color:#fff}
.pagination-controls{display:flex;align-items:center;gap:12px;margin-top:12px}
</style>
