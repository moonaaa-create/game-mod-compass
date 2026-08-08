<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { resetChat, sendChatMessage } from './api.js'

const INITIAL_SUGGESTIONS = [
  '로블록스 어드벤처 게임 추천해줘',
  '친구들이랑 하기 좋은 로블록스 게임 알려줘',
  '마인크래프트 기술 모드 추천해줘',
  '가벼운 마인크래프트 RPG 모드가 궁금해',
]

const chatLog = ref(null)
const draft = ref('')
const error = ref(null)
const isLoading = ref(false)
const isResetting = ref(false)
const conversationDone = ref(false)
const activeGameType = ref(null)
const recommendations = ref([])
const messages = ref([])

let nextMessageId = 0

const composerPlaceholder = computed(() => (
  conversationDone.value
    ? '새로 추천받기를 눌러 새로운 대화를 시작하세요.'
    : '예: 로블록스 어드벤처 게임 추천해줘'
))

const isSendDisabled = computed(() => (
  isLoading.value || conversationDone.value || draft.value.trim().length === 0
))

function createMessage(role, text, suggestions = []) {
  return {
    id: nextMessageId++,
    role,
    text,
    suggestions,
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (!chatLog.value) return
    chatLog.value.scrollTop = chatLog.value.scrollHeight
  })
}

function initializeConversation() {
  recommendations.value = []
  activeGameType.value = null
  conversationDone.value = false
  error.value = null
  draft.value = ''
  messages.value = [
    createMessage(
      'bot',
      '안녕하세요! 어떤 게임을 추천받고 싶으신가요? 자유롭게 이야기해주세요 :)',
      INITIAL_SUGGESTIONS,
    ),
  ]
  scrollToBottom()
}

function resultMeta(item) {
  if (activeGameType.value === 'roblox') {
    return `${item.genre} · 동접 ${Number(item.playing ?? 0).toLocaleString()}명`
  }
  return `다운로드 ${Number(item.download_count ?? 0).toLocaleString()}회`
}

function resultTags(item) {
  if (activeGameType.value === 'roblox') return []
  return item.loaders ?? []
}

async function handleSend(prefilledMessage = null) {
  const message = (prefilledMessage ?? draft.value).trim()
  if (!message || isLoading.value || conversationDone.value) return

  error.value = null
  draft.value = ''
  messages.value.push(createMessage('user', message))
  scrollToBottom()

  isLoading.value = true
  scrollToBottom()

  try {
    const response = await sendChatMessage(message)
    activeGameType.value = response.game_type ?? activeGameType.value
    recommendations.value = response.recommendations ?? []
    conversationDone.value = response.stage === 'done'
    messages.value.push(createMessage('bot', response.reply ?? '추천 내용을 준비했어요.'))
    scrollToBottom()
  } catch (err) {
    error.value = err.message
    scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

async function restartChat() {
  isResetting.value = true
  let resetError = null

  try {
    await resetChat()
  } catch (err) {
    resetError = err.message
  } finally {
    initializeConversation()
    if (resetError) {
      error.value = `서버 대화 초기화에 실패했어요: ${resetError}`
    }
    isResetting.value = false
  }
}

function useSuggestion(text) {
  draft.value = text
  void handleSend(text)
}

function avatar(role) {
  return role === 'bot' ? '🧭' : '🙂'
}

onMounted(() => {
  initializeConversation()
})
</script>

<template>
  <div class="app-shell">
    <div class="chat-shell">
      <div class="hero-panel">
        <div class="hero-kicker">AI GAME GUIDE</div>
        <div class="app-title">Game Mod Compass</div>
        <p class="hero-copy">로블록스 게임과 마인크래프트 모드를 자유롭게 대화하며 추천받아보세요.</p>
      </div>

      <div ref="chatLog" class="chat-log">
        <template v-for="message in messages" :key="message.id">
          <div class="message-row" :class="message.role">
            <div class="message-avatar">{{ avatar(message.role) }}</div>
            <div class="message-stack">
              <div class="chat-bubble" :class="message.role">{{ message.text }}</div>
              <div v-if="message.suggestions?.length && !conversationDone" class="chat-options">
                <button
                  v-for="suggestion in message.suggestions"
                  :key="suggestion"
                  class="chip"
                  type="button"
                  @click="useSuggestion(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>
          </div>
        </template>

        <div v-if="isLoading" class="message-row bot typing-row">
          <div class="message-avatar">🧭</div>
          <div class="message-stack">
            <div class="chat-bubble bot typing-bubble" aria-label="AI is typing">
              <span class="typing-dot" />
              <span class="typing-dot" />
              <span class="typing-dot" />
            </div>
          </div>
        </div>

        <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

        <div v-if="recommendations.length" class="chat-results">
          <div class="results-header">
            <div>
              <strong>추천 결과</strong>
              <p>{{ activeGameType === 'roblox' ? '로블록스 추천' : '마인크래프트 추천' }}</p>
            </div>
          </div>

          <div v-for="(item, idx) in recommendations" :key="item.id" class="chat-result-row">
            <div class="rank">{{ idx + 1 }}</div>
            <img
              class="chat-thumb"
              :src="item.thumbnail_url || item.logo_url"
              alt=""
              loading="lazy"
            />
            <div class="info">
              <div class="title">{{ item.name }}</div>
              <div class="meta">
                {{ resultMeta(item) }}
                <span v-for="tag in resultTags(item)" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>

          <button class="btn-ghost" type="button" :disabled="isResetting" @click="restartChat">
            🔄 새로 추천받기
          </button>
        </div>
      </div>

      <form class="composer" @submit.prevent="handleSend()">
        <textarea
          v-model="draft"
          class="composer-input"
          rows="1"
          :placeholder="composerPlaceholder"
          :disabled="isLoading || conversationDone"
          @keydown.enter.exact.prevent="handleSend()"
        />
        <button class="btn-send" type="submit" :disabled="isSendDisabled">
          {{ isLoading ? '전송 중' : '전송' }}
        </button>
      </form>
    </div>
  </div>
</template>
