<template>
  <nav class="app-navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <svg class="brand-icon" viewBox="0 0 24 24">
          <path fill="currentColor" d="M12,3L2,12H5V20H19V12H22L12,3M12,7.7C14.1,7.7 15.8,9.4 15.8,11.5C15.8,13.6 14.1,15.3 12,15.3C9.9,15.3 8.2,13.6 8.2,11.5C8.2,9.4 9.9,7.7 12,7.7M7,17V18H17V17C17,14.3 14.7,12 12,12C9.3,12 7,14.3 7,17Z" />
        </svg>
        <span>Insurance Reports</span>
      </div>
      
      <div class="navbar-links">
        <router-link to="/dashboard" class="nav-link">
          <svg class="nav-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z" />
          </svg>
          <span>Dashboard</span>
        </router-link>
        
        <router-link to="/reports" class="nav-link">
          <svg class="nav-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2M7,20H9V14H7V20M11,20H13V12H11V20M15,20H17V16H15V20Z" />
          </svg>
          <span>Reports</span>
        </router-link>
        
        <button @click="logout" class="logout-btn">
          <svg class="logout-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M16,17V14H9V10H16V7L21,12L16,17M14,2A2,2 0 0,1 16,4V6H14V4H5V20H14V18H16V20A2,2 0 0,1 14,22H5A2,2 0 0,1 3,20V4A2,2 0 0,1 5,2H14Z" />
          </svg>
          <span>Logout</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  methods: {
    logout() {
      localStorage.removeItem('token')
      this.$store.commit('SET_AUTH', false)
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.app-navbar {
  background: linear-gradient(135deg, #2c3e50 0%, #1a2530 100%);
  color: white;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 100;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.4rem;
  font-weight: 600;
  color: white;
}

.brand-icon {
  width: 28px;
  height: 28px;
  color: #3498db;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 6px;
  color: #ecf0f1;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.nav-link.router-link-exact-active {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
}

.nav-link.router-link-exact-active .nav-icon {
  color: #3498db;
}

.nav-icon {
  width: 20px;
  height: 20px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 6px;
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  margin-left: 8px;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 0.1);
  transform: translateY(-1px);
}

.logout-icon {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 16px;
  }
  
  .nav-link span, .logout-btn span {
    display: none;
  }
  
  .nav-link, .logout-btn {
    padding: 10px;
  }
  
  .brand-icon, .nav-icon, .logout-icon {
    width: 24px;
    height: 24px;
  }
}
</style>