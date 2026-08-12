<script setup>
/**
 * Mod Compass - HomeView.vue
 * - 3 메뉴 네브바: 1. 프로젝트 소개, 2. 참여자 소개 (독립 페이지 이동), 3. AI 대화 시작
 * - 1:1 대화형 AI 가이드 카드: GitHub Copilot 공식 로고 적용
 * - ov6.html 3D Voxel Overworld Engine + Ultra-transparent Minimalist Glass UI
 */
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import VoxelTerrainCanvas from '../components/VoxelTerrainCanvas.vue'

const emit = defineEmits(['navigate-chat', 'navigate-team', 'toggle-theme', 'toggle-engine-pause'])

const props = defineProps({
  theme: { type: String, required: true },
  isEnginePaused: { type: Boolean, default: false },
})

const activeTech = ref(null)
const mobileMenuOpen = ref(false)

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// 모바일 전용 섹션 아코디언 토글 상태 관리 (기본적으로 첫번째는 펼치고 나머지는 접어 가독성 확보)
const mobileSections = reactive({
  whySelection: true,
  whyStory: false,
  features: false,
  agentArch: false,
})

const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth <= 768
}

function toggleMobileSection(key) {
  mobileSections[key] = !mobileSections[key]
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

function toggleTechInfo(key) {
  activeTech.value = activeTech.value === key ? null : key
}

function toggleTheme() {
  emit('toggle-theme')
}

function onCanvasClick() {
  emit('navigate-chat')
}
</script>

<template>
  <div class="home-view">
    <!-- 3D Voxel Overworld Engine Background -->
    <VoxelTerrainCanvas :theme="props.theme" :is-paused="props.isEnginePaused" @canvas-click="onCanvasClick" />

    <!-- 상단 플로팅 네비게이션 바 (3가지 메뉴: 1. 프로젝트 소개, 2. 참여자 소개, 3. AI 대화 시작) -->
    <header class="overworld-navbar">
      <div class="header-container">
        <a class="logo" href="#about">
          🧭 Mod Compass
        </a>
        <button class="mobile-menu-toggle" type="button" @click="toggleMobileMenu" :aria-expanded="mobileMenuOpen">
          {{ mobileMenuOpen ? '✕' : '☰' }}
        </button>
        <nav class="nav-links" :class="{ 'is-open': mobileMenuOpen }">
          <a href="#about" class="nav-btn" @click="mobileMenuOpen = false">프로젝트 소개</a>
          <button class="nav-btn" type="button" @click="emit('navigate-team'); mobileMenuOpen = false">
            참여자 소개
          </button>
          <button class="nav-btn highlight" type="button" @click="emit('navigate-chat'); mobileMenuOpen = false">
            AI 대화 시작 ✨
          </button>
          <button
            class="theme-toggle-btn engine-btn"
            :class="{ paused: props.isEnginePaused }"
            type="button"
            @click="emit('toggle-engine-pause')"
            :title="props.isEnginePaused ? '3D 배경 재생' : '3D 배경 일시정지 (발열 및 배터리 절약 모드)'"
          >
            {{ props.isEnginePaused ? '▶️ 3D 재생' : '⏸️ 3D 일시정지' }}
          </button>
          <button class="theme-toggle-btn" type="button" @click="toggleTheme">
            {{ props.theme === 'dark' ? '☀️ 라이트 모드' : '🌙 다크 모드' }}
          </button>
        </nav>
      </div>
    </header>

    <!-- 메인 컨텐츠 투명 오버레이 -->
    <main class="overworld-content">
      <!-- 히어로 섹션 -->
      <section id="about" class="hero-section">
        <div class="hero-glass-card">
          <h1>가상의 세상에서 여러분의 상상력을 키워주는<br />Mod Compass</h1>
          <p>
            <strong>Mod Compass</strong>는 3D 오버월드 지형 탐색과 대화형 AI 파이프라인을 결합하여
            마인크래프트 모드와 로블록스 인기 게임을 맞춤 추천합니다.
          </p>

          <div class="hero-actions">
            <button class="chat-btn main-action" type="button" @click="emit('navigate-chat')">
              💬 AI 챗봇 추천 시작하기
            </button>
            <a href="#features" class="btn-secondary">
              🔍 주요 기능 둘러보기
            </a>
          </div>

          <!-- 실시간 데이터 카운터 -->
          <div class="stats-counter-bar">
            <div class="stat-item">
              <span class="stat-num">94+</span>
              <span class="stat-label">로블록스 인기 플레이스</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">100+</span>
              <span class="stat-label">CurseForge 마크 모드</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">24/7</span>
              <span class="stat-label">AI 맞춤 대화 서비스</span>
            </div>
          </div>
        </div>

        <!-- 1. 독립 카드: 수많은 주제 중 Mod Compass를 선택한 이유 -->
        <div class="why-selection-card mobile-collapsible" :class="{ 'is-open': mobileSections.whySelection }">
          <div class="why-selection-header clickable-header" @click="toggleMobileSection('whySelection')">
            <span class="selection-badge">💡 WHY MOD COMPASS</span>
            <h2>
              수많은 주제 중 'Mod Compass'를 선택한 이유
              <span class="mobile-toggle-arrow">{{ mobileSections.whySelection ? '▲' : '▼' }}</span>
            </h2>
          </div>

          <div class="collapsible-body">
            <div class="why-reasons-grid">
              <div class="reason-card">
                <div class="reason-header">
                  <span class="reason-icon">🎪</span>
                  <h4>8월 22일(토) 파인콘 축제 'AI 놀이터'</h4>
                </div>
                <p>
                  파인콘 축제가 <strong>'AI 놀이터'</strong>를 컨셉으로 개최되기에, 초등학생 아이들이
                  우리의 Mod Compass 프로젝트를 통해 <strong>정말 AI와 신나게 놀 수 있는 프로젝트</strong>라고 확신하여 선정했습니다.
                </p>
              </div>

              <div class="reason-card">
                <div class="reason-header">
                  <span class="reason-icon">🏢</span>
                  <h4>8월 8일 MS 본사 하루 만의 완벽 제작</h4>
                </div>
                <p>
                  8월 8일 <strong>Microsoft 서울 본사 해커톤</strong> 현장에서 주어진 시간 안에
                  <strong>단 하루 만에 완성도 높은 서비스로 구현</strong>해낼 수 있는 확실한 주제였습니다.
                </p>
              </div>

              <div class="reason-card">
                <div class="reason-header">
                  <span class="reason-icon">💡</span>
                  <h4>팀원 모두의 높은 이해도 &amp; 아이디어 통합</h4>
                </div>
                <p>
                  팀원 모두가 마인크래프트와 로블록스 생태계를 잘 알고 있어,
                  <strong>모든 팀원의 상상력과 창의적인 아이디어를 하나로 모아 결합</strong>할 수 있었습니다.
                </p>
              </div>

              <div class="reason-card">
                <div class="reason-header">
                  <span class="reason-icon">🛠️</span>
                  <h4>YouthAIproject:D에서 배운 기술 활용</h4>
                </div>
                <p>
                  <strong>YouthAIproject:D</strong>에서 4개월 동안 배운 <strong>파이썬, GitHub Codespaces, GitHub Copilot CLI, LangChain, RAG, MCP</strong> 등 핵심 AI 개념과 최신 기술을 실전 프로젝트에 적극 활용했습니다.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. 독립 카드: 왜 수많은 게임 중 마인크래프트와 로블록스 인가요? -->
        <div class="why-story-card mobile-collapsible" :class="{ 'is-open': mobileSections.whyStory }">
          <div class="why-story-header clickable-header" @click="toggleMobileSection('whyStory')">
            <span class="why-badge">🧱 PHILOSOPHY &amp; PROJECT GOAL</span>
            <h2>
              왜 수많은 게임 중 마인크래프트와 로블록스 인가요?
              <span class="mobile-toggle-arrow">{{ mobileSections.whyStory ? '▲' : '▼' }}</span>
            </h2>
          </div>

          <div class="collapsible-body">
            <div class="why-story-body">
              <div class="story-comparison">
                <div class="story-box analog">
                  <div class="box-icon">🪵 🧩</div>
                  <h3>아날로그 시대: 블록과 상상력</h3>
                  <p>
                    옛날에는 <strong>쌓기나무 블록</strong>, <strong>레고</strong>와 같은 네모 블록으로
                    인간의 상상력을 기르는 활동을 했습니다.
                  </p>
                </div>

                <div class="story-arrow">➔</div>

                <div class="story-box digital">
                  <div class="box-icon">🖥️ ⚡</div>
                  <h3>컴퓨팅 시대: 세상을 구현하는 무대</h3>
                  <p>
                    요즘같이 컴퓨팅 파워가 받쳐주는 시대에서 아이들이 <strong>마인크래프트</strong>와 <strong>로블록스</strong>라는
                    가상의 세계에서 세상을 만들고 구현하고 시험하는 환경이 주어졌습니다.
                  </p>
                </div>
              </div>

              <!-- 프로젝트 목표 & 타겟 사용자 카드 -->
              <div class="story-goal-card">
                <div class="goal-item">
                  <span class="goal-icon">🎯</span>
                  <div class="goal-text">
                    <h4>프로젝트 목표</h4>
                    <p>
                      우리는 여기서 사용자의 성향을 기반으로 마인크래프트의 여러 가지 모드와 로블록스 게임을 추천하여,
                      <strong>사용자의 상상력을 더욱 키워주는 것</strong>을 프로젝트의 목표로 두고 있습니다.
                    </p>
                  </div>
                </div>

                <div class="goal-divider"></div>

                <div class="goal-item target">
                  <span class="goal-icon">👥</span>
                  <div class="goal-text">
                    <h4>타겟 사용자</h4>
                    <p class="target-highlight">
                      <strong>초등학교 3학년 ~ 성인</strong>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 프로젝트 핵심 특징 카드 4가지 (대주제: 우리 프로젝트의 특징) -->
      <section id="features" class="features-section mobile-collapsible" :class="{ 'is-open': mobileSections.features }">
        <div class="features-header clickable-header" @click="toggleMobileSection('features')">
          <span class="features-badge">✨ CORE FEATURES</span>
          <h2>
            우리 프로젝트의 특징
            <span class="mobile-toggle-arrow">{{ mobileSections.features ? '▲' : '▼' }}</span>
          </h2>
        </div>

        <div class="collapsible-body">
          <div class="features">
            <!-- 1. CurseForge API 마인크래프트 상위 100개 모드 -->
            <div class="feature-card">
              <div class="pixel-art-container mc-bg">
                <div class="mc-creeper-art"></div>
              </div>
              <div class="feature-content">
                <h3>🟩 CurseForge API 연동 마인크래프트 상위 100개 모드</h3>
                <p>
                  세계 최대 모드 플랫폼 <strong>CurseForge API</strong>를 활용하여 마인크래프트 상위 100개 인기 모드 메타데이터를 파싱하고
                  <strong>AI Agent 추천시스템에 탑재</strong>했습니다.
                </p>
              </div>
            </div>

            <!-- 2. Roblox 인기게임 트렌드 반영 -->
            <div class="feature-card">
              <div class="pixel-art-container rb-bg">
                <div class="rb-block-art"></div>
              </div>
              <div class="feature-content">
                <h3>🟥 Roblox 인기게임 트렌드 반영</h3>
                <p>
                  로블록스 플랫폼 내 수많은 플레이스 중 실시간 동시 접속자 수 및 방문 트렌드를 정밀하게 반영하여,
                  혼자 즐길 캐주얼 게임부터 대규모 멀티까지 최적의 플레이스를 추천합니다.
                </p>
              </div>
            </div>

            <!-- 3. ChatGPT 5.4 기반 AI Agent 구현 (ChatGPT 로고 적용) -->
            <div class="feature-card">
              <div class="pixel-art-container chatgpt-bg">
                <img src="/chatgpt-user-emblem.png" alt="ChatGPT Logo" class="feature-card-logo chatgpt-img" />
              </div>
              <div class="feature-content">
                <h3>🤖 ChatGPT 5.4 기반 AI Agent 구현</h3>
                <p>
                  Microsoft APIM으로 연결된 최신 <strong>ChatGPT 5.4 기반 AI Agent</strong>를 탑재하여 유저의 성향과 대화 맥락을 정밀 분석하고
                  맞춤 추천 및 사유를 제공합니다.
                </p>
              </div>
            </div>

            <!-- 4. Copilot CLI & Matt Pocock 회의 방식 제작 (Copilot CLI 이미지 적용) -->
            <div class="feature-card">
              <div class="pixel-art-container copilot-cli-bg">
                <img src="/copilot-cli-user-terminal.png" alt="GitHub Copilot CLI User Terminal" class="feature-card-logo copilot-cli-img" />
              </div>
              <div class="feature-content">
                <h3>🚀 Copilot CLI와 Matt Pocock 회의 방식으로 프로젝트 하루만에 제작</h3>
                <p>
                  <strong>GitHub Copilot CLI</strong> 오케스트레이션과 <strong>Matt Pocock 회의 방식</strong>(프롬프트 이터레이션 및 구조적 회의 기법)을 적용해
                  프로젝트를 신속하고 정교하게 구현했습니다.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 사용자 기반 AI Agent 설계 구조도 -->
      <section id="ai-agent-arch" class="agent-arch-section mobile-collapsible" :class="{ 'is-open': mobileSections.agentArch }">
        <div class="agent-arch-header clickable-header" @click="toggleMobileSection('agentArch')">
          <span class="agent-arch-badge">🧠 AI AGENT ARCHITECTURE</span>
          <h2>
            사용자 기반 AI Agent 설계 구조
            <span class="mobile-toggle-arrow">{{ mobileSections.agentArch ? '▲' : '▼' }}</span>
          </h2>
          <p class="agent-arch-subtitle">
            사용자의 성향 분석부터 RAG 기반 모드 데이터 탐색, AI 추론 및 추천 사유 생성까지의 프로세스
          </p>
        </div>

        <div class="collapsible-body">
          <div class="pipeline-flow">
            <div class="pipeline-step">
              <div class="step-num">STEP 1</div>
              <div class="step-icon">💬 👤</div>
              <h3>유저 성향 &amp; 대화 입력</h3>
              <p>유저 선택 기분/플레이 스타일, 자연어 대화 메시지 및 연령대/플랫폼 파라미터 수집</p>
              <div class="step-tag">User Input Context</div>
            </div>

            <div class="pipeline-arrow">➔</div>

            <div class="pipeline-step">
              <div class="step-num">STEP 2</div>
              <div class="step-icon">⚙️ 🤖</div>
              <h3>AI Agent 의도 분석</h3>
              <p><strong>ChatGPT 5.4 (MS APIM)</strong> 기반 맥락 분석, 성향 파악 및 검색 키워드 라우팅</p>
              <div class="step-tag">Intent Routing</div>
            </div>

            <div class="pipeline-arrow">➔</div>

            <div class="pipeline-step">
              <div class="step-num">STEP 3</div>
              <div class="step-icon">📦 ⚡</div>
              <h3>CurseForge &amp; RAG 쿼리</h3>
              <p>CurseForge API 100개 마크 모드 &amp; 로블록스 인기 트렌드 DB 검색 및 Prompt 결합</p>
              <div class="step-tag">Metadata RAG Engine</div>
            </div>

            <div class="pipeline-arrow">➔</div>

            <div class="pipeline-step highlight">
              <div class="step-num">STEP 4</div>
              <div class="step-icon">🧭 ✨</div>
              <h3>맞춤 추천 &amp; 사유 생성</h3>
              <p>최적 모드/게임 3~5개 매칭, 맞춤 <strong>추천 사유 및 가이드</strong> 실시간 답변 생성</p>
              <div class="step-tag">Agent Output &amp; Chat</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 기술 스펙 아코디언 -->
      <section id="tech" class="tech-section">
        <h2>🛠️ 기술 스펙 & 시스템 아키텍처</h2>
        <p class="tech-subtitle">👇 클릭하여 각 레이어별 세부 사양을 확인하세요.</p>

        <div class="tech-btn-grid">
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'fe' }"
            type="button"
            @click="toggleTechInfo('fe')"
          >
            <span>&lt;프론트엔드&gt; Vue 3 + ov6 3D Engine</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'be' }"
            type="button"
            @click="toggleTechInfo('be')"
          >
            <span>&lt;백엔드&gt; FastAPI + NLU</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'db' }"
            type="button"
            @click="toggleTechInfo('db')"
          >
            <span>&lt;DB&gt; SQLModel + SQLite</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'ui' }"
            type="button"
            @click="toggleTechInfo('ui')"
          >
            <span>&lt;UI디자인&gt; 3D Glassmorphism</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'copilot' }"
            type="button"
            @click="toggleTechInfo('copilot')"
          >
            <span>&lt;AI파이프라인&gt; Copilot CLI + Wayfinder</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'cron' }"
            type="button"
            @click="toggleTechInfo('cron')"
          >
            <span>&lt;데이터싱크&gt; 매일 자정 크론 자동 싱크</span>
            <span class="arrow">▼</span>
          </button>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'fe' }">
          <h4>💻 &lt;프론트엔드&gt; Vue 3 + Vite + ov6.html 3D InstancedMesh Engine</h4>
          <p>
            `ov6.html` 3D 엔진 코드를 이식하여 InstancedMesh 기반 60x60 지형, 삼림, 굽이치는 강,
            드론 카메라 궤적 및 3D 나침반과 큐브가 실시간 렌더링되는 고성능 3D 가상 공간을 구축했습니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'be' }">
          <h4>🐍 &lt;백엔드&gt; Python FastAPI + NLU 파서 + OpenAI API</h4>
          <p>
            FastAPI + SQLModel로 데이터를 정제하고 1-Turn 자연어 의도 파싱, AI 추천 이유(Reasoning)
            자동 생성, 랭킹 알고리즘 및 오프라인 하이브리드 인퍼런스를 제공합니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'db' }">
          <h4>🗄️ &lt;DB&gt; SQLModel & SQLite 데이터베이스</h4>
          <p>
            CurseForge 마인크래프트 100개 모드 및 로블록스 상위 94개 게임의 정제된 메타데이터를
            초고속으로 검색·매칭하는 경량화 DB 시스템입니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'ui' }">
          <h4>🎨 &lt;UI디자인&gt; 3D Glassmorphism &amp; Modern Aesthetic</h4>
          <p>
            Gemini AI 디자인 가이드 기반 픽셀 아트 및 차세대 3D 컴퍼스, 글로우 그라데이션,
            직관적이고 미려한 현대적 인터페이스로 구성되었습니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'copilot' }">
          <h4>💬 &lt;AI파이프라인&gt; Copilot CLI + Matt Pocock/Wayfinder 대화형 파이프라인</h4>
          <p>
            Wayfinder 프롬프트 인터뷰 방식을 응용하여 사용자 질문 의도를 정확하게 분해하고
            게임/모드 데이터베이스의 매칭 가중치와 실시간으로 연동합니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'cron' }">
          <h4>🌙 &lt;데이터싱크&gt; 매일 자정 크론 기반 최신 데이터 자동 싱크</h4>
          <p>
            Roblox 공식 API 및 CurseForge API 데이터 순위 갱신은 매일 자정 자동 갱신되어
            사용자는 항상 최신의 동시접속자 수와 다운로드 수 지표를 확인하게 됩니다.
          </p>
        </div>
      </section>
    </main>

    <footer class="overworld-footer">&copy; 2026 Mod Compass Team. All rights reserved.</footer>
  </div>
