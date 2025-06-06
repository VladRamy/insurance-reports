import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

Vue.config.productionTip = false

// Создаём новый экземпляр axios с настройками
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Добавляем interceptor для токена
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
    console.log('Token added to request:', token) // Для отладки
  } else {
    console.warn('No token available') // Для отладки
  }
  return config
})

Vue.prototype.$axios = apiClient

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

Vue.use(Toast, {
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true
})