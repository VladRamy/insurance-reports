<template>
  <div>
    <h1>Dashboard</h1>
    
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
        <p>{{ dashboardData.loss_ratio.toFixed(2) }}%</p>
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
            <td>{{ product.premium > 0 ? ((product.claims / product.premium) * 100).toFixed(2) + '%' : 'N/A' }}</td>
          </tr>
        </tbody>
      </table>
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
      }
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
      try {
        const response = await this.axios.get('dashboard/')
        this.dashboardData = response.data
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }
  },
  created() {
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