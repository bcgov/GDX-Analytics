import Vue from 'vue'
import App from './App.vue'
import router from './router'

Vue.config.productionTip = false

new Vue({
  router,
  render: function (h) { return h(App) }
}).$mount('#app')

// This is a global After-Hook which calls the Snowplow page tracking event. See the
// Vue.js documentation here:
// https://router.vuejs.org/guide/advanced/navigation-guards.html#global-after-hooks
router.afterEach((to, from) => {
  window.snowplow('trackPageView');
})
