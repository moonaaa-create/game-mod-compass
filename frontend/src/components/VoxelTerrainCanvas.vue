<script setup>
/**
 * VoxelTerrainCanvas.vue
 * ov6.html 3D Voxel Engine (InstancedMesh 60x60 terrain, river, trees, fog, drone camera)
 * Full-screen fixed background renderer (100vw x 100vh)
 */
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as THREE from 'three'

const props = defineProps({
  theme: { type: String, default: 'light' },
  isPaused: { type: Boolean, default: false },
})

const emit = defineEmits(['canvas-click'])

const canvasRef = ref(null)
const containerRef = ref(null)

let scene, camera, renderer, animationFrameId
let grassMesh, waterMesh, woodMesh, leafMesh
let compassGroup, robloxCube, mcCube
let ambientLight, sunLight, cyanPoint
let mouseX = 0
let mouseY = 0
let time = 0

function initVoxelEngine() {
  if (!canvasRef.value || !containerRef.value) return

  const width = window.innerWidth
  const height = window.innerHeight

  // 1. Scene & Fog & Camera
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 200)

  // 2. Renderer
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: false,
    powerPreference: 'high-performance',
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(1) // 1 to match ov6.html fast performance

  // 3. Lights (from ov6.html)
  ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
  scene.add(ambientLight)

  sunLight = new THREE.DirectionalLight(0xfffaed, 0.7)
  sunLight.position.set(30, 50, 20)
  scene.add(sunLight)

  cyanPoint = new THREE.PointLight(0x3b82f6, 1.2, 30)
  cyanPoint.position.set(0, 8, 0)
  scene.add(cyanPoint)

  // Apply Day / Night Theme atmosphere
  scene.fog = new THREE.Fog(0x82c0e7, 30, 95)
  updateThemeLighting(props.theme === 'dark')

  // 4. Voxel Terrain Grid (from ov6.html)
  const boxGeo = new THREE.BoxGeometry(1, 1, 1)
  const gridSize = 60
  const offset = gridSize / 2
  const maxBlocks = gridSize * gridSize * 4

  const grassMat = new THREE.MeshLambertMaterial({ color: 0xffffff })
  const waterMat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 })
  const woodMat = new THREE.MeshLambertMaterial({ color: 0x5c3a21 })
  const leafMat = new THREE.MeshLambertMaterial({ color: 0x2e6631 })

  grassMesh = new THREE.InstancedMesh(boxGeo, grassMat, maxBlocks)
  waterMesh = new THREE.InstancedMesh(boxGeo, waterMat, maxBlocks)
  woodMesh = new THREE.InstancedMesh(boxGeo, woodMat, 1200)
  leafMesh = new THREE.InstancedMesh(boxGeo, leafMat, 3500)

  const dummy = new THREE.Object3D()
  const tempColor = new THREE.Color()

  const grassColors = [new THREE.Color(0x4d8c36), new THREE.Color(0x52943a), new THREE.Color(0x447f2e)]
  const shallowWater = new THREE.Color(0x38b6ff)
  const deepWater = new THREE.Color(0x1d70e3)

  let wdIdx = 0, lIdx = 0
  const waterLevel = -0.5

  function plantSimpleTree(tx, ty, tz) {
    for (let h = 0; h < 3; h++) {
      dummy.position.set(tx, ty + h, tz)
      dummy.updateMatrix()
      woodMesh.setMatrixAt(wdIdx++, dummy.matrix)
    }
    for (let lx = -1; lx <= 1; lx++) {
      for (let lz = -1; lz <= 1; lz++) {
        for (let ly = 2; ly <= 3; ly++) {
          dummy.position.set(tx + lx, ty + ly, tz + lz)
          dummy.updateMatrix()
          leafMesh.setMatrixAt(lIdx++, dummy.matrix)
        }
      }
    }
  }

  let gIdx = 0, wIdx = 0
  for (let x = 0; x < gridSize; x++) {
    for (let z = 0; z < gridSize; z++) {
      const worldX = x - offset
      const worldZ = z - offset

      const riverVal = Math.sin(worldX * 0.12) * 4 + Math.cos(worldZ * 0.08) * 3
      const isRiver = Math.abs(worldZ - riverVal) < 2.2

      let y = Math.floor(
        Math.sin(worldX * 0.1) * 2 +
        Math.cos(worldZ * 0.1) * 2.5 +
        Math.sin((worldX + worldZ) * 0.05) * 4
      )

      if (isRiver) y = Math.min(y, -1)

      if (y >= 0) {
        dummy.position.set(worldX, y, worldZ)
        dummy.updateMatrix()
        grassMesh.setMatrixAt(gIdx, dummy.matrix)

        tempColor.copy(grassColors[(x + z) % grassColors.length])
        grassMesh.setColorAt(gIdx++, tempColor)

        if (!isRiver && Math.random() < 0.02 && Math.abs(worldX) > 4 && Math.abs(worldZ) > 4) {
          plantSimpleTree(worldX, y + 1, worldZ)
        }
      } else {
        dummy.position.set(worldX, waterLevel, worldZ)
        dummy.updateMatrix()
        waterMesh.setMatrixAt(wIdx, dummy.matrix)

        const depthFactor = Math.random() * 0.5
        tempColor.copy(shallowWater).lerp(deepWater, depthFactor)
        waterMesh.setColorAt(wIdx++, tempColor)
      }
    }
  }

  if (grassMesh.instanceColor) grassMesh.instanceColor.needsUpdate = true
  if (waterMesh.instanceColor) waterMesh.instanceColor.needsUpdate = true

  scene.add(grassMesh)
  scene.add(waterMesh)
  scene.add(woodMesh)
  scene.add(leafMesh)

  // 5. Hero 3D Objects: 🧭 Mod Compass + Roblox Block + Minecraft Block
  const compassGroupTemp = new THREE.Group()

  const ringGeo = new THREE.TorusGeometry(2, 0.18, 16, 32)
  const goldMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8, roughness: 0.2 })
  const ring = new THREE.Mesh(ringGeo, goldMat)
  ring.rotation.x = Math.PI / 2
  compassGroupTemp.add(ring)

  const dialGeo = new THREE.CylinderGeometry(1.9, 1.9, 0.1, 32)
  const dialMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 })
  const dial = new THREE.Mesh(dialGeo, dialMat)
  compassGroupTemp.add(dial)

  const needleGeo = new THREE.ConeGeometry(0.35, 2.2, 4)
  const needleNorthMat = new THREE.MeshStandardMaterial({ color: 0xef4444 })
  const needleNorth = new THREE.Mesh(needleGeo, needleNorthMat)
  needleNorth.position.z = -0.9
  needleNorth.rotation.x = Math.PI / 2
  compassGroupTemp.add(needleNorth)

  const needleSouthMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6 })
  const needleSouth = new THREE.Mesh(needleGeo, needleSouthMat)
  needleSouth.position.z = 0.9
  needleSouth.rotation.x = -Math.PI / 2
  compassGroupTemp.add(needleSouth)

  compassGroupTemp.position.set(0, 5.5, 0)
  compassGroup = compassGroupTemp
  scene.add(compassGroup)

  const rbBoxGeo = new THREE.BoxGeometry(1.8, 1.8, 1.8)
  const rbBoxMat = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.1 })
  const rbBox = new THREE.Mesh(rbBoxGeo, rbBoxMat)
  rbBox.position.set(-6, 6, -2)
  robloxCube = rbBox
  scene.add(robloxCube)

  const mcGroup = new THREE.Group()
  const mcBoxGeo = new THREE.BoxGeometry(1.8, 1.8, 1.8)
  const mcBoxMat = new THREE.MeshStandardMaterial({ color: 0x10b981 })
  const mcBox = new THREE.Mesh(mcBoxGeo, mcBoxMat)
  mcGroup.add(mcBox)

  mcGroup.position.set(6, 5, 2)
  mcCube = mcGroup
  scene.add(mcCube)

  // Event Listeners
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', onWindowResize)

  initVoxelEngineAnimation()
}