</template>

<style scoped>
.home-page {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--text-color);
  overflow-x: hidden;
}

/* 슬림 플로팅 네비게이션 바 */
.overworld-navbar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100vw - 32px);
  max-width: 900px;
  z-index: 100;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 50px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  padding: 6px 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.logo {
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  text-decoration: none;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}

.mobile-menu-toggle {
  display: none;
}

.nav-btn {
  background: none;
  border: none;
  color: #f1f5f9;
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.45rem 0.9rem;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.12);
  color: #60a5fa;
}

.nav-btn.highlight {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
  border-radius: 30px;
  padding: 0.45rem 1.1rem;
}

.nav-btn.highlight:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

.theme-toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 0.45rem 0.9rem;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
}

/* 메인 컨텐츠 투명 오버레이 */
.overworld-content {
  position: relative;
  z-index: 10;
  max-width: 1000px;
  margin: 0 auto;
  padding: 100px 1.5rem 3rem;
  width: 100%;
  pointer-events: none;
}

.overworld-content > * {
  pointer-events: auto;
}

.hero-section {
  margin-top: 3vh;
  margin-bottom: 4rem;
}

.hero-glass-card {
  text-align: center;
  padding: 2.2rem 2rem;
  background: rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(8px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.hero-glass-card h1 {
  font-size: 2.5rem;
  line-height: 1.35;
  margin-bottom: 0.8rem;
  word-break: keep-all;
  font-weight: 800;
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.7);
}

.hero-glass-card p {
  color: #e2e8f0;
  font-size: 1.05rem;
  max-width: 720px;
  margin: 0 auto 1.8rem auto;
  word-break: keep-all;
  line-height: 1.55;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.chat-btn.main-action {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #ffffff;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  border: none;
  border-radius: 35px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.chat-btn.main-action:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 25px rgba(59, 130, 246, 0.6);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 1rem 1.8rem;
  font-size: 0.98rem;
  font-weight: 600;
  border-radius: 35px;
  text-decoration: none;
  transition: all 0.2s;
  backdrop-filter: blur(4px);
}

.btn-secondary:hover {
  border-color: #60a5fa;
  color: #60a5fa;
  background: rgba(255, 255, 255, 0.2);
}

.stats-counter-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding-top: 1.4rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 1.7rem;
  font-weight: 800;
  color: #60a5fa;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.stat-label {
  font-size: 0.85rem;
  color: #cbd5e1;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: rgba(255, 255, 255, 0.15);
}

/* 독립적인 프로젝트 소개 카드 2종 */
.why-selection-card,
.why-story-card {
  margin-top: 2.5rem;
  background: rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(8px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 2.2rem 2rem;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.why-story-header {
  text-align: center;
  margin-bottom: 1.8rem;
}

.why-badge {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.18);
  border: 1px solid rgba(59, 130, 246, 0.4);
  padding: 4px 14px;
  border-radius: 20px;
  margin-bottom: 0.6rem;
}

.why-story-header h2,
.why-story-header h3 {
  font-size: 1.85rem;
  font-weight: 800;
  color: #ffffff !important;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.7);
  word-break: keep-all;
}

.story-comparison {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.6rem;
  flex-wrap: wrap;
}

.story-box {
  flex: 1;
  min-width: 260px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.4rem 1.2rem;
  transition: transform 0.2s, border-color 0.2s;
}

.story-box:hover {
  transform: translateY(-3px);
  border-color: #3b82f6;
  background: rgba(30, 41, 59, 0.7);
}

.box-icon {
  font-size: 1.8rem;
  margin-bottom: 0.6rem;
}

.story-box h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #60a5fa;
  margin-bottom: 0.5rem;
}

.story-box p {
  font-size: 0.92rem;
  color: #cbd5e1;
  line-height: 1.55;
  word-break: keep-all;
}

.story-arrow {
  font-size: 1.5rem;
  color: #60a5fa;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
}

@media (max-width: 640px) {
  .story-arrow {
    transform: rotate(90deg);
    width: 100%;
  }
}

.story-goal-card {
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 18px;
  padding: 1.4rem 1.6rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.goal-item {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  flex: 2;
  min-width: 280px;
}

.goal-item.target {
  flex: 1;
  min-width: 200px;
}

.goal-icon {
  font-size: 1.8rem;
  line-height: 1;
}

.goal-text h4 {
  font-size: 1.05rem;
  font-weight: 800;
  color: #60a5fa;
  margin-bottom: 0.3rem;
}

.goal-text p {
  font-size: 0.92rem;
  color: #e2e8f0;
  line-height: 1.52;
  word-break: keep-all;
}

.target-highlight {
  font-size: 1.12rem !important;
  color: #60a5fa !important;
  font-weight: 700;
}

.goal-divider {
  width: 1px;
  height: 60px;
  background: rgba(255, 255, 255, 0.15);
}

@media (max-width: 640px) {
  .goal-divider {
    display: none;
  }
}

/* Why Mod Compass Selection Reasons Card */
.why-selection-header {
  text-align: center;
  margin-bottom: 1.8rem;
}

.why-selection-header h2,
.why-selection-header h3 {
  font-size: 1.85rem;
  font-weight: 800;
  color: #ffffff !important;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.7);
  word-break: keep-all;
}

.selection-badge {
  display: inline-block;
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.4);
  font-size: 0.72rem;
  font-weight: 800;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  letter-spacing: 0.05em;
  margin-bottom: 0.4rem;
}

.why-selection-header h3 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #f8fafc;
}

