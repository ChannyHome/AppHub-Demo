<script setup lang="ts">
defineProps<{ msg: string }>();
import { apphubApi } from "../api/apphub";
</script>

<template>
  <h1>{{ msg }}</h1>
  <fieldset class="domain-fieldset">
    <!-- 헤더 라인 -->
    <legend class="domain-legend">
      <img
        :src="apphubApi.ShowImageUrl('HAWK.png')"
        class="domain-icon"
        alt="HAWk"
      />
    </legend>
    <!-- 앱 영역 -->
    <div class="domain-body">
      <a
        class="app-tile"
        href="apphub://run?cat=hawk&app=WCT&exe=WaferChipTracer.exe&admin=true"
      >
        <img
          class="app-icon"
          :src="apphubApi.ShowImageUrl('wct.png')"
          alt="WCT"
        />
        <div class="app-name">WCT</div>
      </a>
      <a
        class="app-tile"
        href="apphub://run?cat=hawk&app=WMM&exe=WaferMapMerge.exe&admin=true"
      >
        <img
          class="app-icon"
          :src="apphubApi.ShowImageUrl('wmm.png')"
          alt="WMM"
        />
        <div class="app-name">WMM</div>
      </a>
      <a
        class="app-tile"
        href="apphub://run?cat=hawk&app=WMO&exe=WaferMapOverlay.exe&admin=true"
      >
        <img
          class="app-icon"
          :src="apphubApi.ShowImageUrl('wmo.png')"
          alt="WMO"
        />
        <div class="app-name">WMO</div>
      </a>
      <a
        class="app-tile"
        href="apphub://run?cat=hawk&app=WME&exe=WaferMapEditor.exe&admin=true"
      >
        <img
          class="app-icon"
          :src="apphubApi.ShowImageUrl('wme.png')"
          alt="WME"
        />
        <div class="app-name">WME</div>
      </a>
    </div>
  </fieldset>
</template>

<style scoped>
h1 {
  display: flex;
  justify-content: center;
  font-size: 3.2em;
  line-height: 1.1;
}

.read-the-docs {
  color: #888;
}
.domain-card {
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 14px;
  padding: 16px;
  margin-top: 20px;
  background: #fff;
}

.domain-fieldset {
  border: 1px solid rgba(0, 0, 0, 0.18);
  border-radius: 14px;
  padding: 16px 16px 14px;
  margin-top: 22px;
  background: #fff;
}
/* 핵심: legend를 왼쪽으로 붙이기 */
.domain-legend {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  padding: 0 10px;
  background: #fff;

  /* ↓↓↓ 이 2개가 포인트 */
  margin-left: 0; /* 혹시 남아있는 auto 제거 */
  text-align: left;
}

.domain-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.domain-icon {
  width: 200px;
  height: 100px;
  margin-right: 10px;
}
.domain-line {
  flex: 1;
  height: 1px;
  background: rgba(0, 0, 0, 0.2);
}
.domain-body {
  display: flex;
  gap: 30px;
  margin-left: 7%;
  overflow-x: auto;
  padding-top: px;
}
.app-tile {
  width: 200x;
  padding: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  text-align: center;
  text-decoration: none;
}
.app-icon {
  width: 120px;
  height: 120px;
  display: block;
  margin: 0 auto 6px;
  will-change: filter;
  transition: filter 300ms;
}
.app-icon:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.app-icon.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
.app-name {
  font-size: 13px;
  color: #222;
  font-weight: 600;
  line-height: 1.1;
  white-space: nowrap;
}
</style>
