<template>
  <van-collapse v-model="activeNames">
    <van-collapse-item
      v-for="scene in props.scenes"
      :key="scene.id"
      :name="scene.id"
    >
      <template #title>
        <div class="scene-title">
          <van-icon
            class="icon"
            name="fire-o"
            :color="scene.checked ? '#ee0a24' : ''"
          />
          {{ scene.name }}
          <van-switch
            class="switch"
            @click.stop
            v-model="scene.checked"
            size="14px"
          />
          <van-rate
            @click.stop
            icon="good-job"
            void-icon="good-job-o"
            v-model="scene.sort"
            :count="props.scenes.length"
          />
        </div>
      </template>
      <van-row>
        <van-row>
          <van-col span="24">
            <van-field label-width="56" name="time" label="最长时间">
              <template #input>
                <van-radio-group v-model="scene.time" direction="horizontal">
                  <van-radio :name="3600">1小时</van-radio>
                  <van-radio :name="7200">2小时</van-radio>
                  <van-radio :name="10800">3小时</van-radio>
                  <van-radio :name="14400">4小时</van-radio>
                </van-radio-group>
              </template>
            </van-field>
          </van-col>
        </van-row>
        <van-col span="24">
          <van-field label-width="56" name="gw_checked" label="指定怪物">
            <template #input>
              <van-checkbox-group
                v-model="scene.gw_checked"
                direction="horizontal"
              >
                <van-checkbox
                  v-for="gw in scene.gws"
                  :name="gw"
                  shape="square"
                  >{{ gw }}</van-checkbox
                >
              </van-checkbox-group>
            </template>
          </van-field>
        </van-col>
      </van-row>
    </van-collapse-item>
  </van-collapse>
</template>
<script lang="ts" setup>
import { ref } from 'vue';
import { Config } from '@/types';
const props = defineProps<{ scenes: Config['scenes'] }>();
const activeNames = ref(['1']);
</script>
<style lang="scss" scoped>
.scene-title {
  display: flex;
  align-items: center;
  .icon {
    margin-right: 6px;
  }
  .switch {
    margin-left: 6px;
    margin-right: 6px;
  }
}
</style>
