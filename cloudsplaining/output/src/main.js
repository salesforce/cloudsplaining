import {createApp} from 'vue';
import App from './App.vue';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import router from './routes/routes';

const app = createApp(App)
// Install BootstrapVue
app.use(BootstrapVue)
// Optionally install the BootstrapVue icon components plugin
app.use(IconsPlugin)

app.config.productionTip = false

new app({
  render: h => h(App),
  router,
}).mount('#app')
