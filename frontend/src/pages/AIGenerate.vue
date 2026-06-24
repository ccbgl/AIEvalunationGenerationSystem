<template>
  <div>
    <h2>AI 评价生成</h2>
    <form @submit.prevent="onSubmit">
      <label>Shop ID: <input v-model="form.shop_id" /></label><br />
      <label>Level: <select v-model="form.level"><option>recommend</option><option>general</option><option>bad</option></select></label><br />
      <label>Tags: <input v-model="tags" placeholder="comma separated"/></label><br />
      <label>Target Platform: <select v-model="form.target_platform"><option>google</option><option>xiaohongshu</option></select></label><br />
      <button type="submit">Generate</button>
    </form>
    <pre>{{ result }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
const form = ref({ shop_id: 1, level: 'recommend', tags: [], target_platform: 'google' })
const tags = ref('')
const result = ref('')

async function onSubmit(){
  form.value.tags = tags.value.split(',').map(s=>s.trim()).filter(Boolean)
  try{
    const res = await axios.post('/api/ai/generate?token=demo', form.value)
    result.value = res.data.content
  }catch(e){
    result.value = 'error: ' + e
  }
}
</script>
