<script setup>
/**
 * Mod Compass - TeamView.vue
 * 유스AI프로젝트:D 2기 2조 팀 소개 페이지
 */
import VoxelTerrainCanvas from '../components/VoxelTerrainCanvas.vue'

const emit = defineEmits(['navigate-home', 'navigate-chat', 'navigate-team', 'toggle-theme', 'toggle-engine-pause'])

const props = defineProps({
  theme: { type: String, required: true },
  isEnginePaused: { type: Boolean, default: false },
})

function toggleTheme() {
  emit('toggle-theme')
}

const teamMembers = [
  {
    name: '이정안',
    group: '유스AI프로젝트:D 2기 2조',
    role: 'Frontend & 3D Engine',
    avatar: 'LEE',
    bio: 'Vue 3 기반의 UI/UX 설계 및 Three.js ov6 3D 복셀 지형 엔진 구축을 담당했습니다.',
    techs: ['Vue 3', 'Three.js', 'Vite', 'CSS Glassmorphism'],
  },
  {
    name: '송영진',
    group: '유스AI프로젝트:D 2기 2조',
    role: 'Backend & AI Pipeline',
    avatar: 'SONG',
    bio: 'FastAPI 파이프라인 구축, NLU 대화 의도 파싱 알고리즘 및 OpenAI API 인퍼런스를 담당했습니다.',
    techs: ['FastAPI', 'Python', 'OpenAI API', 'NLU Parser'],
  },
  {
    name: '우은결',
    group: '유스AI프로젝트:D 2기 2조',
    role: 'Data & Recommendation Engine',
    avatar: 'WOO',
    bio: 'CurseForge 모드 및 Roblox 인기 게임 메타데이터 정제, SQLModel DB 스키마 및 랭킹 엔진을 제작했습니다.',
    techs: ['SQLModel', 'SQLite', 'CurseForge API', 'Roblox API'],
  },
]
</script>

<template>
  <div class="team-page">
    <!-- 3D Voxel Overworld Background -->
    <VoxelTerrainCanvas :theme="props.theme" :is-paused="props.isEnginePaused" />

    <!-- 상단 네비게이션 바 -->
    <header class="overworld-navbar">
      <div class="header-container">
        <button class="logo" type="button" @click="emit('navigate-home')">
          🧭 Mod Compass
        </button>
        <nav class="nav-links">
          <button class="nav-btn" type="button" @click="emit('navigate-home')">
            프로젝트 소개
          </button>
          <button class="nav-btn active" type="button" @click="emit('navigate-team')">
            참여자 소개
          </button>
          <button class="nav-btn highlight" type="button" @click="emit('navigate-chat')">
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

    <!-- 메인 참여자 소개 컨텐츠 -->
    <main class="team-content">
      <div class="team-hero-card">
        <span class="group-badge">🚀 유스AI프로젝트:D 2기 2조</span>
        <h1>Mod Compass 프로젝트 참여자 소개</h1>
        <p class="hero-sub">
          해커톤에서 <strong>Mod Compass</strong> 프로젝트를 함께 기획하고 개발한
          <strong>유스AI프로젝트:D 2기 2조</strong> 팀원들입니다.
        </p>

        <div class="team-grid">
          <div v-for="member in teamMembers" :key="member.name" class="member-card">
            <div class="member-avatar">{{ member.avatar }}</div>
            <span class="group-tag">🚀 {{ member.group }}</span>
            <h2>{{ member.name }}</h2>
            <span class="role-badge">{{ member.role }}</span>
            <p class="member-bio">{{ member.bio }}</p>
            <div class="tech-tags">
              <span v-for="tech in member.techs" :key="tech" class="tech-tag">{{ tech }}</span>
            </div>
          </div>
        </div>

        <div class="team-actions">
          <button class="btn-primary" type="button" @click="emit('navigate-chat')">
            💬 AI 챗봇과 대화하러 가기
          </button>
          <button class="btn-secondary" type="button" @click="emit('navigate-home')">
            🏠 홈 프로젝트 소개로 돌아가기
          </button>
        </div>
      </div>
    </main>

    <footer class="overworld-footer">
      &copy; 2026 Mod Compass Team · 유스AI프로젝트:D 2기 2조. All rights reserved.
    </footer>
  </div>
</template>

<style scoped>
.team-page {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: var(--text-color);
  overflow-x: hidden;
}

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
  background: none;
  border: none;
  font-size: 1.35rem;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
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
  transition: all 0.2s;
}

.nav-btn:hover {
  background-color: rgba(255, 255, 255, 0.12);
  color: #60a5fa;
}

.nav-btn.active {
  background-color: rgba(59, 130, 246, 0.25);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.nav-btn.highlight {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
  border-radius: 30px;
  padding: 0.5rem 1.2rem;
  font-weight: 700;
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

.team-content {
  position: relative;
  z-index: 10;
  max-width: 1000px;
  margin: 0 auto;
  padding: 100px 1.5rem 3rem;
  width: 100%;
}

.team-hero-card {
  padding: 3rem 2.5rem;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(12px);
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.group-badge {
  display: inline-block;
  font-size: 0.88rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.18);
  border: 1px solid rgba(59, 130, 246, 0.4);
  padding: 6px 18px;
  border-radius: 20px;
  margin-bottom: 1.2rem;
}

.team-hero-card h1 {
  font-size: 2.4rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 0.8rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.hero-sub {
  color: #cbd5e1;
  font-size: 1.08rem;
  margin-bottom: 2.8rem;
  line-height: 1.6;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 1.8rem;
  margin-bottom: 3rem;
}

.member-card {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 2.2rem 1.6rem;
  text-align: center;
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.member-card:hover {
  transform: translateY(-6px);
  border-color: #3b82f6;
  background: rgba(30, 41, 59, 0.8);
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.2);
}

.member-avatar {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 800;
  margin-bottom: 1rem;
  box-shadow: 0 6px 18px rgba(59, 130, 246, 0.4);
}

.group-tag {
  font-size: 0.8rem;
  color: #93c5fd;
  font-weight: 700;
  margin-bottom: 0.4rem;
}

.member-card h2 {
  font-size: 1.5rem;
  color: #ffffff;
  margin-bottom: 0.4rem;
}

.role-badge {
  font-size: 0.82rem;
  color: #60a5fa;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 4px 12px;
  border-radius: 14px;
  font-weight: 700;
  margin-bottom: 1rem;
}

.member-bio {
  color: #e2e8f0;
  font-size: 0.92rem;
  line-height: 1.6;
  margin-bottom: 1.2rem;
  word-break: keep-all;
  flex: 1;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
}

.tech-tag {
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  padding: 3px 9px;
  border-radius: 10px;
}

.team-actions {
  display: flex;
  justify-content: center;
  gap: 1.2rem;
  flex-wrap: wrap;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #ffffff;
  padding: 1rem 2.2rem;
  font-size: 1.05rem;
  font-weight: 700;
  border: none;
  border-radius: 35px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 6px 18px rgba(59, 130, 246, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.6);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 35px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: #60a5fa;
  color: #60a5fa;
}

.overworld-footer {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 1.8rem;
  color: #cbd5e1;
  font-size: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(8px);
}
</style>
