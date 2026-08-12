<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Matter from 'matter-js'

const emit = defineEmits(['navigate-home', 'navigate-team', 'toggle-engine-pause'])

const matterContainer = ref(null)
const domContainer = ref(null)
const inputEl = ref(null)
const draft = ref('')
const isLoading = ref(false)

let engine = null
let render = null
let runner = null
let mouseConstraint = null
let bubblesData = []

// 백엔드 API 주소 (VITE_API_BASE 환경 변수, 없으면 로컬 개발 기본값)
const API_URL = `${import.meta.env.VITE_API_BASE || 'http://localhost:8000'}/api/chat`

function initMatter() {
  engine = Matter.Engine.create()
  engine.world.gravity.y = -0.05
  engine.world.gravity.x = 0

  render = Matter.Render.create({
    element: matterContainer.value,
    engine: engine,
    options: {
      width: window.innerWidth,
      height: window.innerHeight,
      wireframes: false,
      background: 'transparent'
    }
  })
  Matter.Render.run(render)

  runner = Matter.Runner.create()
  Matter.Runner.run(runner, engine)

  const wallOpt = { isStatic: true, render: { visible: false } }
  Matter.Composite.add(engine.world, [
    Matter.Bodies.rectangle(window.innerWidth / 2, -50, window.innerWidth, 100, wallOpt),
    Matter.Bodies.rectangle(window.innerWidth / 2, window.innerHeight + 50, window.innerWidth, 100, wallOpt),
    Matter.Bodies.rectangle(-50, window.innerHeight / 2, 100, window.innerHeight, wallOpt),
    Matter.Bodies.rectangle(window.innerWidth + 50, window.innerHeight / 2, 100, window.innerHeight, wallOpt)
  ])

  const mouse = Matter.Mouse.create(render.canvas)
  mouseConstraint = Matter.MouseConstraint.create(engine, {
    mouse: mouse,
    constraint: { stiffness: 0.2, render: { visible: false } }
  })
  Matter.Composite.add(engine.world, mouseConstraint)
  render.mouse = mouse

  Matter.Events.on(render, 'beforeRender', () => {
    bubblesData.forEach(b => {
      const x = b.body.position.x - b.width / 2
      const y = b.body.position.y - b.height / 2
      b.element.style.transform = `translate(${x}px, ${y}px) rotate(${b.body.angle}rad)`
    })
  })

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  if (render) {
    render.canvas.width = window.innerWidth
    render.canvas.height = window.innerHeight
  }
}

function addBubble(text, role) {
  if (!domContainer.value || !engine) return

  const tempDiv = document.createElement('div')
  tempDiv.className = `chat-bubble ${role}`
  tempDiv.textContent = text
  tempDiv.style.visibility = 'hidden'
  document.body.appendChild(tempDiv)
  const { width, height } = tempDiv.getBoundingClientRect()
  document.body.removeChild(tempDiv)

  const bubbleDiv = document.createElement('div')
  bubbleDiv.className = `chat-bubble ${role}`
  bubbleDiv.textContent = text

  const startX = window.innerWidth / 2 + (Math.random() * 100 - 50)
  const startY = window.innerHeight - 150

  const body = Matter.Bodies.rectangle(startX, startY, width, height, {
    restitution: 0.8,
    frictionAir: 0.05,
    density: 0.002,
    render: { visible: false }
  })

  Matter.Body.applyForce(body, body.position, { x: (Math.random() - 0.5) * 0.05, y: -0.1 })
  Matter.Composite.add(engine.world, body)
  domContainer.value.appendChild(bubbleDiv)
  bubblesData.push({ body, element: bubbleDiv, width, height })
}

