<template>
  <div>
    <label>Content</label>
    <textarea v-model="model.content" rows="6" placeholder="AI or manual content" />
    <div class="row">
      <button @click="$emit('generate')">AI Generate</button>
      <button @click="$emit('submit')">Submit</button>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
const props = defineProps({ value: Object })
const model = reactive({ content: props.value?.content || '' })
</script>

<style scoped>
textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px}
.row{display:flex;gap:8px;margin-top:8px}
button{flex:1;padding:8px;border-radius:6px;border:none;background:#ff6b6b;color:#fff}
</style>
