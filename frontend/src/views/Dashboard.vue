<template>
  <div>
    <h1>Dashboard</h1>
    
    <div v-if="loading" class="loading">
      Loading data...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
      <button @click="fetchDashboardData">Retry</button>
    </div>
    
    <div v-else class="dashboard-content">
      <!-- Ваши существующие компоненты dashboard -->
      <div class="metrics-grid">
        <div class="metric-card">
          <h3>Total Premium</h3>
          <p>{{ formatCurrency(dashboardData.total_premium) }}</p>
        </div>
        
        <!-- Остальные метрики -->
      </div>
      
      <div class="card">
        <h2>Top Products</h2>
        <table class="data-table">
          <!-- Таблица продуктов -->
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      dashboardData: {
        total_premium: 0,
        total_claims: 0,
        open_claims: 0,
        loss_ratio: 0,
        top_products: []
      },
      loading: false,
      error: null
    }
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    },
    async fetchDashboardData() {
      this.loading = true
      this.error = null
      
      try {
        const response = await this.$axios.get('dashboard/')
        this.dashboardData = response.data
      } catch (error) {
        console.error('Dashboard error:', error)
        if (error.response?.status === 401) {
          this.error = 'Session expired. Please login again.'
          this.$router.push('/login')
        } else {
          this.error = 'Failed to load dashboard data'
        }
      } finally {
        this.loading = false
      }
    }
  },
  created() {
    // Устанавливаем токен из localStorage
    const token = localStorage.getItem('token')
    if (token) {
      this.$axios.defaults.headers.common['Authorization'] = `Token ${token}`
    }
    
    this.fetchDashboardData()
  }
}
</script>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 20px;
  text-align: center;
}

.metric-card h3 {
  margin-top: 0;
  color: #666;
  font-size: 1em;
}

.metric-card p {
  font-size: 1.5em;
  font-weight: bold;
  margin-bottom: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.data-table th {
  background-color: #f8f8f8;
  font-weight: bold;
}

.data-table tr:hover {
  background-color: #f5f5f5;
}
</style>