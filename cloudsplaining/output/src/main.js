import { createApp } from 'vue';
import App from './App.vue';
import router from './routes/routes';
import { Components, Directives, createBootstrap } from 'bootstrap-vue-next';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

const app = createApp(App);

app.use(router);
app.use(createBootstrap());

Object.entries(Components).forEach(([name, component]) => {
  app.component(name, component);
});

const directiveNameFromKey = (key) =>
  key.replace(/^vB/, 'b').replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);

Object.entries(Directives).forEach(([key, directive]) => {
  app.directive(directiveNameFromKey(key), directive);
});
app.mount('#app');
