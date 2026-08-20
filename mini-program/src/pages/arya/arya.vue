<template>
  <view class="arya-page">
    <!-- 消息列表 -->
    <scroll-view scroll-y class="msg-list" :scroll-into-view="scrollInto">
      <view v-if="needLogin" class="login-tip">
        <text>登录后即可与 Arya 对话 ~</text>
        <button class="login-btn" @click="goLogin">去登录</button>
      </view>
      <view v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
        <view class="bubble">
          <text>{{ m.content }}</text>
          <button
            v-if="m.role === 'assistant' && m.callMaster"
            class="call-btn"
            @click="contactVisible = true"
          >
            {{ m.callHint || '联系店主定制' }}
          </button>
        </view>
      </view>
      <view v-if="sending" class="msg-row assistant">
        <view class="bubble typing">Arya 正在输入...</view>
      </view>
      <view id="bottom"></view>
    </scroll-view>

    <!-- 输入栏 -->
    <view class="input-bar">
      <input
        v-model="input"
        class="input"
        placeholder="和 Arya 聊聊吧~"
        confirm-type="send"
        @confirm="onSend"
      />
      <button class="send-btn" @click="onSend">发送</button>
      <view class="clear" @click="onClear">清空</view>
    </view>

    <contact-modal :visible="contactVisible" @close="contactVisible = false" />
  </view>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'

import { clearSessions, sendMessage } from '@/api/arya'
import { useUserStore } from '@/stores/user'
import ContactModal from '@/components/contact-modal.vue'

interface Msg {
  role: 'user' | 'assistant'
  content: string
  callMaster: boolean
  callHint: string
}

const userStore = useUserStore()
const messages = ref<Msg[]>([])
const input = ref('')
const sending = ref(false)
const contactVisible = ref(false)
const scrollInto = ref('')
const needLogin = computed(() => !userStore.isLoggedIn)

onLoad(() => {
  // 欢迎语
  pushAssistant('你好呀~ 我是 Arya, Arya_handcraft 的毛毡猫咪小助手,有什么想了解的吗?喵~')
})

onShow(() => {
  if (userStore.isLoggedIn) {
    refreshLoginUser()
  }
})

async function refreshLoginUser() {
  if (!uni.getStorageSync('access_token')) return
  try {
    await userStore.fetchUser()
  } catch {
    // token 失效
  }
}

function pushAssistant(content: string, callMaster = false, callHint = '') {
  messages.value.push({ role: 'assistant', content, callMaster, callHint })
  scrollToBottom()
}

function scrollToBottom() {
  setTimeout(() => {
    scrollInto.value = 'bottom'
  }, 50)
}

async function onSend() {
  const text = input.value.trim()
  if (!text || sending.value) return
  if (!userStore.isLoggedIn) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }
  input.value = ''
  messages.value.push({ role: 'user', content: text, callMaster: false, callHint: '' })
  sending.value = true
  scrollToBottom()
  try {
    const res = await sendMessage(text)
    pushAssistant(
      res.reply,
      res.intent === 'call_master',
      res.call_master_hint || '',
    )
    // 若意图是呼叫主人,自动呼出联系弹窗
    if (res.intent === 'call_master') {
      setTimeout(() => {
        contactVisible.value = true
      }, 300)
    }
  } catch {
    pushAssistant('喵~ 我有点走神了,请稍后再试。')
  } finally {
    sending.value = false
  }
}

async function onClear() {
  try {
    await clearSessions()
  } catch {
    // ignore
  }
  messages.value = []
  pushAssistant('记忆已清空,我们重新开始吧~ 喵')
}

function goLogin() {
  uni.switchTab({ url: '/pages/mine/mine' })
}
</script>
<style scoped lang="scss">
.arya-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #faf6f0;
}
.msg-list {
  flex: 1;
  overflow: hidden;
  padding: 24rpx;
  box-sizing: border-box;
}
.login-tip {
  margin-top: 20vh;
  text-align: center;
  color: #b9b1ac;
  font-size: 26rpx;
}
.login-btn {
  margin-top: 24rpx;
  width: 320rpx;
  border-radius: 999rpx;
  background: #c9a9a6;
  color: #fff;
  border: none;
  font-size: 26rpx;
}
.msg-row {
  display: flex;
  margin-bottom: 24rpx;
}
.msg-row.user {
  justify-content: flex-end;
}
.msg-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 78%;
  padding: 20rpx 24rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  line-height: 1.6;
  color: #5a5350;
  word-break: break-word;
}
.msg-row.user .bubble {
  background: #c9a9a6;
  color: #fff;
}
.msg-row.assistant .bubble {
  background: #fff;
}
.bubble .typing {
  color: #b9b1ac;
}
.call-btn {
  margin-top: 16rpx;
  border-radius: 999rpx;
  background: #a98b84;
  color: #fff;
  border: none;
  font-size: 24rpx;
  padding: 0 24rpx;
}
.input-bar {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx 32rpx;
  background: #fff;
  border-top: 1px solid #f0ebe6;
}
.input {
  flex: 1;
  height: 72rpx;
  background: #faf6f0;
  border-radius: 999rpx;
  padding: 0 24rpx;
  font-size: 26rpx;
}
.send-btn {
  border-radius: 999rpx;
  background: #c9a9a6;
  color: #fff;
  border: none;
  font-size: 26rpx;
  padding: 0 32rpx;
  line-height: 72rpx;
  height: 72rpx;
  margin: 0;
}
.clear {
  color: #b9b1ac;
  font-size: 24rpx;
}
</style>