.why-reasons-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

@media (max-width: 768px) {
  .why-reasons-grid {
    grid-template-columns: 1fr;
  }
}

.reason-card {
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 1.2rem;
  transition: transform 0.2s, border-color 0.2s;
}

.reason-card:hover {
  transform: translateY(-3px);
  border-color: #a855f7;
  background: rgba(15, 23, 42, 0.65);
}

.reason-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.6rem;
}

.reason-icon {
  font-size: 1.4rem;
}

.reason-header h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #e9d5ff;
}

.reason-card p {
  font-size: 0.9rem;
  color: #cbd5e1;
  line-height: 1.52;
  word-break: keep-all;
}

/* Features Main Header Section */
.features-section {
  margin-top: 3.5rem;
  margin-bottom: 3.5rem;
}

.features-header {
  text-align: center;
  margin-bottom: 2rem;
}

.features-badge {
  display: inline-block;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.4);
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  letter-spacing: 0.08em;
  margin-bottom: 0.6rem;
}

.features-header h2 {
  font-size: 2.1rem;
  font-weight: 800;
  color: #ffffff !important;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.7);
  word-break: keep-all;
}

/* Feature Cards (2행 2열 2x2 그리드 레이아웃 고정) */
.features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.8rem;
}

/* 사용자 기반 AI Agent 설계 구조 섹션 */
.agent-arch-section {
  margin-top: 3.5rem;
  margin-bottom: 3.5rem;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 2.5rem 2rem;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
}