async function sendMessage() {
  const text = draft.value.trim()
  if (!text || isLoading.value) return

  addBubble(text, 'user')
  draft.value = ''
  isLoading.value = true

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })

    if (res.ok) {
      const data = await res.json()
      addBubble(data.reply, 'ai')
    } else {
      addBubble('⚠️ 서버 에러가 발생했습니다.', 'ai')
    }
  } catch (err) {
    addBubble('⚠️ 네트워크 연결에 실패했습니다.', 'ai')
  } finally {
    isLoading.value = false
  }
}

function restartChat() {
  // Clear all bubbles
  bubblesData.forEach(b => {
    Matter.Composite.remove(engine.world, b.body)
    if (b.element.parentNode) b.element.parentNode.removeChild(b.element)
  })
  bubblesData = []
  
  // 환영 메시지
  addBubble('안티그래비티 챗봇 모드입니다! 궁금한 게임이나 모드를 편하게 물어보세요 🚀', 'ai')
}

onMounted(() => {
  initMatter()
  setTimeout(() => {
    addBubble('안티그래비티 챗봇 모드입니다! 궁금한 게임이나 모드를 편하게 물어보세요 🚀', 'ai')
  }, 500)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (render) {
    Matter.Render.stop(render)
    render.canvas.remove()
  }
  if (runner) Matter.Runner.stop(runner)
  if (engine) Matter.Engine.clear(engine)
})
</script>

<template>
  <div class="chat-page antigravity-mode">
    
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
          <button class="pill-btn" type="button" @click="restartChat">
            🔄 리셋
          </button>
        </div>
      </header>
    </div>

    <!-- Matter.js Canvas Container -->
    <div ref="matterContainer" class="matter-container"></div>
    
    <!-- Floating DOM Elements Container -->
    <div ref="domContainer" class="dom-container"></div>

    <div class="input-container">
      <input 
        type="text" 
        v-model="draft" 
        @keypress.enter="sendMessage" 
        placeholder="무중력 공간에 메시지를 던져보세요..." 
        :disabled="isLoading"
      />
      <button @click="sendMessage" :disabled="isLoading">전송</button>
    </div>
  </div>
</template>

<style scoped>
.antigravity-mode {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #1e1e2f, #2a2a4a);
  color: white;
  font-family: sans-serif;
}

.chat-nav-wrapper {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: 100%;
  display: flex;
  justify-content: center;
}

.chat-pill-nav {
  display: flex;
  align-items: center;
  gap: 20px;
  background: rgba(10, 10, 20, 0.75);
  padding: 10px 20px;
  border-radius: 50px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.pill-logo {
  background: none;
  border: none;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  cursor: pointer;
}

.pill-actions {
  display: flex;
  gap: 10px;
}

.pill-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.pill-btn:hover {
  background: rgba(255,255,255,0.2);
}

.matter-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.dom-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.input-container {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  gap: 10px;
  background: rgba(10, 10, 20, 0.75);
  padding: 10px;
  border-radius: 50px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  width: 90%;
  max-width: 600px;
}

.input-container input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  padding: 10px 20px;
  font-size: 1.1rem;
  outline: none;
}

.input-container input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-container button {
  background: #6c5ce7;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 40px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.input-container button:hover:not(:disabled) {
  background: #a29bfe;
  transform: scale(1.05);
}

.input-container button:active:not(:disabled) {
  transform: scale(0.95);
}

.input-container button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

<style>
/* Global styles for chat bubbles so they can be injected into body or domContainer */
.chat-bubble {
  position: absolute;
  max-width: min(70vw, 480px);
  background: rgba(20, 20, 35, 0.92);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.35);
  padding: 16px 26px;
  border-radius: 24px;
  font-size: 1.15rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
  transform-origin: center center;
  color: #ffffff;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.6);
  font-family: sans-serif;
}

.chat-bubble.user {
  background: rgba(30, 90, 160, 0.92);
  border-color: rgba(140, 210, 255, 0.7);
}

.chat-bubble.ai {
  background: rgba(150, 40, 120, 0.92);
  border-color: rgba(255, 150, 220, 0.7);
}
</style>
