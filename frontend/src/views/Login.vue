<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Login</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            autocomplete="username"
            required
          >
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            autocomplete="current-password"
            required
          >
        </div>
        <button 
          type="submit" 
          class="button" 
          :disabled="loading"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <p v-if="error" class="error-message">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    }
  },
  methods: {
  async login() {
    try {
      const response = await this.$axios.post('auth/', {  // или 'api/api/auth/' если нужно
        username: this.username,
        password: this.password
      });
      
      // Сохраняем полученный токен
      const token = response.data.token;
      localStorage.setItem('token', token);
      
      // Устанавливаем токен для всех последующих запросов
      this.$axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      
      // Перенаправляем на защищенную страницу
      this.$router.push('/dashboard');
    } catch (error) {
      console.error('Login error:', error.response);
      this.error = 'Invalid username or password';
    }
  }
}
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f8f9fa;
}

.login-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.login-card h2 {
  margin-top: 0;
  text-align: center;
  color: #333;
}

.error-message {
  color: red;
  margin-top: 15px;
  text-align: center;
}
</style>