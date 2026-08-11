<script setup>
/**
 * AI 게임 모드 추천 챗봇 (ChatView.vue)
 * - 백엔드 FastAPI /api/chat 연동 + 스마트 클라이언트 하이브리드 오프라인 폴백
 * - 1-Turn 즉시 추천 지원 & AI 맞춤 추천 사유(Reasoning) 제시
 * - 추천 카드 클릭 시 상세 정보를 확인할 수 있는 모달 팝업 제공
 */
import { computed, nextTick, onMounted, ref } from 'vue'
import { resetChat as apiResetChat, sendChatMessage as apiSendChatMessage } from '../api.js'

const emit = defineEmits(['navigate-home', 'navigate-team'])

const props = defineProps({})

const INITIAL_SUGGESTIONS = [
  '🚀 로블록스 공포 게임 추천해줘',
  '🧩 마인크래프트 기술 모드 추천해줘',
  '⚔️ 친구들이랑 하기 좋은 로블록스 어드벤처',
  '🪄 마인크래프트 마법 모드가 궁금해',
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
const copySuccess = ref(false)

// 상세 모달 상태
const selectedItem = ref(null)

let nextMessageId = 0

// 클라이언트 오프라인 폴백 상태
const scriptState = ref({ gameType: null, genre: null, category: null, size: null })

const composerPlaceholder = computed(() => (
  conversationDone.value
    ? '새로 추천받기를 눌러 새로운 대화를 시작하세요.'
    : '예: 로블록스 공포 게임 5개 추천해줘'
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
  selectedItem.value = null
  scriptState.value = { gameType: null, genre: null, category: null, size: null }
  messages.value = [
    createMessage(
      'bot',
      '안녕하세요! Game Mod Compass AI 가이드입니다 🧭\n어떤 게임이나 모드를 찾으시나요? 편하게 질문해주시면 취향에 꼭 맞는 추천을 도와드릴게요!',
      INITIAL_SUGGESTIONS,
    ),
  ]
  scrollToBottom()
}

function openDetailModal(item) {
  selectedItem.value = item
}

function closeDetailModal() {
  selectedItem.value = null
}

function resultMeta(item) {
  if (activeGameType.value === 'roblox') {
    const playing = item.playing ? item.playing.toLocaleString() : '인기'
    return `${item.genre || '어드벤처'} · 동접 ${playing}명`
  }
  const dl = item.download_count ? item.download_count.toLocaleString() : '1,000,000+'
  return `다운로드 ${dl}회`
}

function resultTags(item) {
  if (activeGameType.value === 'roblox') return [item.genre || 'Roblox']
  return item.loaders && item.loaders.length ? item.loaders : ['Forge']
}

// --- 오프라인 하이브리드 로컬 카탈로그 (백엔드 미연동 시 폴백) -----------------
const ROBLOX_FULL_CATALOG = {
  'Horror': [
    { id: 101, name: 'DOORS 👁️', universe_id: 3537107339, genre: 'Horror', playing: 38490, visits: 2100000000, description: '방을 하나씩 이동하며 기괴한 괴물들을 피하고 탈출하는 고품격 1인칭 공포 어드벤처 게임입니다.', url: 'https://www.roblox.com/games/10873380714/DOORS', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-53f81a48fb348823169b97fd42a1094a/150/150/Image/Png/noFilter', reason: '로블록스 공포 장르 압도적 1위! 손땀 쥐는 긴장감과 친구들과의 협동 탈출 재미가 뛰어납니다.' },
    { id: 102, name: 'Flee the Facility 🏃', universe_id: 110539706, genre: 'Horror', playing: 24500, visits: 3800000000, description: '살인마를 피해 컴퓨터를 해킹하고 탈출구를 열어야 하는 비대칭 생존 공포 게임입니다.', url: 'https://www.roblox.com/games/893973440/Flee-the-Facility', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a64f70da20fc1e80ee76fe5d49c1be0a/150/150/Image/Png/noFilter', reason: '친구들과 함께할수록 재미가 배가되는 로블록스 클래식 공포 술래잡기 게임입니다.' },
    { id: 103, name: 'The Mimic 👻', universe_id: 2315715878, genre: 'Horror', playing: 14200, visits: 720000000, description: '일본 전통 요괴 전설을 바탕으로 제작된 동양적 분위기의 공포 에피소드 게임입니다.', url: 'https://www.roblox.com/games/6243697925/The-Mimic', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a16e27d3d8380da38b43960549590ca2/150/150/Image/Png/noFilter', reason: '소름 돋는 연출과 훌륭한 스토리 그래픽으로 유저들에게 극찬받는 심리 공포작입니다.' },
    { id: 104, name: 'Rainbow Friends 🌈', universe_id: 3418579089, genre: 'Horror', playing: 29100, visits: 1400000000, description: '귀여운 외모 뒤에 숨겨진 괴물들을 피해 블록을 모으고 야간 생존하는 캐주얼 스릴러입니다.', url: 'https://www.roblox.com/games/7991339063/Rainbow-Friends', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-ae0b1c314ffcf425584d23023492bba6/150/150/Image/Png/noFilter', reason: '쉬운 규칙과 캐릭터성으로 가볍게 스릴을 즐기고 싶은 플레이어에게 추천합니다.' },
    { id: 105, name: 'Evade 🚨', universe_id: 3676648797, genre: 'Horror', playing: 31000, visits: 1900000000, description: '밈(Meme) 넥스트봇들을 피해 빠른 속도로 달리고 동료를 구출하는 3D 공포 게임입니다.', url: 'https://www.roblox.com/games/9872472334/Evade', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-9704151d9c8a70e7ebe0ced8cb2b95c1/150/150/Image/Png/noFilter', reason: '빠른 템포의 스피드감과 동료 부활 시스템으로 대규모 멀티 플레이어에게 최고입니다.' },
  ],
  'Adventure': [
    { id: 1, name: '⚔️ Blox Fruits', universe_id: 396860069, genre: 'Adventure', playing: 342100, visits: 32000000000, description: '해적이 되어 강력한 열매 능력을 얻고 대해적 시대를 탐험하는 오픈월드 RPG 어드벤처입니다.', url: 'https://www.roblox.com/games/2753915549/Blox-Fruits', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a64f70da20fc1e80ee76fe5d49c1be0a/150/150/Image/Png/noFilter', reason: '전 세계 로블록스 동시접속자 1위! 화려한 스킬과 성장 요소가 압도적입니다.' },
    { id: 2, name: 'Build A Boat For Treasure ⛵', universe_id: 5374135, genre: 'Adventure', playing: 21400, visits: 3100000000, description: '다양한 블록으로 나만의 배를 만들어 거친 강과 장애물을 넘어 보물을 찾아 항해하는 게임입니다.', url: 'https://www.roblox.com/games/5374135/Build-A-Boat-For-Treasure', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-a16e27d3d8380da38b43960549590ca2/150/150/Image/Png/noFilter', reason: '창의적인 배 제작과 친구들과의 공동 물리 실험 항해 재미가 돋보입니다.' },
    { id: 3, name: 'Brookhaven 🏡RP', universe_id: 2018898144, genre: 'Town and City', playing: 195000, visits: 48000000000, description: '멋진 집과 자동차를 소유하고 자유롭게 마을을 탐험하며 역할을 연기하는 차세대 롤플레잉입니다.', url: 'https://www.roblox.com/games/4924922222/Brookhaven-RP', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-9704151d9c8a70e7ebe0ced8cb2b95c1/150/150/Image/Png/noFilter', reason: '규칙 없이 자유로운 일상 시뮬레이션을 즐기는 유저에게 최적의 선택입니다.' },
    { id: 4, name: 'Adopt Me! 🐾', universe_id: 920587237, genre: 'Simulation', playing: 148000, visits: 36000000000, description: '수백 가지 전설 펫을 수집하고 키우며 나만의 집을 꾸미고 거래하는 따뜻한 육성 시뮬레이터입니다.', url: 'https://www.roblox.com/games/920587237/Adopt-Me', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-53f81a48fb348823169b97fd42a1094a/150/150/Image/Png/noFilter', reason: '귀여운 펫 수집과 거래 시스템으로 누구나 부담 없이 즐길 수 있는 힐링작입니다.' },
    { id: 5, name: 'Tower of Hell 🗼', universe_id: 196208686, genre: 'Obby and Platformer', playing: 24100, visits: 13000000000, description: '체크포인트 없이 무작위로 생성되는 높은 타워의 정상까지 빠르게 등반하는 타임어택 오비입니다.', url: 'https://www.roblox.com/games/196208686/Tower-of-Hell', thumbnail_url: 'https://tr.rbxcdn.com/180DAY-ae0b1c314ffcf425584d23023492bba6/150/150/Image/Png/noFilter', reason: '점프 능력을 겨루는 도전 욕구 자극과 피지컬 오비의 최고봉입니다.' },
  ],
}

const MINECRAFT_FULL_CATALOG = {
  'technology': [
    { id: 201, name: 'Create: Mechanical Automation ⚙️', slug: 'create', download_count: 58204000, categories: ['technology'], loaders: ['Forge', 'Fabric'], summary: '톱니바퀴, 벨트, 풍차, 앙상블 시스템으로 마인크래프트에 현실적인 공학 자동화 공장을 구축하는 혁신적 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/create', logo_url: 'https://media.forgecdn.net/avatars/282/64/637286105828775463.png', reason: '마크 공학 모드의 신화! 압도적인 애니메이션 기계 조작감으로 높은 평가를 받습니다.' },
    { id: 202, name: 'Applied Energistics 2 💎', slug: 'applied-energistics-2', download_count: 46102000, categories: ['technology'], loaders: ['Forge', 'Fabric'], summary: '물질을 디지털 에너지 네트워크로 전환하여 대용량 디지털 자동 창고와 오토 크래프팅을 구현합니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/applied-energistics-2', logo_url: 'https://media.forgecdn.net/avatars/46/782/635706509930784901.png', reason: '아이템 정리에 지친 플레이어에게 필수인 디지털 자동화 대용량 수집 모드입니다.' },
    { id: 203, name: 'Industrial Craft Reborn ⚡', slug: 'industrial-craft', download_count: 32211000, categories: ['technology'], loaders: ['Forge'], summary: '원자력 발전소, 전기 회로망, 채굴기, 제트팩을 도입하여 현대 산업 사회를 재현합니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/industrial-craft', logo_url: 'https://media.forgecdn.net/avatars/15/485/635398285513254972.png', reason: '전력망 구축과 원자력 발전까지 산업 기술의 정석을 체험할 수 있습니다.' },
    { id: 204, name: 'Mekanism High Tech 🧪', slug: 'mekanism', download_count: 39500000, categories: ['technology'], loaders: ['Forge', 'NeoForge'], summary: '5단계 기체-액체 화학 공정, 핵융합 원자로, 디지털 마이너 채굴 로봇 시스템을 제공합니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/mekanism', logo_url: 'https://media.forgecdn.net/avatars/31/361/635467471960249789.png', reason: '정교한 기술 티어 상승과 핵융합 발전이라는 확실한 엔드 콘텐츠 목표를 부여합니다.' },
    { id: 205, name: 'Thermal Expansion 🔥', slug: 'thermal-expansion', download_count: 48900000, categories: ['technology'], loaders: ['Forge'], summary: 'RF 전력을 기반으로 한 다양한 제련 기계와 광물 가공 배율 시스템을 제공하는 친숙한 테크 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/thermal-expansion', logo_url: 'https://media.forgecdn.net/avatars/12/375/635398284566354972.png', reason: '입문하기 쉽고 깔끔한 기계 라인업으로 입문자부터 숙련자까지 사랑받습니다.' },
  ],
  'magic': [
    { id: 301, name: 'Thaumcraft Arcane Magic 🔮', slug: 'thaumcraft', download_count: 51200000, categories: ['magic'], loaders: ['Forge'], summary: '세계의 위상(Aspect)을 연구하고 마법 지팡이와 연금술 솥단지로 비밀 주문을 완성해나가는 대형 마법 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/thaumcraft', logo_url: 'https://media.forgecdn.net/avatars/14/563/635398285918754972.png', reason: '깊이 있는 연구 서적 전개와 몰입감 높은 연구 프로세스가 탐험욕을 자극합니다.' },
    { id: 302, name: 'Botania Nature Spells 🌸', slug: 'botania', download_count: 54100000, categories: ['magic'], loaders: ['Forge', 'Fabric'], summary: '신비로운 마법 꽃과 마나(Mana) 에너지를 렌즈와 기계로 전달하여 마법 기계를 가동하는 테크니컬 마법 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/botania', logo_url: 'https://media.forgecdn.net/avatars/24/491/635408103328754972.png', reason: 'GUI 없이 마나 전달체와 꽃으로만 작동하는 시각적으로 가장 아름다운 마법 모드입니다.' },
    { id: 303, name: 'Ars Nouveau Spellmaking 📜', slug: 'ars-nouveau', download_count: 28400000, categories: ['magic'], loaders: ['Forge', 'NeoForge'], summary: '나만의 마법 문양을 조합해 맞춤형 연쇄 주문을 직접 창작하고 룬 마법 문명을 구축하는 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/ars-nouveau', logo_url: 'https://media.forgecdn.net/avatars/305/778/637375128362775463.png', reason: '주문 조합의 자유도가 극대화되어 사용자만의 강력한 오리지널 마법 작성이 가능합니다.' },
    { id: 304, name: 'Blood Magic Rituals 🩸', slug: 'blood-magic', download_count: 42100000, categories: ['magic'], loaders: ['Forge'], summary: '생명 에너지를 제단에 바쳐 강력한 마법 장신구와 영역 룬 제단을 구축하는 다크 판타지 마법 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/blood-magic', logo_url: 'https://media.forgecdn.net/avatars/19/223/635400194883254972.png', reason: '강력한 제단 의식과 유용한 영역 마법 효과로 묵직한 마법 성장을 원하는 보스전 유저에게 좋습니다.' },
    { id: 305, name: 'Twilight Forest 🌲', slug: 'twilight-forest', download_count: 67300000, categories: ['magic', 'adventure_rpg'], loaders: ['Forge', 'Fabric'], summary: '영원한 저녁 노을이 지는 신비로운 숲 차원으로 이동해 던전과 던전 보스를 정복하는 모험 모드입니다.', url: 'https://www.curseforge.com/minecraft/mc-mods/the-twilight-forest', logo_url: 'https://media.forgecdn.net/avatars/16/894/635398287890754972.png', reason: '수십 년간 전 세계 마인크래프트 탐험 모드 중 1위를 지켜온 신화적인 차원 모드입니다.' },
  ],
}

function matchSmartIntent(text) {
  const lowered = text.toLowerCase()
  let gameType = null
  if (/로블록스|roblox|robux/i.test(lowered)) gameType = 'roblox'
  if (/마인크래프트|마크|minecraft|mc/i.test(lowered)) gameType = 'minecraft'

  let robloxGenre = null
  if (/공포|호러|horror|무서운/i.test(lowered)) robloxGenre = 'Horror'
  else if (/어드벤처|모험|rpg|알피지/i.test(lowered)) robloxGenre = 'Adventure'

  let mcCat = null
  if (/기술|테크|공학|기계|tech/i.test(lowered)) mcCat = 'technology'
  else if (/마법|매직|magic|주문/i.test(lowered)) mcCat = 'magic'

  return { gameType, robloxGenre, mcCat }
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
    // 백엔드 API 연동 시도
    const res = await apiSendChatMessage(message)
    if (res && res.reply) {
      activeGameType.value = res.game_type ?? activeGameType.value
      recommendations.value = res.recommendations ?? []
      conversationDone.value = res.stage === 'done'
      messages.value.push(createMessage('bot', res.reply))
      scrollToBottom()
      isLoading.value = false
      return
    }
  } catch (e) {
    // API 에러 시 클라이언트 스마트 하이브리드 인퍼런스로 자연스럽게 전환
    console.warn('API connection offline, using hybrid client AI engine:', e)
  }

  // 클라이언트 오프라인 폴백 처리
  await new Promise((resolve) => setTimeout(resolve, 400))

  const { gameType, robloxGenre, mcCat } = matchSmartIntent(message)
  const currentGT = gameType || scriptState.value.gameType

  if (!currentGT) {
    messages.value.push(
      createMessage(
        'bot',
        '로블록스와 마인크래프트 중 어떤 종목을 추천받고 싶으신가요? 추천받을 게임을 말씀해주세요!',
        ['로블록스 추천', '마인크래프트 추천'],
      ),
    )
    isLoading.value = false
    scrollToBottom()
    return
  }

  scriptState.value.gameType = currentGT
  activeGameType.value = currentGT

  if (currentGT === 'roblox') {
    const genre = robloxGenre || (message.includes('공포') ? 'Horror' : 'Adventure')
    const catalog = ROBLOX_FULL_CATALOG[genre] || ROBLOX_FULL_CATALOG['Adventure']
    recommendations.value = catalog
    conversationDone.value = true
    messages.value.push(
      createMessage(
        'bot',
        `좋아요! ${genre} 취향에 맞춰 로블록스 인기 추천 5개를 엄선했어요. 각 카드를 클릭하면 상세 AI 추천 사유를 보실 수 있습니다.`,
      ),
    )
  } else {
    const cat = mcCat || 'technology'
    const catalog = MINECRAFT_FULL_CATALOG[cat] || MINECRAFT_FULL_CATALOG['technology']
    recommendations.value = catalog
    conversationDone.value = true
    const catName = cat === 'technology' ? '기술/공학' : '마법/주문'
    messages.value.push(
      createMessage(
        'bot',
        `좋아요! ${catName} 성향에 맞춰 마인크래프트 모드 추천 5개를 준비했어요. 각 카드를 클릭하면 모드 설치 링크와 상세 정보를 확인하실 수 있습니다.`,
      ),
    )
  }

  isLoading.value = false
  scrollToBottom()
}

async function restartChat() {
  isResetting.value = true
  try {
    await apiResetChat()
  } catch (e) {
    // ignore
  }
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

function copyRecommendationList() {
  if (!recommendations.value.length) return
  const text = recommendations.value
    .map((item, i) => `${i + 1}. ${item.name} (${item.genre || item.categories?.join(', ') || '추천'})`)
    .join('\n')

  navigator.clipboard.writeText(`[Game Mod Compass AI 추천 결과]\n${text}`).then(() => {
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2000)
  })
}

onMounted(() => {
  initializeConversation()
})
</script>

<template>
  <div class="chat-page">
    <!-- 플로팅 네브바 -->
    <div class="chat-nav-wrapper">
      <header class="chat-pill-nav">
        <button class="pill-logo" type="button" @click="emit('navigate-home')">
          🧭 Mod Compass
        </button>
        <div class="pill-actions">
          <button class="pill-btn" type="button" @click="emit('navigate-home')">
            🏠 프로젝트 소개
          </button>
          <button class="pill-btn" type="button" @click="emit('navigate-team')">
            👥 참여자 소개
          </button>

          <button class="pill-btn" type="button" :disabled="isResetting" @click="restartChat">
            🔄 새로 추천받기
          </button>
        </div>
      </header>
    </div>

    <!-- 메인 대화 영역 -->
    <div class="chat-shell">
      <div class="hero-panel">
        <div class="hero-kicker">AI GAME RECOMMENDATION ENGINE</div>
        <div class="app-title">🧭 Mod Compass AI 챗봇</div>
        <p class="hero-copy">자유롭게 이야기하거나 원하는 키워드를 입력해 당신만의 맞춤 게임과 모드를 찾아보세요.</p>
      </div>

      <div ref="chatLog" class="chat-log">
        <template v-for="message in messages" :key="message.id">
          <div class="message-row" :class="message.role">
            <div class="message-avatar">{{ avatar(message.role) }}</div>
            <div class="message-stack">
              <div class="chat-bubble" :class="message.role">{{ message.text }}</div>

              <!-- 추천 선택 칩 -->
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

        <!-- 타이핑 노드 -->
        <div v-if="isLoading" class="message-row bot typing-row">
          <div class="message-avatar">🧭</div>
          <div class="message-stack">
            <div class="chat-bubble bot typing-bubble" aria-label="AI가 분석 중입니다">
              <span class="typing-text">AI가 맞춤 추천 목록을 찾고 있습니다</span>
              <span class="typing-dot" />
              <span class="typing-dot" />
              <span class="typing-dot" />
            </div>
          </div>
        </div>

        <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

        <!-- 최종 추천 결과 리스트 -->
        <div v-if="recommendations.length" class="chat-results">
          <div class="results-header">
            <div>
              <strong class="results-title">🏆 AI 맞춤 추천 상위 5선</strong>
              <p>{{ activeGameType === 'roblox' ? '로블록스 추천 컬렉션' : '마인크래프트 추천 모드' }} (카드를 클릭하면 상세 정보를 볼 수 있습니다)</p>
            </div>
            <button class="btn-share" type="button" @click="copyRecommendationList">
              {{ copySuccess ? '✓ 복사완료' : '📋 추천결과 복사' }}
            </button>
          </div>

          <div
            v-for="(item, idx) in recommendations"
            :key="item.id || idx"
            class="chat-result-row clickable-card"
            @click="openDetailModal(item)"
          >
            <div class="rank">{{ idx + 1 }}</div>
            <img
              class="chat-thumb"
              :src="item.thumbnail_url || item.logo_url || 'https://via.placeholder.com/60'"
              alt=""
              loading="lazy"
            />
            <div class="info">
              <div class="title-row">
                <span class="title">{{ item.name }}</span>
                <span class="view-detail-hint">상세보기 🔍</span>
              </div>
              <div class="meta">
                {{ resultMeta(item) }}
                <span v-for="tag in resultTags(item)" :key="tag" class="tag">{{ tag }}</span>
              </div>
              <p v-if="item.reason" class="reason-preview">
                🤖 <strong>AI 추천 이유:</strong> {{ item.reason }}
              </p>
            </div>
          </div>

          <div class="results-actions">
            <button class="btn-ghost" type="button" :disabled="isResetting" @click="restartChat">
              🔄 다른 키워드로 다시 추천받기
            </button>
          </div>
        </div>
      </div>

      <!-- 사용자 메시지 입력 폼 -->
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
          {{ isLoading ? '분석 중...' : '전송' }}
        </button>
      </form>
    </div>

    <!-- 상세 모달 팝업 (Detail Modal) -->
    <div v-if="selectedItem" class="modal-backdrop" @click.self="closeDetailModal">
      <div class="modal-card">
        <button class="modal-close-btn" type="button" @click="closeDetailModal">✕</button>

        <div class="modal-header">
          <img
            class="modal-thumb"
            :src="selectedItem.thumbnail_url || selectedItem.logo_url || 'https://via.placeholder.com/100'"
            alt=""
          />
          <div class="modal-header-info">
            <span class="modal-badge">{{ activeGameType === 'roblox' ? 'ROBLOX GAME' : 'MINECRAFT MOD' }}</span>
            <h2>{{ selectedItem.name }}</h2>
            <div class="modal-tags">
              <span v-for="tag in resultTags(selectedItem)" :key="tag" class="modal-tag">{{ tag }}</span>
            </div>
          </div>
        </div>

        <div class="modal-body">
          <div v-if="selectedItem.reason" class="modal-reason-box">
            <h4>💡 AI 파이프라인 추천 사유</h4>
            <p>{{ selectedItem.reason }}</p>
          </div>

          <div class="modal-desc-box">
            <h4>📖 게임/모드 상세 개요</h4>
            <p>{{ selectedItem.description || selectedItem.summary || '상세 메타데이터 설명이 제공됩니다.' }}</p>
          </div>

          <div class="modal-stats-grid">
            <div v-if="selectedItem.playing !== undefined" class="modal-stat-card">
              <span class="label">현재 동시 접속자</span>
              <span class="val">{{ selectedItem.playing.toLocaleString() }}명</span>
            </div>
            <div v-if="selectedItem.visits !== undefined" class="modal-stat-card">
              <span class="label">누적 방문 수</span>
              <span class="val">{{ (selectedItem.visits / 100000000).toFixed(1) }}억 회</span>
            </div>
            <div v-if="selectedItem.download_count !== undefined" class="modal-stat-card">
              <span class="label">누적 다운로드</span>
              <span class="val">{{ selectedItem.download_count.toLocaleString() }}회</span>
            </div>
            <div v-if="selectedItem.loaders" class="modal-stat-card">
              <span class="label">지원 모드로더</span>
              <span class="val">{{ selectedItem.loaders.join(', ') }}</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <a
            v-if="selectedItem.url"
            :href="selectedItem.url"
            target="_blank"
            rel="noopener noreferrer"
            class="modal-action-btn primary"
          >
            🚀 {{ activeGameType === 'roblox' ? '로블록스에서 바로 플레이하기' : 'CurseForge에서 모드 다운로드' }}
          </a>
          <button class="modal-action-btn secondary" type="button" @click="closeDetailModal">
            닫기
          </button>
        </div>
      </div>
    </div>


  </div>
</template>

<style scoped>
.chat-page {
  width: 100%;
  min-height: 100vh;
  background: var(--chat-bg-gradient, radial-gradient(circle at 50% 0%, #1e293b, #0f172a));
  color: var(--chat-text-main, #f8fafc);
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
  max-width: 920px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 10px 24px;
  border-radius: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  animation: fadeInUp 0.5s ease forwards;
}

.pill-logo {
  background: none;
  border: none;
  font-size: 1.1rem;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.pill-tag {
  font-size: 0.75rem;
  color: #60a5fa;
  font-weight: 700;
  background: rgba(59, 130, 246, 0.15);
  padding: 3px 8px;
  border-radius: 12px;
}

.pill-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pill-btn {
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover:not(:disabled) {
  background-color: #3b82f6;
  color: #ffffff;
  transform: translateY(-2px);
}

.chat-shell {
  width: 100%;
  max-width: 920px;
  min-height: calc(100vh - 140px);
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.7s ease forwards;
  overflow: hidden;
}

.hero-panel {
  padding: 18px 26px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(15, 23, 42, 0.4);
}

.hero-kicker {
  color: #60a5fa;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.app-title {
  margin-top: 4px;
  font-size: 1.35rem;
  font-weight: 800;
}

.hero-copy {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 0.9rem;
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
  animation: fadeInUp 0.25s ease-out;
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
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  font-size: 18px;
}

.message-row.user .message-avatar {
  background: #2563eb;
}

.chat-bubble {
  padding: 16px 22px;
  border-radius: 20px;
  font-size: 1.05rem;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: keep-all;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  letter-spacing: -0.2px;
}

.chat-bubble.bot {
  background-color: #26354d;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-bottom-left-radius: 4px;
}

.chat-bubble.user {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border-bottom-right-radius: 4px;
  font-weight: 500;
}

.chat-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 9px 15px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chip:hover {
  transform: translateY(-2px);
  border-color: #60a5fa;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.15);
}

.typing-bubble {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.typing-text {
  font-size: 0.88rem;
  color: #94a3b8;
}

.typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #60a5fa;
  animation: typing-pulse 1s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

@keyframes typing-pulse {
  0%, 100% { transform: scale(1); opacity: 0.4; }
  50% { transform: scale(1.4); opacity: 1; }
}

.chat-results {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.results-title {
  font-size: 1.1rem;
  color: #60a5fa;
}

.results-header p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 13px;
}

.btn-share {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-share:hover {
  background: #3b82f6;
  color: #ffffff;
}

.clickable-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.clickable-card:hover {
  transform: translateY(-3px);
  border-color: #3b82f6 !important;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.25);
}

.chat-result-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 14px 16px;
}

.rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  flex-shrink: 0;
}

.chat-thumb {
  width: 58px;
  height: 58px;
  border-radius: 14px;
  object-fit: cover;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info {
  flex: 1;
  min-width: 0;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: 700;
  font-size: 1.05rem;
  color: #f8fafc;
}

.view-detail-hint {
  font-size: 0.75rem;
  color: #60a5fa;
  font-weight: 600;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.reason-preview {
  margin-top: 8px;
  font-size: 0.85rem;
  color: #cbd5e1;
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
  padding: 6px 10px;
  border-radius: 6px;
  line-height: 1.45;
}

.results-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.btn-ghost {
  background: transparent;
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 9px 18px;
  border-radius: 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ghost:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #60a5fa;
}

.composer {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  padding: 18px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.5);
}

.composer-input {
  flex: 1;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 12px 18px;
  color: #ffffff;
  font-size: 0.95rem;
  resize: none;
  outline: none;
  font-family: inherit;
}

.composer-input:focus {
  border-color: #3b82f6;
}

.btn-send {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border: none;
  padding: 12px 24px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal Styling */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.2s ease;
}

.modal-card {
  width: 100%;
  max-width: 580px;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 28px;
  position: relative;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  color: #f8fafc;
}

.modal-close-btn {
  position: absolute;
  top: 18px;
  right: 18px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #94a3b8;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: #ef4444;
  color: #ffffff;
}

.modal-header {
  display: flex;
  gap: 18px;
  align-items: center;
  margin-bottom: 20px;
}

.modal-thumb {
  width: 80px;
  height: 80px;
  border-radius: 18px;
  object-fit: cover;
  border: 2px solid rgba(59, 130, 246, 0.4);
}

.modal-header-info h2 {
  font-size: 1.4rem;
  margin: 4px 0 8px 0;
}

.modal-badge {
  font-size: 0.75rem;
  font-weight: 800;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.15);
  padding: 3px 10px;
  border-radius: 12px;
}

.modal-tags {
  display: flex;
  gap: 6px;
}

.modal-tag {
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 3px 10px;
  border-radius: 12px;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.modal-reason-box {
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 14px 18px;
}

.modal-reason-box h4 {
  color: #60a5fa;
  margin-bottom: 6px;
  font-size: 0.95rem;
}

.modal-reason-box p {
  color: #e2e8f0;
  font-size: 0.92rem;
  line-height: 1.5;
}

.modal-desc-box h4 {
  color: #94a3b8;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.modal-desc-box p {
  color: #cbd5e1;
  font-size: 0.92rem;
  line-height: 1.55;
}

.modal-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.modal-stat-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
}

.modal-stat-card .label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.modal-stat-card .val {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
  margin-top: 2px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-action-btn {
  padding: 12px 20px;
  border-radius: 14px;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.modal-action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

.modal-action-btn.secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #cbd5e1;
}

.modal-action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-action-btn.danger {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.modal-action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.25);
  color: #ffffff;
}

.pill-btn.key-btn.active {
  background: rgba(59, 130, 246, 0.25);
  border: 1px solid #3b82f6;
  color: #60a5fa;
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
}

.ms-key-modal {
  max-width: 520px;
}

.modal-desc {
  color: #cbd5e1;
  font-size: 0.92rem;
  line-height: 1.55;
  margin-bottom: 1.2rem;
}

.key-field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 1.2rem;
}

.key-field-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #94a3b8;
}

.key-field-input {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 12px 16px;
  color: #ffffff;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}

.key-field-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

.key-status-alert {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
}

.key-status-alert.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
}

.key-status-alert.info {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #93c5fd;
}

@media (max-width: 768px) {
  .chat-page {
    padding: 80px 10px 10px;
  }
  .chat-pill-nav {
    padding: 8px 12px;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .pill-logo {
    font-size: 0.95rem;
  }
  .pill-btn {
    padding: 6px 12px;
    font-size: 0.75rem;
  }
  .chat-shell {
    min-height: calc(100vh - 120px);
    border-radius: 16px;
  }
  .hero-panel {
    padding: 14px 18px;
  }
  .app-title {
    font-size: 1.15rem;
  }
  .chat-log {
    padding: 16px 12px;
  }
  .chat-input-area {
    padding: 12px;
  }
  .chat-textarea {
    font-size: 0.9rem;
    padding: 12px 48px 12px 14px;
  }
  .send-btn {
    width: 36px;
    height: 36px;
    right: 8px;
    bottom: 8px;
  }
  .chat-bubble {
    padding: 14px 16px;
    font-size: 1rem;
  }
  .ai-controls {
    flex-wrap: wrap;
    gap: 6px;
  }
  .modal-panel {
    width: 90%;
    margin: 20px;
    padding: 20px;
  }
}
</style>
