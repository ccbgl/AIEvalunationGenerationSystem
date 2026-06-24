<template>
  <header class="app-header">
    <div class="brand"><router-link to="/">Sunny Tea House</router-link></div>
    <nav>
      <router-link to="/">Shops</router-link>
      <router-link to="/ai">AI Generate</router-link>
      <router-link v-if="!logged" to="/login">Login</router-link>
      <router-link v-if="!logged" to="/register">Register</router-link>
      <router-link v-if="logged" to="/me">My</router-link>
    </nav>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
const logged = computed(()=> !!localStorage.getItem('token'))
</script>

<style scoped>
.app-header{display:flex;align-items:center;justify-content:space-between;padding:12px;background:#fff;border-bottom:1px solid #f0f0f0}
.brand a{font-weight:700;color:#ff6b6b;text-decoration:none}
nav a{margin-left:12px;color:#333;text-decoration:none}
</style>
