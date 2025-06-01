<template>
  <div class="report-card">
    <div class="report-header">
      <div class="header-content">
        <h2 class="report-title">{{ reportTitle }}</h2>
        <p class="report-subtitle" v-if="reportSubtitle">{{ reportSubtitle }}</p>
      </div>
      
      <div class="export-actions">
        <button @click="handleExport('excel')" class="export-btn excel-btn">
          <svg class="export-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m-1.7 16.6l-1.4-1.4 1.6-1.6H9v-2h3.5l-1.6-1.6 1.4-1.4 3.5 3.5-3.5 3.5M13 9V3.5L18.5 9H13z"/>
          </svg>
          Excel
        </button>
        <button @click="handleExport('pdf')" class="export-btn pdf-btn">
          <svg class="export-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m-1.1 17H9v-1.8h3.9v1.8m0-3.6H9v-1.8h3.9v1.8M13 9V3.5L18.5 9H13z"/>
          </svg>
          PDF
        </button>
      </div>
    </div>
    
    <div class="report-body">
      <div v-if="hasData" class="report-content">
        <DynamicTable 
          :data="normalizedData" 
          :report-type="reportType"
          :products="products"
        />
        
        <div v-if="reportType === 'cashflow'" class="chart-container">
          <CashFlowChart :chart-data="normalizedData" />
        </div>
      </div>
      
      <div v-else class="no-data-message">
        No data available for this report
      </div>
    </div>
  </div>
</template>

<script>
import DynamicTable from './tables/DynamicTable.vue'
import CashFlowChart from './charts/CashFlowChart.vue'

export default {
  name: 'ReportViewer',
  components: { DynamicTable, CashFlowChart },
  props: {
    data: [Array, Object],
    reportType: {
      type: String,
      required: true,
      validator: value => ['cashflow', 'reserves', 'loss_ratio', 'forecast'].includes(value)
    },
    products: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    hasData() {
      if (!this.data) return false
      
      // Для forecast проверяем оба массива
      if (this.reportType === 'forecast') {
        return (
          (this.data.historical && this.data.historical.length > 0) ||
          (this.data.forecast && this.data.forecast.length > 0)
        )
      }
      
      // Для остальных типов проверяем сам массив данных
      return Array.isArray(this.data) ? this.data.length > 0 : false
    },
    normalizedData() {
      if (!this.data) return []
      
      switch (this.reportType) {
        case 'cashflow':
          return this.normalizeCashflowData()
        case 'reserves':
          return this.normalizeReservesData()
        case 'loss_ratio':
          return this.normalizeLossRatioData()
        case 'forecast':
          return this.normalizeForecastData()
        default:
          return Array.isArray(this.data) ? this.data : [this.data]
      }
    },
    reportTitle() {
      const titles = {
        cashflow: 'Cash Flow Report',
        reserves: 'Reserves Report',
        loss_ratio: 'Loss Ratio Report',
        forecast: 'Payment Forecast'
      }
      return titles[this.reportType] || 'Report'
    },
    reportSubtitle() {
      return `Report for ${this.reportType}`
    }
  },
  methods: {
    handleExport(format) {
      this.$emit('export', format)
    },
    normalizeCashflowData() {
      return (Array.isArray(this.data) ? this.data : []).map(item => ({
        date: item.date,
        product_name: item.product__name || item.product_name || 'N/A',
        expected_amount: item.expected_sum || item.expected_amount || 0,
        actual_amount: item.actual_sum || item.actual_amount || 0,
        difference: (item.actual_sum || item.actual_amount || 0) - 
                  (item.expected_sum || item.expected_amount || 0),
      }))
    },
    normalizeReservesData() {
      return (Array.isArray(this.data) ? this.data : []).map(item => {
        // Ищем продукт в переданном списке продуктов
        const product = this.products.find(p => 
          p.id === item.product_id || 
          p.id === item.product.id
        ) || {}
        
        return {
          calculation_date: item.calculation_date,
          product_name: product.product_name || item.product_name || 'N/A',
          total_reserves: item.total_reserves || 0,
          required_reserves: item.required_reserves || 0,
          available_reserves: item.available_reserves || 0,
          sufficiency_ratio: item.required_reserves ?
            (item.available_reserves / item.required_reserves * 100) : 0
        }
      })
    },
    normalizeLossRatioData() {
      return (Array.isArray(this.data) ? this.data : []).map(item => ({
        product_name: item.product__name || item.product_name || 'N/A',
        year: item.year || new Date(item.date).getFullYear(),
        month: item.month || new Date(item.date).getMonth() + 1,
        earned_premium: item.earned_premium || 0,
        incurred_losses: item.incurred_losses || 0,
        loss_ratio: item.earned_premium ?
          (item.incurred_losses / item.earned_premium * 100) : 0
      }))
    },
    normalizeForecastData() {
      // Если данные пришли как объект с historical/forecast
      if (typeof this.data === 'object' && !Array.isArray(this.data)) {
        return [
          ...(this.data.historical || []).map(item => ({
            date: item.date,
            amount: item.actual_amount || item.amount || 0,
            type: 'historical'
          })),
          ...(this.data.forecast || []).map(item => ({
            date: item.date,
            amount: item.amount || item.forecast_amount || 0,
            type: 'forecast'
          }))
        ]
      }
      
      // Если данные пришли как плоский массив
      return Array.isArray(this.data) ? this.data : []
    }
  }
}
</script>

<style scoped>
/* Стили остаются без изменений */
.report-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-content {
  flex: 1;
}

.report-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.report-subtitle {
  margin: 4px 0 0;
  font-size: 0.9rem;
  color: #7f8c8d;
  font-weight: 400;
}

.export-actions {
  display: flex;
  gap: 12px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  color: white;
}

.export-icon {
  width: 18px;
  height: 18px;
}

.excel-btn {
  background: #1d6f42;
}

.excel-btn:hover {
  background: #165a34;
  transform: translateY(-1px);
}

.pdf-btn {
  background: #d32f2f;
}

.pdf-btn:hover {
  background: #b71c1c;
  transform: translateY(-1px);
}

.report-body {
  padding: 0 24px 24px;
}

.report-content {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.no-data-message {
  padding: 40px;
  text-align: center;
  color: #757575;
  font-style: italic;
  font-size: 1.1rem;
}

.chart-container {
  position: relative;
  height: 400px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .report-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .export-actions {
    width: 100%;
  }
  
  .export-btn {
    flex: 1;
    justify-content: center;
    padding: 10px;
  }
}
</style>