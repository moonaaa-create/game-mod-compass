<script setup>
/**
 * 앱 셸: 페이지 전환(홈 <-> 참여자소개 <-> 채팅), 테마, 3D 엔진 일시정지 상태 관리
 */
import { onMounted, ref, watch } from 'vue'
import HomeView from './views/HomeView.vue'
import TeamView from './views/TeamView.vue'
import ChatView from './views/ChatView.vue'

const page = ref('home')
const theme = ref('light')
const isEnginePaused = ref(false)

function applyTheme(value) {
  document.documentElement.setAttribute('data-theme', value)
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
}

function toggleEnginePause() {
  isEnginePaused.value = !isEnginePaused.value
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

function goToTeam() {
  page.value = 'team'
}
</script>

<template>
  <HomeView
    v-if="page === 'home'"
    :theme="theme"
    :is-engine-paused="isEnginePaused"
    @navigate-chat="goToChat"
    @navigate-team="goToTeam"
    @toggle-theme="toggleTheme"
    @toggle-engine-pause="toggleEnginePause"
  />
  <TeamView
    v-else-if="page === 'team'"
    :theme="theme"
    :is-engine-paused="isEnginePaused"
    @navigate-home="goToHome"
    @navigate-chat="goToChat"
    @navigate-team="goToTeam"
    @toggle-theme="toggleTheme"
    @toggle-engine-pause="toggleEnginePause"
  />
  <ChatView
    v-else
    :is-engine-paused="isEnginePaused"
    @navigate-home="goToHome"
    @navigate-team="goToTeam"
    @toggle-engine-pause="toggleEnginePause"
  />
</template>
