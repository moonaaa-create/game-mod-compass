<script setup>
/**
 * 팀원 디자인 docs/ai agent/main.html 을 그대로 이식한 랜딩 페이지.
 * 헤더 네브바의 "AI 대화 시작" 버튼을 누르면 부모(App.vue)에게 채팅 화면으로
 * 전환하라는 이벤트를 emit 한다.
 */
import { ref } from 'vue'

const emit = defineEmits(['navigate-chat', 'toggle-theme'])

const props = defineProps({
  theme: { type: String, required: true },
})

const activeTech = ref(null)

function toggleTechInfo(key) {
  activeTech.value = activeTech.value === key ? null : key
}

function toggleTheme() {
  emit('toggle-theme')
}
</script>

<template>
  <div class="home-page">
    <header>
      <div class="header-container">
        <a class="logo" href="#about">🧭 Game Compass</a>
        <nav class="nav-links">
          <a href="#about" class="nav-btn">프로젝트 소개</a>
          <a href="#tech" class="nav-btn">기술 스펙</a>
          <a href="#team" class="nav-btn">참여자 소개</a>
          <button class="nav-btn highlight" type="button" @click="emit('navigate-chat')">
            AI 대화 시작
          </button>
          <button class="theme-toggle-btn" type="button" @click="toggleTheme">
            {{ props.theme === 'dark' ? '☀️ 라이트 모드' : '🌙 다크 모드' }}
          </button>
        </nav>
      </div>
    </header>

    <main>
      <section id="about" class="intro-section">
        <h1>당신의 취향에 딱 맞는 게임 길잡이</h1>
        <p>
          <strong>Game Compass</strong>는 사용자의 성향과 취향을 분석하여 최적의 마인크래프트 모드와
          로블록스 게임을 추천해주는 인공지능 서비스입니다. 어떤 게임을 시작해야 할지 고민될 때, AI와
          대화하며 당신만의 완벽한 콘텐츠를 찾아보세요!
        </p>
        <button class="chat-btn" type="button" @click="emit('navigate-chat')">
          💬 AI와 대화 시작하기
        </button>
      </section>

      <section class="features">
        <div class="feature-card">
          <div class="pixel-art-container">
            <div class="mc-creeper-art"></div>
          </div>
          <div class="feature-content">
            <h3>🟩 CurseForge 상위 100개 모드</h3>
            <p>
              세계적인 모드 플랫폼 <strong>CurseForge</strong>에서 엄선된 인기 상위 100가지 마인크래프트
              모드 데이터를 기반으로, 건축·모험·공학 등 사용자의 성향에 맞는 최적의 모드를 추천해 드립니다.
            </p>
          </div>
        </div>

        <div class="feature-card">
          <div class="pixel-art-container">
            <div class="rb-block-art"></div>
          </div>
          <div class="feature-content">
            <h3>🟥 로블록스 인기 상위 94개 게임</h3>
            <p>
              로블록스 플랫폼 내 수많은 플레이스 중 엄선된 인기 상위 94개 게임 정보를 탑재하여, 친구들과
              함께 안전하고 재미있게 즐길 수 있는 맞춤형 게임을 빠르게 찾아줍니다.
            </p>
          </div>
        </div>

        <div class="feature-card">
          <div class="pixel-art-container">
            <div class="ai-icon-art">
              <div class="ai-face"></div>
            </div>
          </div>
          <div class="feature-content">
            <h3>🤖 쉬운 대화형 AI 가이드</h3>
            <p>
              "친구들이랑 다 같이 할 수 있는 시뮬레이터 알려줘!"나 "만들기 좋아하는 사용자에게 맞는 모드
              추천해줘"처럼 자연스러운 대화로 딱 맞는 콘텐츠를 찾을 수 있습니다.
            </p>
          </div>
        </div>
      </section>

      <section id="tech" class="tech-section">
        <h2>🛠️ 기술 스펙 & 시스템 구조</h2>
        <p class="tech-subtitle">👇 버튼을 클릭하면 기술 스펙별 상세 설명을 확인할 수 있습니다.</p>

        <div class="tech-btn-grid">
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'fe' }"
            type="button"
            @click="toggleTechInfo('fe')"
          >
            <span>&lt;프론트엔드&gt; 자바스크립트</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'be' }"
            type="button"
            @click="toggleTechInfo('be')"
          >
            <span>&lt;백엔드&gt; 파이썬</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'db' }"
            type="button"
            @click="toggleTechInfo('db')"
          >
            <span>&lt;DB&gt; SQL-Lite</span>
            <span class="arrow">▼</span>
          </button>
          <button
            class="tech-btn"
            :class="{ active: activeTech === 'ui' }"
            type="button"
            @click="toggleTechInfo('ui')"
          >
            <span>&lt;UI디자인&gt; Gemini디자인</span>
            <span class="arrow">▼</span>
          </button>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'fe' }">
          <h4>💻 &lt;프론트엔드&gt; 자바스크립트 (JavaScript)</h4>
          <p>Vue 3 + Vite로 다크/라이트 모드 전환, 동적 아코디언 토글, 자유 텍스트 대화형 UI를 구현했습니다.</p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'be' }">
          <h4>🐍 &lt;백엔드&gt; 파이썬 (Python)</h4>
          <p>
            FastAPI + SQLModel로 데이터를 정제하고 AI 인터페이스 간 통신과 비즈니스 로직 및 랭킹 정렬
            알고리즘을 효율적으로 처리합니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'db' }">
          <h4>🗄️ &lt;DB&gt; SQL-Lite</h4>
          <p>
            CurseForge 마인크래프트 모드 상위 100개 및 로블록스 상위 94개 게임의 정제된 메타데이터를
            빠르고 안정적으로 조회하는 경량화 데이터베이스를 구성했습니다.
          </p>
        </div>

        <div class="tech-info-box" :class="{ show: activeTech === 'ui' }">
          <h4>🎨 &lt;UI디자인&gt; Gemini디자인</h4>
          <p>Gemini AI와의 협업을 통해 생성한 CSS 픽셀 아트 및 사용자 친화적 가독성을 갖춘 현대적 모던 웹 인터페이스입니다.</p>
        </div>

        <div class="tech-extra-cards">
          <div class="tech-detail-card">
            <h4>💬 Copilot CLI + Matt Pocock/Wayfinder 기반 인터뷰</h4>
            <p>
              Copilot CLI와 Matt Pocock/Wayfinder 방식의 대화형 프롬프트 인터뷰 기법을 응용하여, 사용자의
              세밀한 요구사항과 게임 취향을 정확히 파악하는 대화 시스템을 구현했습니다.
            </p>
          </div>

          <div class="tech-detail-card">
            <h4>🌙 매일 밤 순위 자동 업데이트 (속도 최적화)</h4>
            <p>
              사용자 접속량이 많은 낮 시간대에 AI 대화 및 추천 답변 속도가 느려지지 않도록, 대용량 순위
              갱신 프로세스는 매일 밤 자정 알고리즘을 통해 자동 업데이트됩니다.
            </p>
          </div>
        </div>
      </section>

      <section id="team" class="team-section">
        <h2>프로젝트 참여자</h2>
        <div class="team-grid">
          <div class="team-card">
            <div class="team-avatar">LEE</div>
            <h3>이정안</h3>
          </div>
          <div class="team-card">
            <div class="team-avatar">SONG</div>
            <h3>송영진</h3>
          </div>
          <div class="team-card">
            <div class="team-avatar">WOO</div>
            <h3>우은결</h3>
          </div>
        </div>
      </section>
    </main>

    <footer>&copy; 2026 Game Compass Team. All rights reserved.</footer>
  </div>
