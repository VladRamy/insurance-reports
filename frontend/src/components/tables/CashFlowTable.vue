<template>
    <table class="data-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Product</th>
          <th>Expected</th>
          <th>Actual</th>
          <th>Difference</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data" :key="item.date + item.product__name">
          <td>{{ item.date }}</td>
          <td>{{ item.product__name }}</td>
          <td>{{ formatCurrency(item.expected_sum) }}</td>
          <td>{{ formatCurrency(item.actual_sum) }}</td>
          <td :class="getDifferenceClass(item)">
            {{ formatCurrency(item.actual_sum - item.expected_sum) }}
          </td>
        </tr>
      </tbody>
    </table>
  </template>
  
  <script>
  export default {
    props: ['data'],
    methods: {
      formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(value)
      },
      getDifferenceClass(item) {
        const diff = item.actual_sum - item.expected_sum
        return {
          'positive': diff > 0,
          'negative': diff < 0
        }
      }
    }
  }
  </script>
  
  <style scoped>
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
  
  .positive {
    color: #4CAF50;
  }
  
  .negative {
    color: #F44336;
  }
  </style>