function initVoxelEngineAnimation() {
  function animate() {
    if (props.isPaused) {
      animationFrameId = null
      return
    }
    animationFrameId = requestAnimationFrame(animate)
    time += 0.0015

    // Drone Camera Orbit around (0,0,0) as in ov6.html
    camera.position.x = Math.sin(time) * 35 + mouseX * 4
    camera.position.z = Math.cos(time * 0.8) * 35 + mouseY * 4
    camera.position.y = 22 + Math.sin(time * 0.5) * 2

    camera.lookAt(0, 2, 0)

    // Compass float & spin
    if (compassGroup) {
      compassGroup.rotation.y = time * 2.5
      compassGroup.rotation.x = Math.sin(time * 3) * 0.15
      compassGroup.position.y = 5.5 + Math.sin(time * 4) * 0.3
    }

    // Cubes float
    if (robloxCube) {
      robloxCube.rotation.x = time * 3
      robloxCube.rotation.y = time * 2
      robloxCube.position.y = 6 + Math.sin(time * 5) * 0.4
    }

    if (mcCube) {
      mcCube.rotation.x = -time * 2.5
      mcCube.rotation.y = time * 3
      mcCube.position.y = 5 + Math.cos(time * 4.5) * 0.4
    }

    renderer.render(scene, camera)
  }

  animate()
}