</template>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  color: var(--text-color);
}

header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: var(--bg-color);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(8px);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.logo {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  text-decoration: none;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-btn {
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
}

.nav-btn:hover {
  background-color: var(--card-bg);
  color: var(--primary-color);
}

.nav-btn.highlight {
  background-color: var(--primary-color);
  color: #ffffff;
}

.nav-btn.highlight:hover {
  background-color: var(--primary-hover);
  color: #ffffff;
}

.theme-toggle-btn {
  background: var(--card-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}

.theme-toggle-btn:hover {
  border-color: var(--primary-color);
}

main {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
  flex: 1;
  width: 100%;
}

.intro-section {
  text-align: center;
  padding: 3.5rem 1.5rem;
  background: var(--card-bg);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  margin-bottom: 2.5rem;
  scroll-margin-top: 90px;
}

.intro-section h1 {
  font-size: 2.3rem;
  margin-bottom: 1rem;
  word-break: keep-all;
}

.intro-section p {
  color: var(--text-muted);
  font-size: 1.05rem;
  max-width: 750px;
  margin: 0 auto 2rem auto;
  word-break: keep-all;
}

.chat-btn {
  display: inline-block;
  background-color: var(--primary-color);
  color: #ffffff;
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  text-decoration: none;
  transition: background-color 0.2s, transform 0.1s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.chat-btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3.5rem;
}

.feature-card {
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.pixel-art-container {
  width: 100%;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.05);
}

.mc-creeper-art {
  width: 100px;
  height: 100px;
  background-color: var(--mc-green);
  position: relative;
  box-shadow: 0 0 0 5px var(--mc-shadow) inset;
}
.mc-creeper-art::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background: var(--mc-black);
  top: 20px;
  left: 20px;
  box-shadow:
    40px 0 0 var(--mc-black),
    20px 20px 0 var(--mc-black),
    10px 40px 0 var(--mc-black),
    30px 40px 0 var(--mc-black),
    0px 50px 0 var(--mc-black),
    10px 50px 0 var(--mc-black),
    30px 50px 0 var(--mc-black),
    40px 50px 0 var(--mc-black);
}

.rb-block-art {
  width: 90px;
  height: 90px;
  background-color: var(--rb-red);
  transform: rotate(-15deg);
  position: relative;
  border-radius: 5px;
}
.rb-block-art::after {
  content: '';
  position: absolute;
  width: 30px;
  height: 30px;
  background-color: var(--card-bg);
  top: 30px;
  left: 30px;
  border-radius: 2px;
  transition: background-color 0.3s;
}

.ai-icon-art {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ai-face {
  width: 60px;
  height: 40px;
  border: 6px solid var(--ai-grey);
  border-radius: 20px;
  position: relative;
}
.ai-face::before,
.ai-face::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background-color: var(--ai-grey);
  border-radius: 50%;
  top: 10px;
}
.ai-face::before {
  left: 12px;
}
.ai-face::after {
  right: 12px;
}

.feature-content {
  padding: 1.5rem;
  flex: 1;
}

.feature-card h3 {
  margin-bottom: 0.5rem;
  color: var(--primary-color);
  font-size: 1.2rem;
}

.feature-card p {
  color: var(--text-muted);
  font-size: 0.95rem;
  word-break: keep-all;
}

.tech-section {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2.5rem 1.5rem;
  margin-bottom: 3.5rem;
  scroll-margin-top: 90px;
}

.tech-section h2 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
  text-align: center;
}

