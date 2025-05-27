<template>
  <div class="report-card">
    <div class="report-header">
      <div class="header-content">
        <h2 class="report-title">{{ reportTitle }}</h2>
        <p class="report-subtitle" v-if="reportSubtitle">{{ reportSubtitle }}</p>
      </div>
      
      <div class="export-actions">
        <button @click="$emit('export', 'excel')" class="export-btn excel-btn">
          <svg class="export-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m-1.7 16.6l-1.4-1.4 1.6-1.6H9v-2h3.5l-1.6-1.6 1.4-1.4 3.5 3.5-3.5 3.5M13 9V3.5L18.5 9H13z"/>
          </svg>
          Excel
        </button>
        <button @click="$emit('export', 'pdf')" class="export-btn pdf-btn">
          <svg class="export-icon" viewBox="0 0 24 24">
            <path fill="currentColor" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6m-1.1 17H9v-1.8h3.9v1.8m0-3.6H9v-1.8h3.9v1.8M13 9V3.5L18.5 9H13z"/>
          </svg>
          PDF
        </button>
      </div>
    </div>
    
    <div class="report-body">
      <div v-if="reportType === 'cashflow'" class="report-content">
        <CashFlowChart :data="data" />
        <CashFlowTable :data="data" />
      </div>
      
      <div v-if="reportType === 'loss_ratio'" class="report-content">
        <!-- <LossRatioChart :data="data" />
        <LossRatioTable :data="data" /> -->
      </div>
    </div>
  </div>
  </template>
  
  <script>
  import CashFlowChart from './charts/CashFlowChart.vue'
  import CashFlowTable from './tables/CashFlowTable.vue'
//   import LossRatioChart from './charts/LossRatioChart.vue'
//   import LossRatioTable from './tables/LossRatioTable.vue'
  
  export default {
    components: {
      CashFlowChart,
      CashFlowTable,
    },
    props: {
      data: Array,
      reportType: String
    },
    computed: {
      reportTitle() {
        const titles = {
          cashflow: 'Cash Flow Report',
          reserves: 'Reserves Report',
          loss_ratio: 'Loss Ratio Report',
          forecast: 'Payment Forecast'
        }
        return titles[this.reportType] || 'Report'
      }
    }
  }
  </script>
  
  <style scoped>
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