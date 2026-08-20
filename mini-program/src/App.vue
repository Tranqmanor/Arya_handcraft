<script setup lang="ts">
// 全局生命周期:欢迎页展示在 pages/index,此处只做应用级初始化
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  console.log('Arya_handcraft launch')
})
</script>

<style lang="scss">
/* 全局样式 */
page {
  background-color: $arya-cream;
  color: $arya-ink;
  font-size: 28rpx;
  font-family: -apple-system, 'PingFang SC', 'Helvetica Neue', Helvetica, sans-serif;
}

/* 通用主按钮(莫兰迪粉,胶囊) */
.arya-btn-primary {
  background: $arya-pink !important;
  color: #fff !important;
  border: none !important;
  border-radius: 999rpx !important;
  font-size: 30rpx;
}
.arya-btn-primary::after {
  border: none;
}

/* 通用次要按钮(白底描边) */
.arya-btn-outline {
  background: #fff !important;
  color: $arya-clay !important;
  border: 1px solid #e5ded8 !important;
  border-radius: 999rpx !important;
  font-size: 28rpx;
}
.arya-btn-outline::after {
  border: none;
}

/* 骨架屏占位色 */
.arya-skeleton {
  background: #f0ebe6;
  border-radius: 12rpx;
}

/* 卡片统一阴影 */
.arya-card {
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 4px 16px rgba(90, 83, 80, 0.06);
}
</style>
