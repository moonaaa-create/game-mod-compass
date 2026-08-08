<script setup>
/**
 * 취향 설문 → 추천 결과 챗봇 UI (docs/spec.md 섹션 7, #9 프로토타입 Variant C 채택안).
 *
 * 대화 흐름은 상태 머신으로 모델링:
 *   pick_game -> (roblox: genres -> player_size) | (minecraft: categories) -> submitting -> results
 */
import { computed, reactive, ref } from 'vue'
import { submitMinecraftSurvey, submitRobloxSurvey } from './api.js'

const ROBLOX_GENRES = [
  'Adventure', 'RPG', 'Simulation', 'Horror', 'Obby and Platformer',
  'Fighting', 'Sports and Racing', 'Town and City', 'Comedy', 'FPS',
]
const MC_CATEGORIES = [
  { value: 'technology', label: '기술 (Technology)' },
  { value: 'magic', label: '마법 (Magic)' },
  { value: 'adventure_rpg', label: '모험/RPG (Adventure & RPG)' },
  { value: 'map_information', label: '맵/정보 (Map & Information)' },
]

// 대화 흐름 단계: 'pick_game' | 'genres' | 'player_size' | 'mc_categories' | 'submitting' | 'results'
const step = ref('pick_game')
const gameType = ref(null) // 'roblox' | 'minecraft'
const selectedGenres = ref([])
const selectedCategories = ref([])
const error = ref(null)
const recommendations = ref([])

// 채팅 로그: { role: 'bot'|'user', text }
const messages = reactive([
  { role: 'bot', text: '안녕하세요! 취향에 맞는 게임/모드를 추천해 드릴게요. 무엇을 추천받고 싶으신가요?' },
])

function toggle(list, value) {
  const idx = list.indexOf(value)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(value)
}

function pickGame(type) {
  gameType.value = type
  messages.push({ role: 'user', text: type === 'roblox' ? '로블록스' : '마인크래프트' })
  if (type === 'roblox') {
    messages.push({ role: 'bot', text: '좋아요! 어떤 장르를 좋아하세요? (복수 선택 가능)' })
    step.value = 'genres'
  } else {
    messages.push({ role: 'bot', text: '좋아요! 관심 있는 모드 카테고리를 선택해주세요. (복수 선택 가능)' })
    step.value = 'mc_categories'
  }
}

function confirmGenres() {
  if (selectedGenres.value.length === 0) return
  messages.push({ role: 'user', text: selectedGenres.value.join(', ') })
  messages.push({ role: 'bot', text: '대규모 멀티플레이를 선호하세요, 아니면 소규모/캐주얼을 선호하세요?' })
  step.value = 'player_size'
}

async function pickPlayerSize(size) {
  messages.push({ role: 'user', text: size === 'large' ? '대규모' : '소규모' })
  step.value = 'submitting'
  messages.push({ role: 'bot', text: '추천을 계산하고 있어요...' })
  try {
    const res = await submitRobloxSurvey({ genres: selectedGenres.value, player_size: size })
    recommendations.value = res.recommendations
    messages.push({ role: 'bot', text: '짜잔! 추천 게임 TOP 5예요 🎮' })
    step.value = 'results'
  } catch (e) {
    error.value = e.message
    step.value = 'genres'
  }
}

async function confirmCategories() {
  if (selectedCategories.value.length === 0) return
  const labels = selectedCategories.value
    .map((v) => MC_CATEGORIES.find((c) => c.value === v)?.label ?? v)
  messages.push({ role: 'user', text: labels.join(', ') })
  step.value = 'submitting'
  messages.push({ role: 'bot', text: '추천을 계산하고 있어요...' })
  try {
    const res = await submitMinecraftSurvey({ categories: selectedCategories.value })
    recommendations.value = res.recommendations
    messages.push({ role: 'bot', text: '짜잔! 추천 모드 TOP 5예요 ⛏️' })
    step.value = 'results'
  } catch (e) {
    error.value = e.message
    step.value = 'mc_categories'
  }
}

function restart() {
  step.value = 'pick_game'
  gameType.value = null
  selectedGenres.value = []
  selectedCategories.value = []
  recommendations.value = []
  error.value = null
  messages.splice(0, messages.length, {
    role: 'bot',
    text: '다시 추천받아 볼까요? 무엇을 추천받고 싶으신가요?',
  })
}

const resultMeta = computed(() => (item) => {
  if (gameType.value === 'roblox') {
    return `${item.genre} · 동접 ${Number(item.playing ?? 0).toLocaleString()}명`
  }
  return `다운로드 ${Number(item.download_count ?? 0).toLocaleString()}회`
})

const resultTags = computed(() => (item) => {
  if (gameType.value === 'roblox') return []
  return item.loaders ?? []
})
</script>

<template>
  <div class="app-shell">
    <div class="chat-shell">
      <div class="app-title">🧭 Game Mod Compass</div>

      <template v-for="(m, i) in messages" :key="i">
        <div class="chat-bubble" :class="m.role">{{ m.text }}</div>
      </template>

      <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

      <div v-if="step === 'pick_game'" class="chat-options">
        <button class="chip" @click="pickGame('roblox')">🟦 로블록스</button>
        <button class="chip" @click="pickGame('minecraft')">🟩 마인크래프트</button>
      </div>

      <template v-if="step === 'genres'">
        <div class="chat-options">
          <button
            v-for="g in ROBLOX_GENRES"
            :key="g"
            class="chip"
            :class="{ selected: selectedGenres.includes(g) }"
            @click="toggle(selectedGenres, g)"
          >
            {{ g }}
          </button>
        </div>
        <button class="btn-primary" :disabled="selectedGenres.length === 0" @click="confirmGenres">
          선택 완료 →
        </button>
      </template>

      <div v-if="step === 'player_size'" class="chat-options">
        <button class="chip" @click="pickPlayerSize('large')">대규모</button>
        <button class="chip" @click="pickPlayerSize('small')">소규모</button>
      </div>

      <template v-if="step === 'mc_categories'">
        <div class="chat-options">
          <button
            v-for="c in MC_CATEGORIES"
            :key="c.value"
            class="chip"
            :class="{ selected: selectedCategories.includes(c.value) }"
            @click="toggle(selectedCategories, c.value)"
          >
            {{ c.label }}
          </button>
        </div>
        <button
          class="btn-primary"
          :disabled="selectedCategories.length === 0"
          @click="confirmCategories"
        >
          선택 완료 →
        </button>
      </template>

      <div v-if="step === 'results'" class="chat-results">
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
        <button class="btn-ghost" @click="restart">🔄 다시 추천받기</button>
      </div>
    </div>
  </div>
</template>