function updateThemeLighting(isDark) {
  if (!scene) return

  // Day / Night Atmosphere
  const skyHex = isDark ? 0x090d16 : 0x82c0e7
  const fogHex = isDark ? 0x0f172a : 0x82c0e7

  scene.background = new THREE.Color(skyHex)
  if (scene.fog) {
    scene.fog.color.setHex(fogHex)
    scene.fog.near = isDark ? 25 : 30
    scene.fog.far = isDark ? 85 : 95
  }

  if (ambientLight) {
    ambientLight.color.setHex(isDark ? 0x1e293b : 0xffffff)
    ambientLight.intensity = isDark ? 0.3 : 0.8
  }

  if (sunLight) {
    sunLight.color.setHex(isDark ? 0x818cf8 : 0xfffaed)
    sunLight.intensity = isDark ? 0.25 : 0.7
  }

  if (cyanPoint) {
    cyanPoint.color.setHex(isDark ? 0x38bdf8 : 0x3b82f6)
    cyanPoint.intensity = isDark ? 2.2 : 1.2
  }

  if (props.isPaused && renderer && camera) {
    renderer.render(scene, camera)
  }
}

function onMouseMove(event) {
  const windowHalfX = window.innerWidth / 2
  const windowHalfY = window.innerHeight / 2
  mouseX = (event.clientX - windowHalfX) / windowHalfX
  mouseY = (event.clientY - windowHalfY) / windowHalfY
}

function onWindowResize() {
  if (!renderer || !camera) return
  const width = window.innerWidth
  const height = window.innerHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  if (scene && camera) {
    renderer.render(scene, camera)
  }
}

watch(() => props.theme, (newTheme) => {
  updateThemeLighting(newTheme === 'dark')
})

watch(() => props.isPaused, (paused) => {
  if (paused) {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }
  } else {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }
    // Resume 3D animation loop
    if (scene && camera) {
      const width = window.innerWidth
      const height = window.innerHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    }
    initVoxelEngineAnimation()
  }
})

onMounted(() => {
  initVoxelEngine()
})

onBeforeUnmount(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', onWindowResize)
  if (renderer) renderer.dispose()
})
</script>

<template>
  <div ref="containerRef" class="voxel-canvas-container" @click="emit('canvas-click')">
    <canvas ref="canvasRef" class="voxel-canvas"></canvas>
  </div>
</template>

<style scoped>
.voxel-canvas-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: 0;
  pointer-events: auto;
  background-color: #0f172a;
}

.voxel-canvas {
  width: 100vw;
  height: 100vh;
  display: block;
}

.engine-control-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  pointer-events: auto;
}

.engine-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #ffffff;
  padding: 0.65rem 1.15rem;
  border-radius: 30px;
  font-size: 0.88rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.engine-toggle-btn:hover {
  transform: translateY(-3px);
  background: rgba(15, 23, 42, 0.9);
  border-color: #3b82f6;
  box-shadow: 0 12px 30px rgba(59, 130, 246, 0.4);
}

.engine-toggle-btn.paused {
  background: rgba(239, 68, 68, 0.3);
  border-color: #ef4444;
  color: #fecaca;
}

.engine-toggle-btn.paused:hover {
  background: rgba(239, 68, 68, 0.5);
  box-shadow: 0 12px 30px rgba(239, 68, 68, 0.5);
}

.status-indicator {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background-color: #ef4444;
  box-shadow: 0 0 8px #ef4444;
  transition: all 0.2s;
}

.status-indicator.active {
  background-color: #10b981;
  box-shadow: 0 0 10px #10b981;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(1); opacity: 0.8; }
}

.saving-badge {
  font-size: 0.72rem;
  background: rgba(239, 68, 68, 0.35);
  color: #fecaca;
  padding: 2px 8px;
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.5);
  margin-left: 2px;
}
</style>
