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

const GREETING = '안녕하세요! 유스AI프로젝트 2기 2조에서 만든 Mod Compass입니다 🧭\n평소에 하시는 게임, 관심사, 취미 등을 알려주시면 그에 맞는 로블록스 게임이나 마인크래프트 모드를 추천해드릴게요!'

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function formatMessage(text) {
  let safe = escapeHtml(text || '')
  // 마크다운 링크 [텍스트](URL) -> 실제 클릭 가능한 링크
  safe = safe.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (m, label, url) => {
    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`
  })
  // 순수 URL도 자동 링크 처리 (마크다운 문법이 아닌 경우 대비)
  safe = safe.replace(/(^|[^"'>])(https?:\/\/[^\s<]+)/g, (m, pre, url) => {
    return `${pre}<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
  })
  // 굵게 표시용 마크다운(**텍스트**)은 어색한 AI 말투 느낌을 주므로 별표만 제거하고 일반 텍스트로 표시
  safe = safe.replace(/\*\*(.+?)\*\*/g, '$1')
  return safe.replace(/\n/g, '<br>')
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
  pushMessage('ai', GREETING)
}

function handleKeydown(e) {
  // 한글 등 IME 조합 중(글자를 완성하기 전) Enter가 눌리면 마지막 글자가 씹히고
  // 전송되는 문제를 막기 위해 조합 중일 때는 전송하지 않음
  if (e.isComposing || e.keyCode === 229) return
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
  pushMessage('ai', GREETING)
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
              <div class="bubble" :class="m.role" v-html="formatMessage(m.text)"></div>
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

.bubble :deep(a) {
  color: #93c5fd;
  text-decoration: underline;
  font-weight: 600;
  word-break: break-all;
}

.bubble.user :deep(a) {
  color: #dbeafe;
}

.bubble :deep(a:hover) {
  color: #bfdbfe;
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
  .chat-header {
    padding: 10px 12px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .logo {
    font-size: 1rem;
  }
  .header-actions {
    gap: 6px;
    width: 100%;
    justify-content: flex-start;
  }
  .header-btn {
    padding: 6px 10px;
    font-size: 0.78rem;
    flex: 1 1 auto;
    text-align: center;
  }
  .chat-body {
    padding: 0 10px;
  }
  .messages-scroll {
    padding: 14px 0;
  }
  .message-row {
    max-width: 96%;
    gap: 6px;
  }
  .avatar {
    width: 30px;
    height: 30px;
    min-width: 30px;
    font-size: 1rem;
  }
  .bubble {
    padding: 11px 14px;
    font-size: 0.95rem;
  }
  .suggestions {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 10px;
    -webkit-overflow-scrolling: touch;
  }
  .suggestion-chip {
    flex: 0 0 auto;
    white-space: nowrap;
    font-size: 0.82rem;
    padding: 7px 14px;
  }
  .input-bar {
    padding: 10px 0 calc(14px + env(safe-area-inset-bottom));
    gap: 8px;
  }
  .input-bar textarea {
    padding: 10px 14px;
    font-size: 0.95rem;
  }
  .send-btn {
    padding: 10px 16px;
    font-size: 0.92rem;
  }
}

@media (max-width: 380px) {
  .header-btn span {
    display: none;
  }
}
</style>
