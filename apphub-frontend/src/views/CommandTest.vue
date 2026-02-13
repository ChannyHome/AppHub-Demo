<script setup lang="ts">
import { ref } from "vue";

const cmd = ref("");
</script>

<template>
  <section class="cmd-panel">
    <div class="cmd-title">Test AppHub Command</div>

    <div class="cmd-input-row">
      <span class="cmd-prefix">apphub://</span>

      <input class="cmd-input" type="text" v-model="cmd" placeholder="open" />
      <!-- 핵심 -->
      <a class="cmd-run" :href="`apphub://${cmd || 'open'}`"> Run </a>
    </div>

    <div class="cmd-actions">
      <a class="cmd-btn open" href="apphub://open">▶ Open</a>
      <a class="cmd-btn exit" href="apphub://exit">■ Exit</a>
    </div>
  </section>
</template>
<style scoped>
.cmd-panel {
  margin-top: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  background: #fff;
  max-width: 800px; /* 원하는 값으로 조정 가능 */
  text-align: center;
}
.cmd-title {
  font-size: 13px;
  font-weight: 700;
  color: #222;
  margin-bottom: 10px;
}

.cmd-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.cmd-input::placeholder {
  color: rgba(0, 0, 0, 0.35); /* 회색 open */
}

.cmd-input:focus {
  border-color: rgba(66, 184, 131, 0.45);
}

.cmd-run {
  padding: 9px 14px;
  border-radius: 10px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
  background: rgba(66, 184, 131, 0.12);
  color: #42b883;
  white-space: nowrap;
}
.cmd-run:hover {
  background: rgba(66, 184, 131, 0.22);
}

.cmd-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px;
}
/* 공통 버튼 */
.cmd-btn {
  padding: 8px 18px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

/* Open 버튼 */
.cmd-btn.open {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: #fff;
}
.cmd-btn.open:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}

/* Exit 버튼 (조금 톤 다운된 블루) */
.cmd-btn.exit {
  background: rgba(79, 172, 254, 0.15);
  color: #2f7fdc;
  border-color: rgba(79, 172, 254, 0.35);
}
.cmd-btn.exit:hover {
  background: rgba(79, 172, 254, 0.25);
}
</style>
