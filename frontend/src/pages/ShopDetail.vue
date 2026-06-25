<template>
  <div class="page"><Header />
    <main>
      <div v-if="!shop">Loading...</div>
      <div v-else>
        <h2>{{ shop.shop_name }}</h2>
        <img :src="shop.cover_image || '/static/img/cover.jpg'" alt="cover" style="width:100%;height:160px;object-fit:cover;border-radius:8px"/>
        <div class="meta">{{ shop.description }}</div>
        <div class="meta">{{ $t('avg') }}: ${{ shop.avg_cost }} · {{ $t('good_rate') }}: {{ shop.good_rate }}%</div>
        <div class="actions">
          <router-link to="/">{{ $t('back') }}</router-link>
          <router-link to="/ai">{{ $t('ai_generate') }}</router-link>
        </div>

        <section style="margin-top:16px">
          <h3>{{ $t('evaluations_title') }}</h3>
                    <div v-if="loadingE">{{ $t('loading_evaluations') }}</div>
          <div v-else>
                      <div v-if="evaluations.length===0">{{ $t('no_evaluations') }}</div>
            <div v-for="ev in evaluations" :key="ev.id" class="eval">
              <div class="eval-header"><strong>{{ ev.username }}</strong> · {{ ev.level }} · {{ ev.create_time }}</div>
              <div class="eval-content" style="white-space:pre-wrap">{{ ev.content }}</div>
              <div class="eval-actions">
                          <button @click="toggleLike(ev)">{{ ev.liked ? $t('unlike') : $t('like') }} ({{ ev.like_count }})</button>
                          <button @click="ev.showReply = !ev.showReply">{{ $t('reply') }} ({{ ev.reply_count }})</button>
              </div>

              <div v-if="ev.showReply" class="reply-box">
                          <textarea v-model="ev.newReply" rows="2" style="width:100%" :placeholder="$t('write_reply_placeholder')"></textarea>
                <div style="display:flex;gap:8px;margin-top:6px">
                            <button @click="submitReply(ev)">{{ $t('submit_reply') }}</button>
                            <button @click="ev.showReply=false">{{ $t('cancel') }}</button>
                </div>
              </div>

              <div class="replies" v-if="ev.replies && ev.replies.length>0">
                <div v-for="r in ev.replies" :key="r.id" class="reply-item">
                  <div><strong>{{ r.username }}</strong> · {{ r.role }} · {{ r.create_time }}</div>
                  <div>{{ r.content }}</div>
                </div>
              </div>

            </div>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import Header from '../components/Header.vue'
import api from '../api'

const { t } = useI18n()

const route = useRoute()
const shop = ref(null)
const evaluations = ref([])
const loadingE = ref(false)

async function load(){
  try{
    const res = await api.get(`/api/shops/${route.params.id}`)
    shop.value = res.data
  }catch(e){ console.warn(e) }
}

async function loadEvals(){
  loadingE.value = true
  try{
    const res = await api.get(`/api/evaluations/shop/${route.params.id}`)
    evaluations.value = res.data.map(ev => ({ ...ev, showReply: false, newReply: '' }))
  }catch(e){ console.warn('load evals', e) }
  loadingE.value = false
}

async function toggleLike(ev){
  try{
    const res = await api.post(`/api/evaluations/${ev.id}/like`)
    // toggle based on response
    if(res.data && res.data.liked!==undefined){
      ev.liked = res.data.liked
      // adjust count
      ev.like_count = ev.liked ? ev.like_count+1 : Math.max(0, ev.like_count-1)
    }else{
      // fallback: refresh list
      await loadEvals()
    }
  }catch(e){ console.warn('like error', e) }
}

async function submitReply(ev){
  if(!ev.newReply) return alert(t('reply_empty'))
  try{
    const payload = { content: ev.newReply }
    await api.post(`/api/evaluations/${ev.id}/reply`, payload)
    ev.newReply = ''
    ev.showReply = false
    // refresh evaluations
    await loadEvals()
  }catch(e){ alert(t('reply_failed')) }
}

onMounted(()=>{ load(); loadEvals() })
</script>

<style>
.meta{margin:8px 0;color:#555}
.actions{display:flex;gap:8px;margin-top:12px}
.eval{border:1px solid #eee;padding:8px;border-radius:6px;margin:8px 0}
.eval-header{color:#333;margin-bottom:6px}
.eval-actions{margin-top:6px}
.reply-item{border-left:2px solid #f0f0f0;padding-left:8px;margin-top:6px}
</style>