.agent-arch-header {
  text-align: center;
  margin-bottom: 2.2rem;
}

.agent-arch-badge {
  display: inline-block;
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.4);
  font-size: 0.78rem;
  font-weight: 800;
  padding: 0.25rem 0.8rem;
  border-radius: 20px;
  letter-spacing: 0.08em;
  margin-bottom: 0.6rem;
}

.agent-arch-header h2 {
  font-size: 2.1rem;
  font-weight: 800;
  color: #ffffff !important;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.7);
  margin-bottom: 0.5rem;
  word-break: keep-all;
}

.agent-arch-subtitle {
  font-size: 0.95rem;
  color: #94a3b8;
  word-break: keep-all;
}

.pipeline-flow {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 0.8rem;
}

.pipeline-step {
  flex: 1;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.4rem 1.1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.2s, border-color 0.2s;
}

.pipeline-step:hover {
  transform: translateY(-4px);
  border-color: #a855f7;
  background: rgba(30, 41, 59, 0.85);
}

.pipeline-step.highlight {
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.15);
}

.step-num {
  font-size: 0.72rem;
  font-weight: 800;
  color: #a855f7;
  letter-spacing: 0.05em;
  margin-bottom: 0.4rem;
}

.step-icon {
  font-size: 1.8rem;
  margin-bottom: 0.6rem;
}

