<template>
  <div class="tip">
    <div class="item">
      <span class="label">战绩：</span>
      <span class="content">{{ zhan_ji }}</span>
    </div>
    <div class="item">
      <span class="label">日志：</span>
      <span class="content">{{ log }}</span>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { ref, onMounted } from 'vue';
const zhan_ji = ref('');
const log = ref('');
onMounted(() => {
  window.airscript.call('tip_mounted', 'onLogs');
});
window.onLogs = (data: { zhan_ji: string; log: string }) => {
  if (data.zhan_ji) {
    zhan_ji.value = data.zhan_ji;
  }
  if (data.log) {
    log.value = data.log;
  }
};
</script>
<style lang="scss">
.tip {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  top: 0;
  padding: 6px;
  background-color: rgba(0, 0, 0, 0.3);
  .item {
    color: #fff;
    font-size: 8px;
  }
}
</style>
