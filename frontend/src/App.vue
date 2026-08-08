<script setup>
/**
 * 앱 셸: 페이지 전환(홈 <-> 채팅)과 테마(라이트/다크) 상태를 관리한다.
 * 팀원 디자인(main.html/chat.html)의 data-theme 속성을 <html> 루트에 반영해
 * 두 페이지가 하나의 테마 토글을 공유하도록 한다.
 */
import { onMounted, ref, watch } from 'vue'
import HomeView from './views/HomeView.vue'
import ChatView from './views/ChatView.vue'

const page = ref('home')
const theme = ref('light')

function applyTheme(value) {
  document.documentElement.setAttribute('data-theme', value)
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

watch(theme, (value) => {
  applyTheme(value)
  localStorage.setItem('theme', value)
})

onMounted(() => {
  const saved = localStorage.getItem('theme')
  theme.value = saved === 'dark' ? 'dark' : 'light'
  applyTheme(theme.value)
})

function goToChat() {
  page.value = 'chat'
}

function goToHome() {
  page.value = 'home'
}
</script>

<template>
  <HomeView
    v-if="page === 'home'"
    :theme="theme"
    @navigate-chat="goToChat"
    @toggle-theme="toggleTheme"
  />
  <ChatView v-else @navigate-home="goToHome" />
</template>
