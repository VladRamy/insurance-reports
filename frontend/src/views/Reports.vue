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
        this.selectedReportType = params.type
        this.loading = true
        this.exportParams = params
        
        try {
          const response = await this.$axios.get('reports/', { params })
          this.reportData = response.data
        } catch (error) {
          console.error('Error generating report:', error)
          alert('Error generating report')
        } finally {
          this.loading = false
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