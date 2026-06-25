<template>
  <div class="page"><Header />
    <main>
      <h2>{{ $t('ai_generate') }}</h2>
      <form @submit.prevent="onGenerate">
        <label>{{ $t('shops') }} ID: <input v-model="shop_id" /></label>
        <label>Level:
          <select v-model="level">
            <option value="recommend">{{ $t('level_recommend') }}</option>
            <option value="general">{{ $t('level_general') }}</option>
            <option value="bad">{{ $t('level_bad') }}</option>
          </select>
        </label>
        <label>Tags: <input v-model="tags" placeholder="service,fast"/></label>
        <label>Target Platform:
          <select v-model="target_platform">
            <option value="google">Google</option>
            <option value="xiaohongshu">小红书</option>
          </select>
        </label>
            <div style="margin-top:8px">{{ $t('remaining_today') }}: <strong>{{ remaining }}</strong></div>
            <button type="submit" :disabled="loading || remaining<=0">{{ $t('generate') }}</button>
          </form>

          <div v-if="loading">{{ $t('generating') }}</div>
          <div v-if="result">
            <textarea v-model="result" rows="6" style="width:100%"></textarea>
          </div>

          <div class="actions">
            <button @click="copyText">{{ $t('copy') }}</button>
            <button @click="copyAndOpen" :disabled="!result">{{ $t('copy_and_open') }}</button>
            <button @click="submitEval" :disabled="!result">{{ $t('submit') }}</button>
          </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Header from '../components/Header.vue'
import api from '../api'

const { t } = useI18n()
const shop_id = ref(1)
const level = ref('recommend')
const tags = ref('')
const target_platform = ref('google')
const loading = ref(false)
const result = ref('')
const remaining = ref(0)
const shop_name = ref('')

async function loadShop(){
  try{
    const res = await api.get(`/api/shops/${Number(shop_id.value)}`)
    shop_name.value = res.data.shop_name || ''
  }catch(e){ shop_name.value = '' }
}

async function onGenerate(){
  loading.value = true
  try{
    await loadShop()
    const payload = { shop_id: Number(shop_id.value), level: level.value, tags: tags.value.split(',').map(s=>s.trim()).filter(Boolean), target_platform: target_platform.value }
    const res = await api.post('/api/evaluations/generate_authenticated', payload)
    result.value = res.data.content
    if(res.data.remaining !== undefined) remaining.value = res.data.remaining
  }catch(e){ result.value = 'Error: ' + (e.response?.data?.detail || e.message) }
  loading.value = false
}

function copyText(){
  if(!result.value) return alert(t('no_content'))
  navigator.clipboard.writeText(result.value).then(()=>alert(t('copied')))
}

function copyAndOpen(){
  if(!result.value) return alert(t('no_content'))
  navigator.clipboard.writeText(result.value).then(()=>{
    // open a relevant platform URL - best-effort
    let url = ''
    const name = shop_name.value || ''
    if(target_platform.value === 'google'){
      url = 'https://www.google.com/search?q=' + encodeURIComponent(name || shop_id.value)
    }else{
      url = 'https://www.xiaohongshu.com/search_result?keyword=' + encodeURIComponent(name || shop_id.value)
    }
    window.open(url, '_blank')
  })
}

async function submitEval(){
  if(!result.value) return alert(t('please_generate_first'))
  try{
    const payload = { shop_id: Number(shop_id.value), level: level.value, tags: tags.value.split(',').map(s=>s.trim()).filter(Boolean), target_platform: target_platform.value, content: result.value, is_ai: true }
    await api.post('/api/evaluations/', payload)
    alert(t('submit_success'))
  }catch(e){ alert(t('submit_failed')) }
}
</script>

<style>
.page main{padding:12px}
form label{display:block;margin:8px 0}
button{padding:8px;background:#ff6b6b;color:#fff;border:none;border-radius:6px}
.actions{display:flex;gap:8px;margin-top:12px}
</style>