.tech-subtitle {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.tech-btn-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.tech-btn {
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 1rem;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tech-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
}

.tech-btn.active {
  background-color: var(--primary-color);
  color: #ffffff;
  border-color: var(--primary-color);
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
  background: var(--bg-color);
  border: 1px solid var(--primary-color);
  border-radius: 12px;
  padding: 1.2rem;
  margin-bottom: 1.5rem;
  animation: fadeIn 0.3s ease-in-out;
}

.tech-info-box.show {
  display: block;
}

.tech-info-box h4 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.tech-info-box p {
  color: var(--text-color);
  font-size: 0.95rem;
  word-break: keep-all;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tech-extra-cards {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.tech-detail-card {
  background: var(--bg-color);
  padding: 1.2rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.tech-detail-card h4 {
  color: var(--primary-color);
  margin-bottom: 0.3rem;
  font-size: 1.05rem;
}

.tech-detail-card p {
  color: var(--text-muted);
  font-size: 0.95rem;
  word-break: keep-all;
}

.team-section {
  margin-top: 2rem;
  margin-bottom: 3rem;
  scroll-margin-top: 90px;
}

.team-section h2 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.team-card {
  background: var(--card-bg);
  padding: 2rem 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  text-align: center;
}

.team-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0 auto 1rem auto;
  letter-spacing: 0.5px;
}

.team-card h3 {
  font-size: 1.2rem;
}

footer {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

@media (max-width: 600px) {
  .header-container {
    flex-direction: column;
    gap: 1rem;
  }
  .nav-links {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
