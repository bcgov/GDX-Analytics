import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App)

app.use(router)

// This is a global After-Hook which calls the Snowplow page tracking event.
// Vue.js documentation here: https://router.vuejs.org/guide/advanced/navigation-guards.html#global-after-hooks
router.afterEach(() => {
    window.snowplow('trackPageView');
  })

app.mount('#app')


