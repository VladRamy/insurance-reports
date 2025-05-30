<template>
  <div>
    <h1>Dashboard</h1>
    
    <div v-if="loading" class="loading-indicator">
      Loading dashboard data...
    </div>
    
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="fetchDashboardData">Retry</button>
    </div>
    
    <div v-else>
      <div class="metrics-grid">
        <div class="metric-card">
          <h3>Total Premium</h3>
          <p>{{ formatCurrency(dashboardData.total_premium) }}</p>
        </div>
        
        <div class="metric-card">
          <h3>Total Claims</h3>
          <p>{{ formatCurrency(dashboardData.total_claims) }}</p>
        </div>
        
        <div class="metric-card">
          <h3>Open Claims</h3>
          <p>{{ formatCurrency(dashboardData.open_claims) }}</p>
        </div>
        
        <div class="metric-card">
          <h3>Loss Ratio</h3>
          <p>{{ dashboardData.loss_ratio !== null && dashboardData.loss_ratio !== undefined ? dashboardData.loss_ratio.toFixed(2) : '0.00' }}%</p>
        </div>
      </div>
      
      <div class="card">
        <h2>Top Products</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Premium</th>
              <th>Claims</th>
              <th>Loss Ratio</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in dashboardData.top_products" :key="product.product__name">
              <td>{{ product.product__name }}</td>
              <td>{{ formatCurrency(product.premium) }}</td>
              <td>{{ formatCurrency(product.claims) }}</td>
              <td>{{ product.premium > 0 ? ((product.claims / product.claims) * 100).toFixed(2) + '%' : 'N/A' }}</td>
            </tr>
          </tbody>
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
    // Добавьте этот метод в секцию methods
    formatCurrency(value) {
      if (value === null || value === undefined || isNaN(value)) {
        return '$0.00';
      }
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    },
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await this.$axios.get('dashboard/');
        this.dashboardData = response.data;
      } catch (error) {
        console.error('Dashboard error:', error);
        if (error.response && error.response.status === 401) {
          this.error = 'Session expired. Please login again.';
          this.$router.push('/login');
        } else {
          this.error = 'Failed to load dashboard data';
        }
      } finally {
        this.loading = false;
      }
    }
  },
  created(){
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