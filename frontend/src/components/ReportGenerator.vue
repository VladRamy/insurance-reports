<template>
  <div class="report-generator">
    <div class="generator-header">
      <h2 class="generator-title">Generate Report</h2>
      <p class="generator-subtitle">Select parameters to generate a custom report</p>
    </div>
    
    <div class="generator-form">
      <div class="form-group">
        <label for="report-type" class="form-label">Report Type</label>
        <div class="form-select-wrapper">
          <select id="report-type" v-model="reportType" class="form-select">
            <option value="cashflow">Cash Flow</option>
            <option value="reserves">Reserves</option>
            <option value="loss_ratio">Loss Ratio</option>
            <option value="forecast">Payment Forecast</option>
          </select>
          <svg class="select-arrow" viewBox="0 0 24 24">
            <path fill="currentColor" d="M7,10L12,15L17,10H7Z" />
          </svg>
        </div>
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Start Date</label>
          <div class="form-input-wrapper">
            <input type="date" v-model="startDate" class="form-input">
            <svg class="date-icon" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z" />
            </svg>
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">End Date</label>
          <div class="form-input-wrapper">
            <input type="date" v-model="endDate" class="form-input">
            <svg class="date-icon" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19,19H5V8H19M16,1V3H8V1H6V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H18V1M17,12H12V17H17V12Z" />
            </svg>
          </div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="product" class="form-label">Product (optional)</label>
        <div class="form-select-wrapper">
          <select id="product" v-model="selectedProduct" class="form-select">
            <option value="">All Products</option>
            <option v-for="product in products" :value="product.id" :key="product.id">
              {{ product.name }}
            </option>
          </select>
          <svg class="select-arrow" viewBox="0 0 24 24">
            <path fill="currentColor" d="M7,10L12,15L17,10H7Z" />
          </svg>
        </div>
      </div>
      
      <div v-if="reportType === 'forecast'" class="form-group">
        <label for="payment-type" class="form-label">Payment Type</label>
        <div class="form-select-wrapper">
          <select id="payment-type" v-model="paymentType" class="form-select">
            <option value="premium">Premium</option>
            <option value="claim">Claim</option>
          </select>
          <svg class="select-arrow" viewBox="0 0 24 24">
            <path fill="currentColor" d="M7,10L12,15L17,10H7Z" />
          </svg>
        </div>
      </div>
      
      <button class="generate-btn" @click="handleGenerate">
        <svg class="generate-icon" viewBox="0 0 24 24">
          <path fill="currentColor" d="M14,12L10,8V11H2V13H10V16M20,18V6C20,4.89 19.1,4 18,4H6A2,2 0 0,0 4,6V9H6V6H18V18H6V15H4V18A2,2 0 0,0 6,20H18A2,2 0 0,0 20,18Z" />
        </svg>
        Generate Report
      </button>
    </div>
  </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        reportType: 'cashflow',
        startDate: this.getDefaultStartDate(),
        endDate: this.getDefaultEndDate(),
        selectedProduct: '',
        paymentType: 'premium',
        products: []
      }
    },
    methods: {
      getDefaultStartDate() {
        const date = new Date()
        date.setMonth(date.getMonth() - 1)
        return date.toISOString().split('T')[0]
      },
      getDefaultEndDate() {
        return new Date().toISOString().split('T')[0]
      },
      async fetchProducts() {
        try {
          const response = await this.$axios.get('products/')
          this.products = response.data
        } catch (error) {
          console.error('Error fetching products:', error)
        }
      },
      handleGenerate() {
        const params = {
          type: this.reportType,
          start_date: this.startDate,
          end_date: this.endDate
        }
        
        if (this.selectedProduct) {
          params.product_id = this.selectedProduct
        }
        
        if (this.reportType === 'forecast') {
          params.payment_type = this.paymentType
        }
        
        this.$emit('generate', params)
      }
    },
    created() {
      this.fetchProducts()
    }
  }
  </script>
  
  <style scoped>
  .report-generator {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    max-width: 600px;
    margin: 0 auto;
  }
  
  .report-generator:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  }
  
  .generator-header {
    padding: 24px;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  }
  
  .generator-title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }
  
  .generator-subtitle {
    margin: 4px 0 0;
    font-size: 0.9rem;
    color: #7f8c8d;
    font-weight: 400;
  }
  
  .generator-form {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .form-row {
    display: flex;
    gap: 16px;
  }
  
  .form-row .form-group {
    flex: 1;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .form-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #34495e;
  }
  
  .form-select-wrapper, .form-input-wrapper {
    position: relative;
  }
  
  .form-select, .form-input {
    width: 100%;
    padding: 10px 16px;
    padding-right: 40px;
    border: 1px solid #dfe6e9;
    border-radius: 6px;
    font-size: 0.875rem;
    transition: all 0.2s ease;
    background-color: #f8f9fa;
  }
  
  .form-select {
    appearance: none;
  }
  
  .form-input {
    padding-right: 16px;
  }
  
  .form-select:focus, .form-input:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    background-color: #fff;
  }
  
  .select-arrow {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 16px;
    pointer-events: none;
    color: #7f8c8d;
  }
  
  .date-icon {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 18px;
    pointer-events: none;
    color: #7f8c8d;
  }
  
  .generate-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 24px;
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 8px;
  }
  
  .generate-btn:hover {
    background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(41, 128, 185, 0.3);
  }
  
  .generate-icon {
    width: 18px;
    height: 18px;
  }
  
  @media (max-width: 600px) {
    .form-row {
      flex-direction: column;
      gap: 20px;
    }
    
    .report-generator {
      border-radius: 0;
      box-shadow: none;
    }
  }
  </style>