.pipeline-step h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
  word-break: keep-all;
}

.pipeline-step p {
  font-size: 0.88rem;
  color: #cbd5e1;
  line-height: 1.5;
  margin-bottom: 1rem;
  flex: 1;
  word-break: keep-all;
}

.step-tag {
  font-size: 0.72rem;
  font-weight: 600;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
}

.pipeline-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a855f7;
  font-size: 1.3rem;
  opacity: 0.8;
}

@media (max-width: 900px) {
  .pipeline-flow {
    flex-direction: column;
  }
  .pipeline-arrow {
    transform: rotate(90deg);
    padding: 0.5rem 0;
  }
}

.feature-card {
  background: rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(8px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, border-color 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: #3b82f6;
  background: rgba(15, 23, 42, 0.5);
}

.pixel-art-container {
  width: 100%;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.15);
}

.mc-creeper-art {
  width: 80px;
  height: 80px;
  background-color: #10b981;
  position: relative;
  box-shadow: 0 0 0 4px #047857 inset;
  border-radius: 6px;
}

.mc-creeper-art::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  background: #064e3b;
  top: 16px;
  left: 16px;
  box-shadow:
    32px 0 0 #064e3b,
    16px 16px 0 #064e3b,
    8px 32px 0 #064e3b,
    24px 32px 0 #064e3b,
    0px 40px 0 #064e3b,
    8px 40px 0 #064e3b,
    24px 40px 0 #064e3b,
    32px 40px 0 #064e3b;
}

