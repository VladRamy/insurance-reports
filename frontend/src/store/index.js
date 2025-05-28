import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    isAuthenticated: false,
    user: null
  },
  mutations: {
    SET_AUTH(state, payload) {
      state.isAuthenticated = payload
    },
    SET_USER(state, payload) {
      state.user = payload
    }
  },
  actions: {
    async checkAuth({ commit }) {
      const token = localStorage.getItem('authToken')
      if (token) {
        try {
          // Можно добавить запрос для проверки токена
          commit('SET_AUTH', true)
        } catch {
          localStorage.removeItem('authToken')
          commit('SET_AUTH', false)
        }
      }
    }
  }
})