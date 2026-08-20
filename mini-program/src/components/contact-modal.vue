<template>
  <view v-if="visible" class="modal-mask" @click="close">
    <view class="modal" @click.stop>
      <view class="title">联系店主</view>
      <image class="qr" src="/static/wechat-qr.png" mode="widthFix" @longpress="saveQr" />
      <view class="tip">{{ tip }}</view>
      <view class="hint">长按图片可保存二维码</view>
      <button class="close-btn" @click="close">关闭</button>
    </view>
  </view>
</template>
<script setup lang="ts">
const props = defineProps<{
  visible: boolean
  tip?: string
}>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

function close() {
  emit('close')
}

function saveQr() {
  uni.previewImage({
    urls: ['/static/wechat-qr.png'],
    current: '/static/wechat-qr.png',
  })
}
</script>
<style scoped lang="scss">
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.modal {
  width: 560rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.title {
  font-size: 34rpx;
  font-weight: 700;
  color: #5a5350;
  margin-bottom: 24rpx;
}
.qr {
  width: 400rpx;
  border-radius: 16rpx;
  background: #fff;
}
.tip {
  margin-top: 20rpx;
  font-size: 26rpx;
  color: #5a5350;
  text-align: center;
}
.hint {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #b9b1ac;
}
.close-btn {
  margin-top: 28rpx;
  width: 100%;
  border-radius: 999rpx;
  background: #c9a9a6;
  color: #fff;
  border: none;
  font-size: 28rpx;
}
</style>