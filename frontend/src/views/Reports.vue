<template>
    <div>
      <h1>Reports</h1>
      
      <ReportGenerator @generate="generateReport" />
      
      <div v-if="loading" class="loading">Loading...</div>
      
      <ReportViewer 
        v-if="reportData && !loading"
        :data="reportData"
        :reportType="selectedReportType"
        @export="exportReport"
      />
    </div>
  </template>
  
  <script>
  import ReportGenerator from '@/components/ReportGenerator'
  import ReportViewer from '@/components/ReportViewer'
  
  export default {
    components: { ReportGenerator, ReportViewer },
    data() {
      return {
        selectedReportType: null,
        reportData: null,
        loading: false,
        exportParams: null
      }
    },
    methods: {
      async generateReport(params) {
        try {
          this.loading = true;
          this.exportParams = params; // Сохраняем параметры для экспорта
          console.log('Sending forecast params:', {
            type: 'forecast',
            start_date: params.start_date,
            end_date: params.end_date,
            payment_type: params.payment_type, // Важно!
            product_id: params.product_id
          });
          if (params.type === 'forecast') {
            params.payment_type = params.payment_type || 'premium'; // Значение по умолчанию
          }
          
          
          const response = await this.$axios.get('reports/', { params })
            .catch(error => {
              console.error('API Error:', error);
              throw new Error('Failed to fetch report data');
            });
            console.log('Forecast response:', response.data);
          if (!response || !response.data) {
            throw new Error('Empty response from server');
          }
          
          this.reportData = response.data.data || []; // Используем response.data.data
          this.selectedReportType = params.type;
          
        } catch (error) {
          console.error('Report generation error:', {
            message: error.message,
            response: error.response.data,
            stack: error.stack
          });
          
          const message = error.response.data.error || 
                        error.response.data.detail || 
                        error.message || 
                        'Report generation failed';
          
          this.$toast.error(message);
          this.reportData = []; // Сбрасываем данные при ошибке
        } finally {
          this.loading = false;
        }
      },
      async exportReport(format) {
        if (!this.exportParams) return
        
        try {
          const params = { ...this.exportParams, format }
          const response = await this.$axios.get('reports/export/', { 
            params,
            responseType: 'blob'
          })
          
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          
          const extension = format === 'pdf' ? 'pdf' : 'xlsx'
          link.setAttribute('download', `${this.selectedReportType}_report.${extension}`)
          document.body.appendChild(link)
          link.click()
          link.remove()
        } catch (error) {
          console.error('Error exporting report:', error)
          alert('Error exporting report')
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .loading {
    padding: 20px;
    text-align: center;
    font-style: italic;
    color: #666;
  }
  </style>