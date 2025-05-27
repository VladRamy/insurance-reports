import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    isAuthenticated: false
  },
  mutations: {
    SET_AUTH(state, payload) {
      state.isAuthenticated = payload
    }
  },
  actions: {
    login({ commit }) {
      commit('SET_AUTH', true)
    },
    logout({ commit }) {
      commit('SET_AUTH', false)
    }
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated
  }
})
