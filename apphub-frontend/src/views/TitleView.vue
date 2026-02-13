<script setup lang="ts">
import { apphubApi } from "../api/apphub";
const downloadUrl = apphubApi.agentDownloadUrl();
</script>

<template>
  <div class="container">
    <a href="apphub://open" class="apphub-launch">
      <img
        :src="apphubApi.ShowImageUrl('AgentTray.png')"
        class="logo vue"
        alt="AppHub"
      />
      <div class="launch-text">AppHub Agent Launch</div>
    </a>
    <a class="download-agent-btn" :href="downloadUrl">
      ⬇ Download Agent (.msi)
    </a>
  </div>
</template>

<style scoped>
.container {
  text-align: center;
}

.apphub-launch {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
}

.launch-text {
  margin-top: 5px;
  font-size: 14px;
  color: #444;
  font-weight: bold;
}

.logo {
  height: 6em;
  /* padding: 1.5em; */
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}

.download-agent-btn {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  padding: 10px 16px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 800;
  color: #fff;

  background: linear-gradient(135deg, #2563eb, #38bdf8); /* blue */
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.22);
}
.download-agent-btn:hover {
  filter: brightness(1.05);
  transform: translateY(-1px);
}
</style>
