<template>
  <div id="app" class="app-wrapper">
    <NavMenu v-if="showNavMenu" />
    <main class="app-main">
      <div class="app-container">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script>
import NavMenu from './components/NavMenu.vue'

export default {
  components: { NavMenu },
  computed: {
    showNavMenu() {
      // Здесь можно добавить логику, если нужно скрывать меню на некоторых страницах
      // Например: return this.$route.name !== 'login'
      return true // Всегда показывать меню
    }
  }
}
</script>

<style>
:root {
  --primary-color: #3498db;
  --primary-hover: #2980b9;
  --success-color: #2ecc71;
  --success-hover: #27ae60;
  --danger-color: #e74c3c;
  --danger-hover: #c0392b;
  --text-color: #2c3e50;
  --text-light: #7f8c8d;
  --background: #f8f9fa;
  --card-bg: #ffffff;
  --border-color: #dfe6e9;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
}

body {
  font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: var(--background);
  color: var(--text-color);
  line-height: 1.6;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.authenticated-layout {
  display: flex;
  min-height: 100vh;
}

.app-main {
  flex: 1;
  padding-top: 64px; /* Высота навбара */
}

.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

.guest-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  padding: 20px;
}

/* Общие компоненты */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 500;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: var(--primary-color);
  color: white;
}

.button:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.button.button-success {
  background-color: var(--success-color);
}

.button.button-success:hover {
  background-color: var(--success-hover);
}

.button.button-danger {
  background-color: var(--danger-color);
}

.button.button-danger:hover {
  background-color: var(--danger-hover);
}

.card {
  background: var(--card-bg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 24px;
  margin-bottom: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  color: var(--text-color);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  transition: all 0.2s ease;
  background-color: #f8f9fa;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  background-color: #fff;
}

@media (max-width: 768px) {
  .app-container {
    padding: 16px;
  }
  
  .card {
    padding: 16px;
  }
}
</style>