.rb-block-art {
  width: 75px;
  height: 75px;
  background-color: #ef4444;
  transform: rotate(-12deg);
  position: relative;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(239, 68, 68, 0.3);
}

.rb-block-art::after {
  content: '';
  position: absolute;
  width: 25px;
  height: 25px;
  background-color: #ffffff;
  top: 25px;
  left: 25px;
  border-radius: 4px;
}

.copilot-logo-art {
  width: 85px;
  height: 85px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(0 0 12px rgba(96, 165, 250, 0.4));
  transition: transform 0.3s ease;
}

.copilot-logo-art:hover {
  transform: scale(1.1) rotate(5deg);
}

.chatgpt-bg {
  background: radial-gradient(circle, rgba(255, 255, 255, 0.25) 0%, rgba(15, 23, 42, 0.5) 100%);
}

.chatgpt-img {
  width: 90px;
  height: 90px;
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  object-fit: contain;
  transition: transform 0.3s ease;
}

.feature-card:hover .chatgpt-img {
  transform: scale(1.08) rotate(5deg);
}

.copilot-cli-bg {
  background: radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, rgba(15, 23, 42, 0.4) 100%);
}

.copilot-cli-img {
  width: 92%;
  max-width: 320px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
}

.feature-card:hover .copilot-cli-img {
  transform: scale(1.04);
}

