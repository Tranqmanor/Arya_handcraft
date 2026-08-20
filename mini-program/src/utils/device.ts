// 本地工具:设备指纹

/** 获取/生成稳定的设备指纹(用于未登录时浏览量去重)。 */
export function getDeviceKey(): string {
  let key = uni.getStorageSync('device_key')
  if (!key) {
    key = `dev-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
    uni.setStorageSync('device_key', key)
  }
  return key
}