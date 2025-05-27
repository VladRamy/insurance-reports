<template>
    <div class="chart-container">
      <canvas ref="chart"></canvas>
    </div>
  </template>
  
  <script>
  import { Bar, mixins } from 'vue-chartjs'
  const { reactiveProp } = mixins
  
  export default {
    extends: Bar,
    mixins: [reactiveProp],
    props: ['chartData'],
    mounted() {
      this.renderChart({
        labels: this.chartData.map(item => item.date),
        datasets: [
          {
            label: 'Expected',
            backgroundColor: '#42A5F5',
            data: this.chartData.map(item => item.expected_sum)
          },
          {
            label: 'Actual',
            backgroundColor: '#FFA726',
            data: this.chartData.map(item => item.actual_sum)
          }
        ]
      }, {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return '$' + value.toLocaleString()
              }
            }
          }]
        }
      })
    }
  }
  </script>
  
  <style scoped>
  .chart-container {
    position: relative;
    height: 400px;
    margin-bottom: 20px;
  }
  </style>