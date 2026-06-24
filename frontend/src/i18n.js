import { createI18n } from 'vue-i18n'

const messages = {
  en: {
    brand: 'Sunny Tea House',
    shops: 'Shops',
    ai_generate: 'AI Generate',
    login: 'Login',
    register: 'Register',
    my: 'My',
    search_placeholder: 'Search shops',
    generate: 'Generate',
    submit: 'Submit',
    copy: 'Copy',
    avg: 'Avg',
    good_rate: 'Good rate'
  },
  zh: {
    brand: 'Sunny Tea House',
    shops: '商铺',
    ai_generate: 'AI 生成',
    login: '登录',
    register: '注册',
    my: '我的',
    search_placeholder: '搜索商铺',
    generate: '生成',
    submit: '提交',
    copy: '复制',
    avg: '人均',
    good_rate: '好评率'
  }
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  globalInjection: true,
  messages
})

export default i18n
