<template>
  <div class="welcome">
    <div class="paw-wrap">
      <img class="paw" :src="`${BASE}icons/logo.png`" alt="Arya" />
    </div>
    <div class="brand">
      <div class="name">Arya手作</div>
      <div class="en-name">ARYA HANDCRAFT</div>
      <div class="sub">手作毛毡猫咪 · 管理</div>
    </div>
    <div class="loading-dots">
      <span class="dot" />
      <span class="dot" />
      <span class="dot" />
    </div>
  </div>
</template>

<script setup lang="ts">
const BASE = import.meta.env.BASE_URL
</script>

<style scoped>
.welcome {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #faf6f0 0%, #eadcd9 100%);
}

.paw-wrap {
  animation: paw-in 0.9s ease-out both;
}

.paw {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  background: #fff;
  animation: breathe 2.4s ease-in-out infinite;
}

@keyframes paw-in {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes breathe {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.08);
  }
}

.brand {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fade-up 0.8s 0.4s ease-out both;
}

.name {
  font-size: 40px;
  font-weight: 700;
  color: #a98b84;
  letter-spacing: 4px;
}

.en-name {
  margin-top: 10px;
  font-size: 14px;
  color: #b9b1ac;
  letter-spacing: 6px;
  text-transform: uppercase;
}

.sub {
  margin-top: 16px;
  font-size: 15px;
  color: #b9b1ac;
  letter-spacing: 2px;
}

.loading-dots {
  position: absolute;
  bottom: 12vh;
  display: flex;
  gap: 12px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #c9a9a6;
  animation: pulse 1.2s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>