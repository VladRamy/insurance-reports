<template>
  <div class="table-responsive">
    <table class="data-table">
      <thead>
        <tr>
          <th v-for="header in headers" :key="header.key">{{ header.title }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in formattedData" :key="index">
          <td v-for="header in headers" :key="header.key" :class="getCellClass(item, header)">
            {{ formatCell(item[header.key], header) }}
          </td>
        </tr>
        <tr v-if="formattedData.length === 0">
          <td :colspan="headers.length" class="no-data">No data available</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: {
    data: Array,
    reportType: String
  },
  computed: {
    headers() {
      const reportHeaders = {
        cashflow: [
          { key: 'date', title: 'Date', type: 'date' },
          { key: 'product_name', title: 'Product', type: 'string' },
          { key: 'expected_amount', title: 'Expected', type: 'currency' },
          { key: 'actual_amount', title: 'Actual', type: 'currency' },
          { key: 'difference', title: 'Difference', type: 'currency' },
          { key: 'accuracy', title: 'Accuracy', type: 'percentage' }
        ],
        reserves: [
          { key: 'calculation_date', title: 'Calculation Date', type: 'date' },
          { key: 'product_name', title: 'Product', type: 'string' },
          { key: 'total_reserves', title: 'Total Reserves', type: 'currency' },
          { key: 'required_reserves', title: 'Required', type: 'currency' },
          { key: 'available_reserves', title: 'Available', type: 'currency' },
          { key: 'sufficiency_ratio', title: 'Sufficiency', type: 'percentage' }
        ],
        loss_ratio: [
          { key: 'product_name', title: 'Product', type: 'string' },
          { key: 'year', title: 'Year', type: 'number' },
          { key: 'month', title: 'Month', type: 'number' },
          { key: 'earned_premium', title: 'Earned Premium', type: 'currency' },
          { key: 'incurred_losses', title: 'Incurred Losses', type: 'currency' },
          { key: 'loss_ratio', title: 'Loss Ratio', type: 'percentage' }
        ],
        forecast: [
          { key: 'date', title: 'Date', type: 'date' },
          { key: 'type', title: 'Type', type: 'string' },
          { key: 'amount', title: 'Amount', type: 'currency' },
          { key: 'forecast_accuracy', title: 'Accuracy', type: 'percentage', optional: true }
        ],
        claims: [
          { key: 'claim_number', title: 'Claim #', type: 'string' },
          { key: 'policy_number', title: 'Policy #', type: 'string' },
          { key: 'event_date', title: 'Event Date', type: 'date' },
          { key: 'status', title: 'Status', type: 'string' },
          { key: 'estimated_amount', title: 'Estimated', type: 'currency' },
          { key: 'paid_amount', title: 'Paid', type: 'currency' },
          { key: 'reserve', title: 'Reserve', type: 'currency' }
        ],
        policies: [
          { key: 'policy_number', title: 'Policy #', type: 'string' },
          { key: 'product_name', title: 'Product', type: 'string' },
          { key: 'start_date', title: 'Start Date', type: 'date' },
          { key: 'end_date', title: 'End Date', type: 'date' },
          { key: 'premium', title: 'Premium', type: 'currency' },
          { key: 'status', title: 'Status', type: 'string' }
        ]
      };
      
      return reportHeaders[this.reportType] || [];
    },
    formattedData() {
      if (!this.data || this.data.length === 0) return [];
      
      return this.data.map(item => {
        const formatted = { ...item };
        
        // Добавляем вычисляемые поля для каждого типа отчета
        switch (this.reportType) {
          case 'cashflow':
            formatted.difference = (item.actual_amount || 0) - (item.expected_amount || 0);
            formatted.accuracy = item.expected_amount 
              ? ((item.actual_amount || 0) / item.expected_amount * 100) 
              : 0;
            break;
            
          case 'reserves':
            formatted.sufficiency_ratio = item.required_reserves 
              ? (item.available_reserves / item.required_reserves * 100) 
              : 0;
            break;
            
          case 'loss_ratio':
            formatted.loss_ratio = item.earned_premium 
              ? (item.incurred_losses / item.earned_premium * 100) 
              : 0;
            break;
            
          case 'forecast':
            if (!formatted.type) {
              formatted.type = formatted.actual_amount !== undefined ? 'actual' : 'forecast';
            }
            break;
        }
        
        return formatted;
      });
    }
  },
  methods: {
    formatCell(value, header) {
      if (value === null || value === undefined || value === 'N/A') {
        return header.optional ? '-' : 'N/A';
      }
      
      switch (header.type) {
        case 'currency':
          return this.formatCurrency(value);
        case 'date':
          return this.formatDate(value);
        case 'percentage':
          return value === 0 ? '0%' : `${parseFloat(value).toFixed(2)}%`;
        case 'number':
          return this.formatNumber(value);
        default:
          return value;
      }
    },
    getCellClass(item, header) {
      const classes = [];
      
      if (header.type === 'currency' || header.type === 'percentage') {
        if (header.key === 'difference') {
          classes.push(item.difference > 0 ? 'positive' : 'negative');
        } else if (header.key === 'loss_ratio') {
          classes.push(item.loss_ratio > 100 ? 'negative' : 'positive');
        } else if (header.key === 'sufficiency_ratio') {
          classes.push(item.sufficiency_ratio < 100 ? 'negative' : 'positive');
        }
      }
      
      return classes.join(' ');
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value || 0);
    },
    formatDate(value) {
      if (!value) return 'N/A';
      const date = new Date(value);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    formatPercentage(value) {
      return `${parseFloat(value).toFixed(2)}%`;
    },
    formatNumber(value) {
      return new Intl.NumberFormat('en-US').format(value);
    }
  }
}
</script>

<style scoped>
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.data-table th, .data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.data-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #2c3e50;
  text-transform: uppercase;
  font-size: 0.8em;
  letter-spacing: 0.5px;
}

.data-table tr:hover {
  background-color: #f8f9fa;
}

.positive {
  color: #4CAF50;
  font-weight: 500;
}

.negative {
  color: #F44336;
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #757575;
  font-style: italic;
}

.table-responsive {
  overflow-x: auto;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>