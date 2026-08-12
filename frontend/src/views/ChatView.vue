<script setup>
/**
 * ChatView - 일반적인 메신저 스타일 채팅 UI
 * (기존 안티그래비티 물리엔진 말풍선 방식 대신, 읽고 대화하기 편한 표준 채팅 레이아웃으로 교체)
 */
import { nextTick, onMounted, ref } from 'vue'

const emit = defineEmits(['navigate-home', 'navigate-team', 'toggle-engine-pause'])

const API_URL = `${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/api/chat`

const messages = ref([])
const draft = ref('')
const isLoading = ref(false)
const messagesEl = ref(null)
const inputEl = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function pushMessage(role, text) {
  messages.value.push({
    role,
    text,
    time: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
  })
  scrollToBottom()
}

async function sendMessage() {
  const text = draft.value.trim()
  if (!text || isLoading.value) return

  pushMessage('user', text)
  draft.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    })

    if (res.ok) {
      const data = await res.json()
      pushMessage('ai', data.reply)
    } else {
      pushMessage('ai', '⚠️ 서버 에러가 발생했습니다. 잠시 후 다시 시도해주세요.')
    }
  } catch (err) {
    pushMessage('ai', '⚠️ 네트워크 연결에 실패했습니다. 인터넷 상태를 확인해주세요.')
  } finally {
    isLoading.value = false
    nextTick(() => inputEl.value?.focus())
  }
}

async function restartChat() {
  messages.value = []
  try {
    await fetch(`${API_URL}/reset`, { method: 'POST', credentials: 'include' })
  } catch (err) {
    // 세션 초기화 실패는 무시하고 화면만 리셋
  }
  pushMessage('ai', '안녕! 나는 Mod Compass의 AI 가이드야 🧭\n마인크래프트 모드나 로블록스 게임, 궁금한 거 편하게 물어봐!')
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const suggestions = [
  '마인크래프트 자동화 모드 추천해줘',
  '로블록스에서 친구랑 할만한 게임 추천해줘',
  '저사양 PC에서도 잘 돌아가는 모드 있어?',
]

function useSuggestion(text) {
  draft.value = text
  sendMessage()
}

onMounted(() => {
  pushMessage('ai', '안녕! 나는 Mod Compass의 AI 가이드야 🧭\n마인크래프트 모드나 로블록스 게임, 궁금한 거 편하게 물어봐!')
  inputEl.value?.focus()
})
</script>

<template>
  <div class="chat-page">
    <header class="chat-header">
      <button class="logo" type="button" @click="emit('navigate-home')">
        🧭 Mod Compass
      </button>
      <div class="header-actions">
        <button class="header-btn" type="button" @click="emit('navigate-home')">
          🏠 프로젝트 소개
        </button>
        <button class="header-btn" type="button" @click="emit('navigate-team')">
          👥 참여자 소개
        </button>
        <button class="header-btn" type="button" @click="restartChat">
          🔄 새 대화
        </button>
      </div>
    </header>

    <main class="chat-body">
      <div ref="messagesEl" class="messages-scroll">
        <div class="messages-inner">
          <div
            v-for="(m, idx) in messages"
            :key="idx"
            class="message-row"
            :class="m.role"
          >
            <div class="avatar" :class="m.role">{{ m.role === 'user' ? '🙂' : '🤖' }}</div>
            <div class="bubble-wrap">
              <div class="bubble" :class="m.role">{{ m.text }}</div>
              <span class="timestamp">{{ m.time }}</span>
            </div>
          </div>

          <div v-if="isLoading" class="message-row ai">
            <div class="avatar ai">🤖</div>
            <div class="bubble-wrap">
              <div class="bubble ai typing">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="messages.length <= 1" class="suggestions">
        <button
          v-for="(s, i) in suggestions"
          :key="i"
          class="suggestion-chip"
          type="button"
          @click="useSuggestion(s)"
        >
          {{ s }}
        </button>
      </div>

      <form class="input-bar" @submit.prevent="sendMessage">
        <textarea
          ref="inputEl"
          v-model="draft"
          rows="1"
          placeholder="궁금한 게임이나 모드를 물어보세요..."
          :disabled="isLoading"
          @keydown="handleKeydown"
        ></textarea>
        <button type="submit" class="send-btn" :disabled="isLoading || !draft.trim()">
          {{ isLoading ? '전송 중...' : '전송 ➤' }}
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
.chat-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: #f1f5f9;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: rgba(15, 23, 42, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  z-index: 10;
}

.logo {
  background: none;
  border: none;
  color: #ffffff;
  font-weight: 700;
  font-size: 1.15rem;
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #f1f5f9;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.header-btn:hover {
  background: rgba(255, 255, 255, 0.18);
}

.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
  padding: 0 16px;
}

.messages-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
}

.messages-inner {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  max-width: 85%;
}

.message-row.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background: rgba(255, 255, 255, 0.1);
}

.avatar.user {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.avatar.ai {
  background: linear-gradient(135deg, #a855f7, #7e22ce);
}

.bubble-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-row.user .bubble-wrap {
  align-items: flex-end;
}

.bubble {
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 1rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.bubble.user {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.bubble.ai {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #f1f5f9;
  border-bottom-left-radius: 4px;
}

.bubble.typing {
  display: flex;
  gap: 5px;
  padding: 16px 20px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) { animation-delay: 0.15s; }
.dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-6px); opacity: 1; }
}

.timestamp {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  padding: 0 4px;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-bottom: 12px;
}

.suggestion-chip {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s, transform 0.15s;
}

.suggestion-chip:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-1px);
}

.input-bar {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 14px 0 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.input-bar textarea {
  flex: 1;
  resize: none;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: #ffffff;
  padding: 12px 18px;
  font-size: 1rem;
  font-family: inherit;
  outline: none;
  max-height: 140px;
}

.input-bar textarea::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.input-bar textarea:focus {
  border-color: #3b82f6;
}

.send-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border: none;
  padding: 12px 22px;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.15s, opacity 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .header-actions {
    gap: 4px;
  }
  .header-btn {
    padding: 6px 10px;
    font-size: 0.8rem;
  }
  .message-row {
    max-width: 92%;
  }
}
</style>
