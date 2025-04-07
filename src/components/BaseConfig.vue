<template>
  <div>
    <van-row>
      <van-col span="12">
        <van-field label-width="50" name="xue" label="血量(%)">
          <template #input>
            <van-stepper v-model="props.base.xue" min="0" max="1" step="0.01" />
          </template>
        </van-field>
      </van-col>
      <van-col span="12">
        <van-field label-width="50" name="lan" label="蓝量(%)">
          <template #input>
            <van-stepper v-model="props.base.lan" min="0" max="1" step="0.01" />
          </template>
        </van-field>
      </van-col>
    </van-row>
    <van-row>
      <van-col span="12">
        <van-field label-width="98" name="check_dao_ju" label="检查背包(回合)">
          <template #input>
            <van-stepper v-model="props.base.check_dao_ju" min="1" step="1" />
          </template>
        </van-field>
      </van-col>
      <van-col span="12"> </van-col>
    </van-row>
  </div>
</template>
<script lang="ts" setup>
import { Config } from '@/types';
const props = defineProps<{ base: Config['base'] }>();
</script>
<style lang="scss" scoped></style>
