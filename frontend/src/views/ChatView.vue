<script setup>
/**
 * 팀원 디자인 docs/ai agent/chat.html의 플로팅 필(pill) 네브바 + 글래스 채팅 카드 스타일을
 * 그대로 이식했다.
 *
 * ⚠️ 임시 조치: 백엔드 /api/chat fetch 연결에서 오류가 발생해 급한 대로 AI 연동을 끄고,
 * 정해진 대본(로컬 규칙 기반 시나리오)으로 동작하도록 변경했다. 네트워크 요청 없이
 * 클라이언트에서만 대화를 진행하며, 나중에 AI 연결을 다시 붙일 때는 handleSend 내부의
 * runScriptedTurn() 호출을 sendChatMessage() 호출로 되돌리면 된다.
 */
import { computed, nextTick, onMounted, ref } from 'vue'

const emit = defineEmits(['navigate-home'])

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

// 대본형 대화 상태 (백엔드 없이 로컬에서만 관리)
const scriptState = ref({ gameType: null, genre: null, category: null, size: null })

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
  scriptState.value = { gameType: null, genre: null, category: null, size: null }
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

// --- 정해진 대본(로컬 규칙 기반) 데이터 -------------------------------------

const ROBLOX_CATALOG = {
  '어드벤처': [
    { name: '⚔️ Blox Fruits', playing: 334490, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a64f70da20fc1e80ee76fe5d49c1be0a/150/150/Image/Png/noFilter' },
    { name: 'DOORS 👁️', playing: 13348, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-53f81a48fb348823169b97fd42a1094a/150/150/Image/Png/noFilter' },
    { name: 'Build A Boat For Treasure', playing: 18045, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a16e27d3d8380da38b43960549590ca2/150/150/Image/Png/noFilter' },
    { name: '🏝️ OFFROAD 🏝️ Driving Empire 🏎️', playing: 63501, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-ae0b1c314ffcf425584d23023492bba6/150/150/Image/Png/noFilter' },
    { name: 'Tower of Hell', playing: 21346, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-9704151d9c8a70e7ebe0ced8cb2b95c1/150/150/Image/Png/noFilter' },
  ],
  '시뮬레이터': [
    { name: 'Adopt Me!', playing: 187234, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a64f70da20fc1e80ee76fe5d49c1be0a/150/150/Image/Png/noFilter' },
    { name: 'Bee Swarm Simulator', playing: 24310, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-9704151d9c8a70e7ebe0ced8cb2b95c1/150/150/Image/Png/noFilter' },
    { name: 'Pet Simulator 99', playing: 41203, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a16e27d3d8380da38b43960549590ca2/150/150/Image/Png/noFilter' },
    { name: 'Mining Simulator 2', playing: 15872, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-53f81a48fb348823169b97fd42a1094a/150/150/Image/Png/noFilter' },
    { name: 'Anime Fighting Simulator', playing: 12044, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-ae0b1c314ffcf425584d23023492bba6/150/150/Image/Png/noFilter' },
  ],
  '롤플레이': [
    { name: 'Brookhaven 🏡RP', playing: 98211, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-9704151d9c8a70e7ebe0ced8cb2b95c1/150/150/Image/Png/noFilter' },
    { name: 'Welcome to Bloxburg', playing: 45120, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a64f70da20fc1e80ee76fe5d49c1be0a/150/150/Image/Png/noFilter' },
    { name: 'Royale High', playing: 33210, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a16e27d3d8380da38b43960549590ca2/150/150/Image/Png/noFilter' },
    { name: 'MeepCity', playing: 9021, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-53f81a48fb348823169b97fd42a1094a/150/150/Image/Png/noFilter' },
    { name: 'Berry Avenue RP', playing: 27650, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-ae0b1c314ffcf425584d23023492bba6/150/150/Image/Png/noFilter' },
  ],
  '오비': [
    { name: 'Tower of Hell', playing: 21346, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-9704151d9c8a70e7ebe0ced8cb2b95c1/150/150/Image/Png/noFilter' },
    { name: 'Mega Fun Obby', playing: 8213, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a64f70da20fc1e80ee76fe5d49c1be0a/150/150/Image/Png/noFilter' },
    { name: 'Speed Run 4', playing: 6102, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a16e27d3d8380da38b43960549590ca2/150/150/Image/Png/noFilter' },
    { name: 'Escape Obby', playing: 4310, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-53f81a48fb348823169b97fd42a1094a/150/150/Image/Png/noFilter' },
    { name: 'Obby Race Clicker', playing: 3987, thumbnail_url: 'https://tr.rbxcdn.com/180DAY-ae0b1c314ffcf425584d23023492bba6/150/150/Image/Png/noFilter' },
  ],
}

const MINECRAFT_CATALOG = {
  '기술': [
    { name: 'Create: Mechanical Craft', download_count: 51204000, loaders: ['Forge'] },
    { name: 'Applied Energistics', download_count: 43102000, loaders: ['Fabric'] },
    { name: 'Industrial Foundry', download_count: 30211000, loaders: ['Forge'] },
    { name: 'Tech Reactor Core', download_count: 21044000, loaders: ['NeoForge'] },
    { name: 'AutoMate Factory', download_count: 15720000, loaders: ['Forge'] },
  ],
  '마법': [
    { name: 'Thaumaturgy', download_count: 49066847, loaders: ['Forge'] },
    { name: 'Wizardry', download_count: 48059506, loaders: ['Fabric'] },
    { name: 'Arcane Grimoire', download_count: 31022000, loaders: ['Forge'] },
    { name: 'Mystic Runes', download_count: 24310000, loaders: ['NeoForge'] },
    { name: 'Enchanted Realms', download_count: 18204000, loaders: ['Fabric'] },
  ],
  '모험/RPG': [
    { name: 'Epic Quest Adventures', download_count: 44210000, loaders: ['Forge'] },
    { name: 'Dungeon Delve RPG', download_count: 39120000, loaders: ['Fabric'] },
    { name: 'Legends Untold', download_count: 27204000, loaders: ['Forge'] },
    { name: 'Roguelike Ruins', download_count: 19882000, loaders: ['NeoForge'] },
    { name: 'Heroes Journey', download_count: 14022000, loaders: ['Fabric'] },
  ],
  '지도 정보': [
    { name: 'Atlas', download_count: 48472722, loaders: ['Forge'] },
    { name: 'JourneyMap Plus', download_count: 41203000, loaders: ['Fabric'] },
    { name: 'Xaero Waypoints', download_count: 33021000, loaders: ['Forge'] },
    { name: 'World Compass', download_count: 22104000, loaders: ['NeoForge'] },
    { name: 'MapPin Tracker', download_count: 16820000, loaders: ['Fabric'] },
  ],
}

function matchGameType(text) {
  if (/로블록스|roblox/i.test(text)) return 'roblox'
  if (/마인크래프트|마크|minecraft/i.test(text)) return 'minecraft'
  return null
}

function matchRobloxGenre(text) {
  if (/어드벤처|모험/.test(text)) return '어드벤처'
  if (/시뮬레이터|시뮬/.test(text)) return '시뮬레이터'
  if (/롤플레이|알피지|롤플/.test(text)) return '롤플레이'
  if (/오비|장애물|파쿠르/.test(text)) return '오비'
  return null
}

function matchMinecraftCategory(text) {
  if (/기술|테크/.test(text)) return '기술'
  if (/마법|매직/.test(text)) return '마법'
  if (/모험|알피지|rpg/i.test(text)) return '모험/RPG'
  if (/지도|맵/.test(text)) return '지도 정보'
  return null
}

function matchSize(text) {
  if (/대규모|친구|다\s*같이|여럿|멀티/.test(text)) return 'large'
  if (/혼자|소규모|편하게|캐주얼/.test(text)) return 'small'
  return null
}

const ROBLOX_GENRE_SUGGESTIONS = ['어드벤처', '시뮬레이터', '롤플레이', '오비']
const MINECRAFT_CATEGORY_SUGGESTIONS = ['기술', '마법', '모험/RPG', '지도 정보']
const SIZE_SUGGESTIONS = ['친구들이랑 대규모로', '혼자 소규모로 편하게']

/**
 * 백엔드 없이 로컬 규칙만으로 다음 대화 단계를 진행한다 (정해진 대본).
 * 반환값은 /api/chat 응답 형태(reply/stage/game_type/recommendations)와 동일하게 맞춰
 * 기존 handleSend 로직을 그대로 재사용할 수 있게 한다.
 */
function runScriptedTurn(message) {
  const state = scriptState.value
  const gameType = matchGameType(message) || state.gameType
  state.gameType = gameType

  if (!gameType) {
    return {
      reply: '로블록스와 마인크래프트 중 어떤 걸 추천받고 싶으신가요?',
      stage: 'chatting',
      game_type: null,
      recommendations: null,
    }
  }

  if (gameType === 'roblox') {
    const genre = matchRobloxGenre(message) || state.genre
    state.genre = genre
    if (!genre) {
      return {
        reply: '좋아요! 로블록스에서 어떤 장르를 좋아하세요? (어드벤처 / 시뮬레이터 / 롤플레이 / 오비)',
        stage: 'chatting',
        game_type: 'roblox',
        recommendations: null,
      }
    }

    const size = matchSize(message) || state.size
    state.size = size
    if (!size) {
      return {
        reply: '친구들이랑 다 같이 할 대규모 멀티가 좋으세요, 아니면 혼자/소규모가 편하세요?',
        stage: 'chatting',
        game_type: 'roblox',
        recommendations: null,
      }
    }

    const sizeText = size === 'large' ? '대규모 멀티' : '소규모/캐주얼'
    return {
      reply: `좋아요! ${genre} 취향과 ${sizeText} 선호를 바탕으로 로블록스 추천 5개를 골라봤어요.`,
      stage: 'done',
      game_type: 'roblox',
      recommendations: (ROBLOX_CATALOG[genre] ?? []).map((item, idx) => ({
        id: idx + 1,
        name: item.name,
        genre,
        playing: item.playing,
        thumbnail_url: item.thumbnail_url,
      })),
    }
  }

  // minecraft
  const category = matchMinecraftCategory(message) || state.category
  state.category = category
  if (!category) {
    return {
      reply: '마인크래프트에서는 어떤 카테고리가 궁금하세요? (기술 / 마법 / 모험·RPG / 지도 정보)',
      stage: 'chatting',
      game_type: 'minecraft',
      recommendations: null,
    }
  }

  return {
    reply: `좋아요! ${category} 성향에 맞춰 마인크래프트 모드 추천 5개를 준비했어요.`,
    stage: 'done',
    game_type: 'minecraft',
    recommendations: (MINECRAFT_CATALOG[category] ?? []).map((item, idx) => ({
      id: idx + 1,
      name: item.name,
      download_count: item.download_count,
      loaders: item.loaders,
    })),
  }
}

function nextSuggestions(response) {
  if (response.stage === 'done') return []
  if (!response.game_type) return ['로블록스', '마인크래프트']
  if (response.game_type === 'roblox' && !scriptState.value.genre) return ROBLOX_GENRE_SUGGESTIONS
  if (response.game_type === 'roblox' && !scriptState.value.size) return SIZE_SUGGESTIONS
  if (response.game_type === 'minecraft' && !scriptState.value.category) return MINECRAFT_CATEGORY_SUGGESTIONS
  return []
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

  // 대본형 로컬 응답 - 자연스러운 타이핑 느낌을 위한 약간의 지연만 둔다 (네트워크 요청 없음)
  await new Promise((resolve) => setTimeout(resolve, 450))

  const response = runScriptedTurn(message)
  activeGameType.value = response.game_type ?? activeGameType.value
  recommendations.value = response.recommendations ?? []
  conversationDone.value = response.stage === 'done'
  messages.value.push(createMessage('bot', response.reply ?? '추천 내용을 준비했어요.', nextSuggestions(response)))
  scrollToBottom()

  isLoading.value = false
}

async function restartChat() {
  isResetting.value = true
  initializeConversation()
  isResetting.value = false
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
  <div class="chat-page">
    <div class="chat-nav-wrapper">
      <header class="chat-pill-nav">
        <button class="pill-logo" type="button" @click="emit('navigate-home')">
          <span class="pill-tag">AI COMPASS</span>
          Game Mod Compass
        </button>
        <div class="pill-actions">
          <button class="pill-btn" type="button" @click="emit('navigate-home')">프로젝트 소개</button>
          <button class="pill-btn" type="button" :disabled="isResetting" @click="restartChat">
            채팅 초기화 🔄
          </button>
        </div>
      </header>
    </div>

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

<style scoped>
.chat-page {
  width: 100%;
  min-height: 100vh;
  background: var(--chat-bg-gradient);
  color: var(--chat-text-main);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 96px 16px 20px;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-nav-wrapper {
  position: fixed;
  top: 20px;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0 20px;
  z-index: 100;
}

.chat-pill-nav {
  width: 100%;
  max-width: 900px;
  background: var(--chat-header-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--chat-border);
  padding: 10px 24px;
  border-radius: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.pill-logo {
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: var(--chat-text-main);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.pill-tag {
  font-size: 0.75rem;
  color: var(--chat-accent);
  font-weight: 700;
}

.pill-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.pill-btn {
  padding: 8px 16px;
  background-color: var(--chat-btn-bg);
  color: var(--chat-btn-text);
  font-size: 0.85rem;
  font-weight: 600;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover:not(:disabled) {
  background-color: var(--chat-btn-hover);
  transform: translateY(-2px);
}

.pill-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-shell {
  width: 100%;
  max-width: 900px;
  min-height: calc(100vh - 140px);
  background: var(--chat-card-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--chat-border);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  overflow: hidden;
}

.hero-panel {
  padding: 16px 24px;
  border-bottom: 1px solid var(--chat-border);
}

.hero-kicker {
  color: var(--chat-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.app-title {
  margin-top: 6px;
  font-size: 1.3rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.hero-copy {
  margin: 6px 0 0;
  color: var(--chat-text-sub);
  font-size: 0.9rem;
  line-height: 1.5;
}

.chat-log {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.message-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  animation: message-in 0.24s ease-out;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.user .message-stack {
  align-items: flex-end;
}

.message-row.user .message-avatar {
  order: 2;
}

.message-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: min(720px, 86%);
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--chat-ai-bg);
  border: 1px solid var(--chat-border);
  flex-shrink: 0;
  font-size: 16px;
}

.message-row.user .message-avatar {
  background: var(--chat-user-bg);
}

.chat-bubble {
  max-width: 100%;
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 0.95rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: keep-all;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.chat-bubble.bot {
  background-color: var(--chat-ai-bg);
  color: var(--chat-ai-text);
  border: 1px solid var(--chat-border);
  border-bottom-left-radius: 4px;
}

.chat-bubble.user {
  background-color: var(--chat-user-bg);
  color: var(--chat-user-text);
  border-bottom-right-radius: 4px;
}

.chat-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--chat-border);
  background: var(--chat-ai-bg);
  color: var(--chat-text-main);
  font-size: 13px;
  transition: transform 0.18s ease, border-color 0.18s ease;
}

.chip:hover {
  transform: translateY(-1px);
  border-color: var(--chat-accent);
}

.typing-row {
  margin-bottom: 4px;
}

.typing-bubble {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--chat-text-sub);
  animation: typing-pulse 1s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

.chat-results {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px;
  border-radius: 20px;
  background: var(--chat-ai-bg);
  border: 1px solid var(--chat-border);
  animation: message-in 0.24s ease-out;
}

.results-header p {
  margin: 6px 0 0;
  color: var(--chat-text-sub);
  font-size: 13px;
}

.chat-result-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--chat-bg-gradient);
  border: 1px solid var(--chat-border);
  border-radius: 16px;
  padding: 12px 14px;
}

.chat-result-row .rank {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--chat-accent);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 13px;
  flex-shrink: 0;
}

.chat-thumb {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  object-fit: cover;
  flex-shrink: 0;
  background: var(--chat-btn-bg);
}

.chat-result-row .info {
  flex: 1;
  min-width: 0;
}

.chat-result-row .title {
  font-weight: 700;
  font-size: 15px;
}

.chat-result-row .meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  font-size: 12px;
  color: var(--chat-text-sub);
  margin-top: 4px;
}

.tag {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--chat-btn-bg);
  color: var(--chat-btn-text);
  display: inline-block;
}

.btn-ghost {
  align-self: flex-start;
  background: transparent;
  color: var(--chat-text-main);
  border: 1px solid var(--chat-border);
  padding: 10px 16px;
  border-radius: 14px;
  font-size: 14px;
  transition: border-color 0.18s ease, transform 0.18s ease;
}

.btn-ghost:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: var(--chat-accent);
}

.btn-ghost:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-banner {
  background: rgba(225, 29, 72, 0.1);
  border: 1px solid #e11d48;
  color: #e11d48;
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 14px;
}

.composer {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  padding: 16px 24px;
  border-top: 1px solid var(--chat-border);
}

.composer-input {
  flex: 1;
  min-height: 48px;
  max-height: 160px;
  resize: none;
  border: 1px solid var(--chat-border);
  border-radius: 24px;
  background: transparent;
  color: var(--chat-text-main);
  padding: 13px 20px;
  font-size: 0.95rem;
  line-height: 1.5;
  outline: none;
  transition: border-color 0.18s ease;
}

.composer-input::placeholder {
  color: var(--chat-text-sub);
}

.composer-input:focus {
  border-color: var(--chat-accent);
}

.composer-input:disabled {
  opacity: 0.68;
  cursor: not-allowed;
}

.btn-send {
  border: none;
  min-width: 84px;
  min-height: 48px;
  padding: 0 24px;
  border-radius: 30px;
  background-color: var(--chat-btn-bg);
  color: var(--chat-btn-text);
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-send:hover:not(:disabled) {
  background-color: var(--chat-btn-hover);
}

.btn-send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@keyframes message-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes typing-pulse {
  0%, 80%, 100% { opacity: 0.35; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-3px); }
}

@media (max-width: 640px) {
  .chat-page {
    padding-top: 130px;
  }

  .chat-pill-nav {
    flex-direction: column;
    gap: 10px;
    border-radius: 24px;
  }

  .message-stack {
    max-width: calc(100% - 48px);
  }

  .composer {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-send {
    width: 100%;
  }
}
</style>
