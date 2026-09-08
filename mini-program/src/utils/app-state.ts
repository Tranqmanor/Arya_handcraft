// 应用级状态:模块作用域,页面实例重建(redirectTo 返回首页)不重置,
// 仅小程序冷启动(重新加载 JS 包)时才回到初始值——用于欢迎页只展示一次。
export const appState = {
  welcomed: false,
}