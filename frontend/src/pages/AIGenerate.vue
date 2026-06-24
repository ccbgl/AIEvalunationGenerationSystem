<template>
  <div class="page"><Header />
    <main>
      <h2>AI Generate Review</h2>
      <form @submit.prevent="onGenerate">
        <label>Shop ID: <input v-model="shop_id" /></label>
        <label>Level:
          <select v-model="level">
            <option value="recommend">Recommend</option>
            <option value="general">General</option>
            <option value="bad">Bad</option>
          </select>
        </label>
        <label>Tags: <input v-model="tags" placeholder="comma separated"/></label>
        <label>Target Platform:
          <select v-model="target_platform">
            <option value="google">Google</option>
            <option value="xiaohongshu">小红书</option>
          </select>
        </label>
        <button type="submit">Generate</button>
      </form>

      <div v-if="loading">Generating...</div>
      <pre v-if="result">{{ result }}</pre>

      <div class="actions">
        <button @click="copyText">Copy to clipboard</button>
        <button @click="submitEval">Submit to site</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from '../components/Header.vue'
import api from '../api'

const shop_id = ref(1)
const level = ref('recommend')
const tags = ref('')
const target_platform = ref('google')
const loading = ref(false)
const result = ref('')

async function onGenerate(){
  loading.value = true
  try{
    const payload = { shop_id: Number(shop_id.value), level: level.value, tags: tags.value.split(',').map(s=>s.trim()).filter(Boolean), target_platform: target_platform.value }
    const res = await api.post('/api/evaluations/generate_authenticated', payload)
    result.value = res.data.content
  }catch(e){ result.value = 'Error: ' + (e.response?.data?.detail || e.message) }
  loading.value = false
}

function copyText(){
  if(!result.value) return alert('no content')
  navigator.clipboard.writeText(result.value).then(()=>alert('copied'))
}

async function submitEval(){
  if(!result.value) return alert('generate first')
  try{
    const payload = { shop_id: Number(shop_id.value), level: level.value, tags: tags.value.split(',').map(s=>s.trim()).filter(Boolean), target_platform: target_platform.value, content: result.value, is_ai: true }
    await api.post('/api/evaluations/', payload)
    alert('submitted')
  }catch(e){ alert('submit error') }
}
</script>

<style>
.page main{padding:12px}
form label{display:block;margin:8px 0}
button{padding:8px;background:#ff6b6b;color:#fff;border:none;border-radius:6px}
.actions{display:flex;gap:8px;margin-top:12px}
</style>
