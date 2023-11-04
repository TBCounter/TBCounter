import { createApp } from 'vue'
import { createPinia } from 'pinia'
// @ts-ignore
import WaveUI from 'wave-ui'
import 'wave-ui/dist/wave-ui.css'
import 'material-design-icons/iconfont/material-icons.css'
// @ts-ignore
import App from './App.vue'
import router from './router'

const app = createApp(App)

new WaveUI(app, { iconsLigature: 'material-icons' })

app.use(createPinia())
app.use(router)

app.mount('#app')