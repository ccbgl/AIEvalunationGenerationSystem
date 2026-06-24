<template>
  <div>
    <h2>Shop {{ id }}</h2>
    <router-link to="/">Back</router-link>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
const id = route.params.id
</script>
