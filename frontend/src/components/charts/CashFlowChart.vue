<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

export default {
  name: 'CashFlowChart',
  props: {
    chartData: {
      type: Array,
      required: true
    }
  },
  setup(props) {
    const chartCanvas = ref(null)
    let chartInstance = null

    const renderChart = () => {
      if (!props.chartData || props.chartData.length === 0) return
      
      Chart.register(...registerables)
      
      if (chartInstance) {
        chartInstance.destroy()
      }

      const ctx = chartCanvas.value.getContext('2d')
      
      const labels = props.chartData.map(item => item.date)
      const expectedData = props.chartData.map(item => item.expected_amount || 0)
      const actualData = props.chartData.map(item => item.actual_amount || 0)

      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: 'Expected',
              backgroundColor: '#42A5F5',
              data: expectedData
            },
            {
              label: 'Actual',
              backgroundColor: '#FFA726',
              data: actualData
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: function(value) {
                  return '$' + value.toLocaleString()
                }
              }
            }
          }
        }
      })
    }

    onMounted(renderChart)
    watch(() => props.chartData, renderChart, { deep: true })

    return {
      chartCanvas
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
}
</style>