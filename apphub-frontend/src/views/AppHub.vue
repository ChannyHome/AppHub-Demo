<script setup lang="ts">
import TitleView from "./TitleView.vue";
import AppView from "./AppView.vue";
import CommandTest from "./CommandTest.vue";
</script>

<template>
  <div>
    <div><TitleView /></div>
    <div class="center">
      <AppView msg="Welcome!! AppHub (DEMO)" />
      <CommandTest />
    </div>
  </div>
</template>

<style scoped>
.center {
  width: min(800px, 100%); /* 가운데 컬럼 폭 */
  margin: 0 auto; /* 핵심: 가운데 */
  display: flex;
  flex-direction: column;
  gap: 18px; /* AppView와 CommandTest 사이 간격 */
}
</style>
