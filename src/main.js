import { createApp } from 'vue'
import App from './App.vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'

import $ from 'jquery'

window.$ = window.jQuery = $

import router from './routers';
import './axios'
import '@fortawesome/fontawesome-free/css/all.css'
import './registerServiceWorker'

const app = createApp(App)
app.use(router)
app.mount ('#app')