<template>
  <div class="layout">
    <div class="header">VIP 偷卡</div>
    <div class="body">
      <van-tabs v-model:active="activeTab">
        <van-form>
          <van-tab title="基本设置" name="base">
            <base-config :base="config.base" />
          </van-tab>
          <van-tab title="场景设置" name="scene">
            <scene-config :scenes="config.scenes" />
          </van-tab>
        </van-form>
      </van-tabs>
    </div>
    <div class="footer">
      <van-action-bar>
        <van-action-bar-button type="danger" text="退出脚本" @click="stop" />
        <van-action-bar-button type="primary" text="运行脚本" @click="start" />
      </van-action-bar>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { showConfirmDialog } from 'vant';
import { showToast } from 'vant';
import { Config } from '@/types';
import BaseConfig from '@/components/BaseConfig.vue';
import SceneConfig from '@/components/SceneConfig.vue';
const activeTab = ref<string>('base');
const config = ref<Config>({
  base: {
    xue: 0.5,
    lan: 0.2,
    check_dao_ju: 1,
  },
  scenes: [],
});
onMounted(() => {
  window.airscript.call('mounted', 'onConfig');
});

const start = () => {
  const scenes = config.value.scenes;
  const sortedScenes = [...scenes].sort((a, b) => {
    // 优先按 checked 状态排序（true 在前）
    if (a.checked !== b.checked) {
      return a.checked ? -1 : 1;
    }
    // 相同状态下按 sort 升序排列
    return b.sort - a.sort;
  });
  config.value.scenes = sortedScenes;
  window.airscript.call('start', JSON.stringify(config.value));
};

const stop = () => {
  showConfirmDialog({
    title: '提示',
    message: '确认退出脚本？',
  }).then(() => {
    showToast('退出成功！');
    setTimeout(() => {
      window.airscript.call('stop', '');
    }, 2000);
  });
};
window.onConfig = (data: Config) => {
  const scenes = data.scenes;
  const sortedScenes = [...scenes].sort((a, b) => {
    // 优先按 checked 状态排序（true 在前）
    if (a.checked !== b.checked) {
      return a.checked ? -1 : 1;
    }
    // 相同状态下按 sort 升序排列
    return b.sort - a.sort;
  });
  data.scenes = sortedScenes;
  config.value = data;
};
</script>

<style lang="scss">
.layout {
  width: 100vw;
  height: 100vh;
  border-radius: 10px;
  background-color: #f8f8f8;
  overflow: hidden;
  .header {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 50px;
    font-weight: bold;
    color: rgb(205, 127, 50);
    font-size: 20px;
    background-color: #fff;
    border-bottom: 1px solid #eff2f5;
  }
  .body {
    height: calc(100% - 100px);
    overflow: auto;
    background-color: #eff2f5;
    .van-tabs {
      height: 100%;
      .van-tabs__wrap {
        border-bottom: 1px solid #eff2f5;
      }
      .van-tabs__content {
        height: calc(100% - 46px);
        background-color: #fff;
        overflow: auto;
      }
    }
  }
  .van-action-bar {
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
  }
}
</style>