.feature-content {
  padding: 1.5rem;
  flex: 1;
}

.feature-card h3 {
  margin-bottom: 0.5rem;
  color: #60a5fa;
  font-size: 1.18rem;
}

.feature-card p {
  color: #e2e8f0;
  font-size: 0.92rem;
  line-height: 1.5;
  word-break: keep-all;
}

/* Tech Section */
.tech-section {
  background: rgba(15, 23, 42, 0.35);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 2.2rem 1.6rem;
  margin-bottom: 3.5rem;
}

.tech-section h2 {
  font-size: 1.8rem;
  margin-bottom: 0.4rem;
  text-align: center;
  color: #ffffff;
}

.tech-subtitle {
  text-align: center;
  color: #cbd5e1;
  font-size: 0.88rem;
  margin-bottom: 1.5rem;
}

.tech-btn-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.9rem;
  margin-bottom: 1.2rem;
}

.tech-btn {
  background-color: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tech-btn:hover {
  border-color: #3b82f6;
  color: #60a5fa;
  transform: translateY(-2px);
}

.tech-btn.active {
  background-color: #3b82f6;
  color: #ffffff;
  border-color: #3b82f6;
}

.tech-btn .arrow {
  font-size: 0.8rem;
  transition: transform 0.3s;
}

.tech-btn.active .arrow {
  transform: rotate(180deg);
}

.tech-info-box {
  display: none;
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid #3b82f6;
  border-radius: 14px;
  padding: 1.2rem;
  margin-bottom: 1.2rem;
  animation: fadeIn 0.3s ease-in-out;
}

.tech-info-box.show {
  display: block;
}

.tech-info-box h4 {
  color: #60a5fa;
  margin-bottom: 0.4rem;
  font-size: 1.1rem;
}

.tech-info-box p {
  color: #e2e8f0;
  font-size: 0.92rem;
  line-height: 1.55;
  word-break: keep-all;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.tech-extra-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.tech-detail-card {
  background: rgba(30, 41, 59, 0.4);
  padding: 1.2rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tech-detail-card h4 {
  color: #60a5fa;
  margin-bottom: 0.3rem;
  font-size: 1rem;
}

.tech-detail-card p {
  color: #cbd5e1;
  font-size: 0.9rem;
  line-height: 1.48;
  word-break: keep-all;
}

/* ==========================================================================
   📱 Mobile Collapsible Architecture & Legibility Enhancements
   ========================================================================== */

/* Toggle arrow styling */
.mobile-toggle-arrow {
  display: none;
  margin-left: 0.6rem;
  font-size: 1.05rem;
  color: #c084fc;
  vertical-align: middle;
  transition: transform 0.25s ease;
}

/* On Desktop (min-width: 769px), collapsible-body is ALWAYS fully expanded */
@media (min-width: 769px) {
  .collapsible-body {
    display: block !important;
  }
}

/* On Mobile (max-width: 768px), contents are collapsed by default and expandable via header clicks */
@media (max-width: 768px) {
  .mobile-toggle-arrow {
    display: inline-block;
  }

  .clickable-header {
    cursor: pointer;
    user-select: none;
    padding: 0.4rem 0.2rem;
    border-radius: 12px;
    transition: background-color 0.2s ease;
  }

  .clickable-header:active {
    background-color: rgba(255, 255, 255, 0.08);
  }

  .collapsible-body {
    display: none;
    padding-top: 1.2rem;
  }

  .mobile-collapsible.is-open .collapsible-body {
    display: block;
    animation: slideDownMobile 0.25s ease-out forwards;
  }

  @keyframes slideDownMobile {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* Mobile Layout Padding & Spacing */
  .why-selection-card,
  .why-story-card,
  .features-section,
  .agent-arch-section,
  .tech-section {
    padding: 1.6rem 1.1rem !important;
    margin-top: 1.4rem !important;
    margin-bottom: 1.4rem !important;
    border-radius: 18px !important;
  }

  /* Single column grids on Mobile */
  .why-reasons-grid,
  .features,
  .pipeline-flow,
  .tech-btn-grid {
    grid-template-columns: 1fr !important;
    flex-direction: column !important;
    gap: 1rem !important;
  }

  .pipeline-arrow {
    transform: rotate(90deg);
    padding: 0.3rem 0;
  }

  /* Mobile Font Sizes & High Legibility */
  .why-selection-header h2,
  .why-story-header h2,
  .features-header h2,
  .agent-arch-header h2,
  .tech-section h2 {
    font-size: 1.4rem !important;
    line-height: 1.35 !important;
    margin-bottom: 0.3rem !important;
  }

  .hero-glass-card h1 {
    font-size: 1.65rem !important;
    line-height: 1.35 !important;
  }

  .nav-links {
    gap: 0.4rem !important;
    flex-wrap: wrap !important;
  }

  .nav-btn {
    padding: 0.4rem 0.6rem !important;
    font-size: 0.8rem !important;
  }
}

/* ===== 모바일 네비게이션 (햄버거 메뉴로 전환하여 본문과 겹치지 않도록 처리) ===== */
@media (max-width: 768px) {
  .overworld-navbar {
    position: sticky;
    top: 0;
    left: 0;
    transform: none;
    width: 100%;
    max-width: 100%;
    border-radius: 0;
    padding: 10px 14px;
    border-left: none;
    border-right: none;
    border-top: none;
  }

  .header-container {
    flex-wrap: wrap;
  }

  .logo {
    font-size: 1.1rem;
  }

  .mobile-menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    color: #ffffff;
    font-size: 1.15rem;
    cursor: pointer;
  }

  .nav-links {
    display: none;
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    gap: 0.5rem !important;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.12);
  }

  .nav-links.is-open {
    display: flex;
  }

  .nav-links .nav-btn,
  .nav-links .theme-toggle-btn {
    width: 100%;
    text-align: center;
    padding: 0.65rem 0.8rem !important;
    font-size: 0.9rem !important;
  }

  /* 네비바가 sticky 흐름으로 바뀌었으므로 본문 상단 여백을 되돌려 겹침 방지 */
  .overworld-content {
    padding: 24px 1rem 3rem !important;
  }

  .hero-section {
    margin-top: 0.5rem !important;
  }
}
</style>
