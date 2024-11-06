import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './views/HomePage.vue'
import About from './views/AboutPage.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const app = createApp(App)

app.use(router)

// Disable production source maps
if (process.env.NODE_ENV === 'production') {
    app.config.productionSourceMap = false
  }

// This is a global After-Hook which calls the Snowplow page tracking event. See the
// Vue.js documentation here:
// https://router.vuejs.org/guide/advanced/navigation-guards.html#global-after-hooks
router.afterEach(() => {
    window.snowplow('trackPageView');
  })

app.mount('#app')


