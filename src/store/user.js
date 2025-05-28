const state = {
  userInfo: JSON.parse(localStorage.getItem('userInfo')) || null
}

const mutations = {
  setUserInfo(state, userInfo) {
    state.userInfo = userInfo
    if (userInfo) {
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    } else {
      localStorage.removeItem('userInfo')
    }
  }
}

const actions = {
  login({ commit }, userInfo) {
    commit('setUserInfo', userInfo)
  },
  logout({ commit }) {
    commit('setUserInfo', null)
    localStorage.removeItem('token')
  }
}

const getters = {
  userInfo: state => state.userInfo,
  isAdmin: state => state.userInfo && state.userInfo.role === 'admin'
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 