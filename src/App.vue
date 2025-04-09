<template>
  <div id="app">
    <router-view />
  </div>
</template>
<script lang="ts" setup>
import { showToast } from 'vant';

window.toast = (msg: string) => {
  showToast(msg);
};
</script>
<style>
body {
  font-size: 16px;
  /* background-color: #f8f8f8; */
  -webkit-font-smoothing: antialiased;
  background-color: transparent;
}
</style>
