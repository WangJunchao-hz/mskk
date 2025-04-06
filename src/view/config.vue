<template>
  <div class="layout">
    <div class="header">VIP 偷卡</div>
    <div class="body">
      <van-tabs v-model:active="activeTab">
        <van-form>
          <van-tab title="基本设置" name="base">
            <van-row>
              <van-col span="8">
                <van-field label-width="50" name="stepper" label="血量(%)">
                  <template #input>
                    <van-stepper
                      v-model="config.base.xue"
                      min="0"
                      max="1"
                      step="0.01"
                      decimal-length="2"
                    />
                  </template>
                </van-field>
              </van-col>
              <van-col span="8">
                <van-field label-width="50" name="stepper" label="蓝量(%)">
                  <template #input>
                    <van-stepper
                      v-model="config.base.lan"
                      min="0"
                      max="1"
                      step="0.01"
                      decimal-length="2"
                    />
                  </template>
                </van-field>
              </van-col>
              <van-col span="8">span: 8</van-col>
              <van-col span="8">span: 8</van-col>
            </van-row>
          </van-tab>
          <van-tab title="场景设置" name="scene">内容 2</van-tab>
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
import { useRouter } from 'vue-router';
import { showConfirmDialog } from 'vant';
import { showToast } from 'vant';
import { Config } from '@/types';
const router = useRouter();
const activeTab = ref<string>('base');
const config = ref<Config>({
  base: {
    xue: 0.5,
    lan: 0.2,
  },
});
onMounted(() => {
  window.airscript.call('mounted', 'onConfig');
});

const start = () => {
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
  console.log(JSON.stringify(data));
  config.value = data;
};
window.jumpToTip = () => {
  router.push('tip');
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
        height: calc(100% - 44px);
        background-color: #fff;
      }
    }
  }
  .van-action-bar {
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
  }
}
</style>
