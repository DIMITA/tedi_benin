<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      <h1>TEDI Multi-Sector Analytics Dashboard</h1>
      <p class="subtitle">Real-time territorial and economic data index across all sectors</p>
    </div>

    <!-- Sector Selector & Filters -->
    <div class="filters-panel">
      <div class="sector-selector">
        <label>Select Sector:</label>
        <div class="sector-buttons">
          <button
            v-for="s in sectors"
            :key="s"
            :class="['sector-btn', { active: activeSector === s }]"
            @click="activeSector = s"
          >
            {{ s.toUpperCase() }}
          </button>
        </div>
      </div>

      <div class="filter-controls">
        <div class="filter-group">
          <label>Year Range:</label>
          <input v-model.number="yearFrom" type="number" min="2010" :max="currentYear" placeholder="From">
          <span>to</span>
          <input v-model.number="yearTo" type="number" min="2010" :max="currentYear" placeholder="To">
        </div>

        <div class="filter-group">
          <label>Group By:</label>
          <select v-model="groupBy">
            <option value="none">Overall (No grouping)</option>
            <option value="commune">Commune</option>
            <option value="category">Category/Sector</option>
            <option value="year">Year (Trend)</option>
          </select>
        </div>

        <button class="btn-refresh" @click="loadData">
          ↻ Refresh Data
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading {{ activeSector }} data...</p>
    </div>

    <!-- KPI Cards -->
    <div v-else class="kpi-cards">
      <div v-for="(kpi, idx) in kpiCards" :key="idx" class="kpi-card">
        <h3>{{ kpi.title }}</h3>
        <div class="kpi-value">{{ kpi.value }}</div>
        <div class="kpi-unit">{{ kpi.unit }}</div>
        <div v-if="kpi.change" :class="['kpi-change', kpi.change > 0 ? 'positive' : 'negative']">
          {{ kpi.change > 0 ? '↑' : '↓' }} {{ Math.abs(kpi.change).toFixed(1) }}%
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div v-if="!loading && data" class="charts-grid">
      <!-- 1. Bar Chart -->
      <div class="chart-card">
        <h3>{{ chartTitles.bar }}</h3>
        <canvas ref="barChartRef"></canvas>
      </div>

      <!-- 2. Line Chart (Trends) -->
      <div class="chart-card">
        <h3>{{ chartTitles.line }}</h3>
        <canvas ref="lineChartRef"></canvas>
      </div>

      <!-- 3. Donut/Pie Chart -->
      <div class="chart-card">
        <h3>{{ chartTitles.donut }}</h3>
        <canvas ref="donutChartRef"></canvas>
      </div>

      <!-- 4. Area Chart -->
      <div class="chart-card">
        <h3>{{ chartTitles.area }}</h3>
        <canvas ref="areaChartRef"></canvas>
      </div>

      <!-- 5. Stacked Bar Chart -->
      <div class="chart-card">
        <h3>{{ chartTitles.stacked }}</h3>
        <canvas ref="stackedChartRef"></canvas>
      </div>

      <!-- 6. Bubble/Scatter Chart -->
      <div class="chart-card">
        <h3>{{ chartTitles.bubble }}</h3>
        <canvas ref="bubbleChartRef"></canvas>
      </div>
    </div>

    <!-- Data Table -->
    <div v-if="!loading && tableData.length > 0" class="data-table-section">
      <h2>Detailed Data</h2>
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="col in tableColumns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in tableData.slice(0, 20)" :key="idx">
              <td v-for="col in tableColumns" :key="col">{{ formatTableCell(row[col], col) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import api from '../services/api'
import { formatPrice } from '@/utils/formatters'

Chart.register(...registerables)

export default {
  name: 'MultiSectorDashboard',
  data() {
    return {
      sectors: ['agriculture', 'realestate', 'employment', 'business'],
      activeSector: 'agriculture',
      yearFrom: 2010,
      yearTo: new Date().getFullYear(),
      groupBy: 'year',
      data: null,
      loading: false,
      activeChartKey: 0,
      
      // Charts
      charts: {
        bar: null,
        line: null,
        donut: null,
        area: null,
        stacked: null,
        bubble: null,
      },
      
      chartTitles: {
        bar: 'Distribution by Category',
        line: 'Trend Over Time',
        donut: 'Breakdown (%)',
        area: 'Cumulative Trend',
        stacked: 'Composition Over Time',
        bubble: 'Correlation Analysis',
      },

      tableColumns: [],
      tableData: [],
    }
  },

  computed: {
    currentYear() {
      return new Date().getFullYear()
    },
    kpiCards() {
      if (!this.data) return []
      
      const sector = this.activeSector
      
      switch (sector) {
        case 'agriculture':
          return [
            {
              title: 'Avg Production',
              value: this.formatNumber(this.data.avg_production),
              unit: 'tons',
              change: 2.5,
            },
            {
              title: 'Total Yield',
              value: this.formatNumber(this.data.total_yield),
              unit: 'kg/ha',
              change: 3.2,
            },
            {
              title: 'Avg Price',
              value: this.formatNumber(this.data.avg_price),
              unit: 'XOF',
              change: 1.8,
            },
            {
              title: 'Data Quality',
              value: (this.data.data_quality_avg * 100).toFixed(1),
              unit: '%',
              change: 0.5,
            },
          ]
        case 'realestate':
          return [
            {
              title: 'Median Price',
              value: this.formatNumber(this.data.median_price),
              unit: 'XOF',
              change: 4.2,
            },
            {
              title: 'Transactions',
              value: this.formatNumber(this.data.total_transactions),
              unit: 'count',
              change: 2.1,
            },
            {
              title: 'Rental Yield',
              value: this.data.rental_yield?.toFixed(2) || 'N/A',
              unit: '%',
              change: 1.5,
            },
            {
              title: 'Infrastructure',
              value: this.data.avg_infrastructure?.toFixed(1) || 'N/A',
              unit: 'score',
              change: 0.3,
            },
          ]
        case 'employment':
          return [
            {
              title: 'Total Employed',
              value: this.formatNumber(this.data.total_employed),
              unit: 'people',
              change: 2.3,
            },
            {
              title: 'Unemployment Rate',
              value: this.data.avg_unemployment_rate?.toFixed(2) || 'N/A',
              unit: '%',
              change: -1.2,
            },
            {
              title: 'Median Salary',
              value: this.formatNumber(this.data.avg_median_salary),
              unit: 'XOF',
              change: 2.8,
            },
            {
              title: 'Informal %',
              value: this.data.avg_informal_rate?.toFixed(2) || 'N/A',
              unit: '%',
              change: -2.5,
            },
          ]
        case 'business':
          return [
            {
              title: 'Total Businesses',
              value: this.formatNumber(this.data.total_businesses),
              unit: 'count',
              change: 5.1,
            },
            {
              title: 'Total Revenue',
              value: this.formatNumber(this.data.total_revenue / 1e9),
              unit: 'B XOF',
              change: 3.7,
            },
            {
              title: 'Employees',
              value: this.formatNumber(this.data.total_employees),
              unit: 'people',
              change: 4.2,
            },
            {
              title: 'Formality Rate',
              value: this.data.avg_formality_rate?.toFixed(2) || 'N/A',
              unit: '%',
              change: 2.1,
            },
          ]
        default:
          return []
      }
    },
  },

  watch: {
    activeSector() {
      this.loadData()
    },
    groupBy() {
      this.loadData()
    },
  },

  mounted() {
    this.loadData()
  },

  methods: {
    async loadData() {
      this.loading = true
      this.destroyCharts()
      
      try {
        const params = {
          year_from: this.yearFrom,
          year_to: this.yearTo,
          group_by: this.groupBy,
        }

        let response
        if (this.activeSector === 'agriculture') {
          response = await api.agriculture.getAggregatedStats(params)
        } else if (this.activeSector === 'realestate') {
          response = await api.realestate.getAggregatedStats(params)
        } else if (this.activeSector === 'employment') {
          response = await api.employment.getAggregatedStats(params)
        } else if (this.activeSector === 'business') {
          response = await api.business.getAggregatedStats(params)
        }

        // Normalize data structure based on sector
        this.data = this.normalizeData(response.data, this.activeSector)
        
        this.prepareTableData()
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        this.loading = false
        // Wait for DOM to update with new data, then init charts
        this.$nextTick(() => {
          setTimeout(() => {
            this.initCharts()
          }, 100)
        })
      }
    },

    normalizeData(apiResponse, sector) {
      // Agriculture has nested structure: { data: { summary, by_commune, by_year, ... }, metadata }
      // Other sectors return: { data: [...], metadata } as list when grouped by year
      
      if (sector === 'agriculture') {
        const inner = apiResponse.data || apiResponse
        // Map by_year to add 'value' field for chart consistency
        const byYear = (inner.by_year || inner.trends?.yearly_data || []).map(d => ({
          year: d.year,
          value: d.production_tonnes || 0,
          yield: d.avg_yield || 0,
          price: d.avg_price || 0,
          area: d.area_ha || 0,
        }))
        return {
          // Summary KPIs
          avg_production: inner.summary?.total_production_tonnes || 0,
          total_yield: inner.summary?.average_yield_t_ha || 0,
          avg_price: inner.summary?.average_price_xof_kg || 0,
          data_quality_avg: inner.summary?.average_quality_score || 0,
          // Grouped data
          by_commune: inner.by_commune || [],
          by_year: byYear,
          by_category: inner.by_crop || [],
          trends: inner.trends || {},
        }
      } else if (sector === 'realestate') {
        // If data is array (grouped by year), convert to proper structure
        if (Array.isArray(apiResponse.data)) {
          const yearData = apiResponse.data
          const latest = yearData[yearData.length - 1] || {}
          return {
            median_price: latest.avg_median_price || 0,
            total_transactions: yearData.reduce((sum, d) => sum + (d.total_transactions || 0), 0),
            rental_yield: latest.avg_rental_yield || 0,
            avg_infrastructure: latest.data_quality || 0,
            by_year: yearData.map(d => ({
              year: d.year,
              value: d.avg_median_price,
              transactions: d.total_transactions,
              rental_yield: d.avg_rental_yield,
            })),
            by_commune: [],
          }
        }
        const inner = apiResponse.data || apiResponse
        return {
          median_price: inner.summary?.avg_median_price || 0,
          total_transactions: inner.summary?.total_transactions || 0,
          rental_yield: inner.summary?.avg_rental_yield || 0,
          avg_infrastructure: inner.summary?.data_quality || 0,
          by_commune: inner.by_commune || [],
          by_year: inner.by_year || [],
        }
      } else if (sector === 'employment') {
        if (Array.isArray(apiResponse.data)) {
          const yearData = apiResponse.data
          const latest = yearData[yearData.length - 1] || {}
          return {
            total_employed: yearData.reduce((sum, d) => sum + (d.total_employed || 0), 0),
            unemployment_rate: latest.avg_unemployment_rate || 0,
            median_salary: latest.avg_median_salary || 0,
            avg_informal_rate: latest.avg_informal_rate || 0,
            by_year: yearData.map(d => ({
              year: d.year,
              value: d.total_employed,
              unemployment: d.avg_unemployment_rate,
              salary: d.avg_median_salary,
            })),
            by_commune: [],
          }
        }
        const inner = apiResponse.data || apiResponse
        return {
          total_employed: inner.summary?.total_employed || 0,
          unemployment_rate: inner.summary?.avg_unemployment_rate || 0,
          median_salary: inner.summary?.avg_median_salary || 0,
          avg_informal_rate: inner.summary?.avg_informal_rate || 0,
          by_commune: inner.by_commune || [],
          by_year: inner.by_year || [],
        }
      } else if (sector === 'business') {
        if (Array.isArray(apiResponse.data)) {
          const yearData = apiResponse.data
          const latest = yearData[yearData.length - 1] || {}
          return {
            total_businesses: yearData.reduce((sum, d) => sum + (d.total_businesses || 0), 0),
            total_revenue: yearData.reduce((sum, d) => sum + (d.total_revenue || 0), 0),
            total_employees: yearData.reduce((sum, d) => sum + (d.total_employees || 0), 0),
            avg_formality_rate: latest.avg_formality_rate || 0,
            by_year: yearData.map(d => ({
              year: d.year,
              value: d.total_businesses,
              revenue: d.total_revenue,
              employees: d.total_employees,
            })),
            by_commune: [],
          }
        }
        const inner = apiResponse.data || apiResponse
        return {
          total_businesses: inner.summary?.total_businesses || 0,
          total_revenue: inner.summary?.total_revenue || 0,
          total_employees: inner.summary?.total_employees || 0,
          avg_formality_rate: inner.summary?.avg_formality_rate || 0,
          by_commune: inner.by_commune || [],
          by_year: inner.by_year || [],
        }
      }
      
      return apiResponse.data || apiResponse
    },

    prepareTableData() {
      if (!this.data) return

      // Use by_year for table when groupBy is year, otherwise by_commune
      if (this.groupBy === 'year' && this.data.by_year && this.data.by_year.length > 0) {
        if (this.activeSector === 'agriculture') {
          this.tableColumns = ['year', 'value', 'yield', 'price']
          this.tableData = this.data.by_year
        } else if (this.activeSector === 'realestate') {
          this.tableColumns = ['year', 'value', 'transactions', 'rental_yield']
          this.tableData = this.data.by_year
        } else if (this.activeSector === 'employment') {
          this.tableColumns = ['year', 'value', 'unemployment', 'salary']
          this.tableData = this.data.by_year
        } else if (this.activeSector === 'business') {
          this.tableColumns = ['year', 'value', 'revenue', 'employees']
          this.tableData = this.data.by_year
        }
      } else if (this.data.by_commune && this.data.by_commune.length > 0) {
        // Extract table columns based on sector - using actual API field names
        if (this.activeSector === 'agriculture') {
          this.tableColumns = ['commune_name', 'production_tonnes', 'avg_yield', 'avg_price', 'records']
          this.tableData = this.data.by_commune
        } else if (this.activeSector === 'realestate') {
          this.tableColumns = ['commune_name', 'avg_median_price', 'total_transactions', 'avg_rental_yield']
          this.tableData = this.data.by_commune
        } else if (this.activeSector === 'employment') {
          this.tableColumns = ['commune_name', 'total_employed', 'avg_unemployment_rate', 'avg_median_salary']
          this.tableData = this.data.by_commune
        } else if (this.activeSector === 'business') {
          this.tableColumns = ['commune_name', 'total_businesses', 'total_revenue', 'total_employees']
          this.tableData = this.data.by_commune
        }
      } else {
        this.tableColumns = []
        this.tableData = []
      }
    },

    initCharts() {
      this.destroyCharts()

      const ctx = {
        bar: this.$refs.barChartRef?.getContext('2d'),
        line: this.$refs.lineChartRef?.getContext('2d'),
        donut: this.$refs.donutChartRef?.getContext('2d'),
        area: this.$refs.areaChartRef?.getContext('2d'),
        stacked: this.$refs.stackedChartRef?.getContext('2d'),
        bubble: this.$refs.bubbleChartRef?.getContext('2d'),
      }

      // Always try to create charts based on available data
      if (this.data.by_year && this.data.by_year.length > 0) {
        this.createLineChart(ctx.line)
        this.createAreaChart(ctx.area)
        this.createStackedChart(ctx.stacked)
        this.createBarChartFromYears(ctx.bar)
        this.createDonutChartFromYears(ctx.donut)
      }
      
      if (this.data.by_commune && this.data.by_commune.length > 0) {
        if (!this.charts.bar) this.createBarChart(ctx.bar)
        if (!this.charts.donut) this.createDonutChart(ctx.donut)
        this.createBubbleChart(ctx.bubble)
      }
    },

    createBarChartFromYears(ctx) {
      if (!ctx || !this.data.by_year || this.data.by_year.length === 0) {
        return
      }

      const sortedData = [...this.data.by_year].sort((a, b) => a.year - b.year)
      const labels = sortedData.map(d => String(Math.floor(d.year)))
      const values = sortedData.map(d => d.value || 0)

      this.charts.bar = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: this.getChartLabel(),
            data: values,
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { display: true } },
          scales: { y: { beginAtZero: true } },
        },
      })
    },

    createDonutChartFromYears(ctx) {
      if (!ctx || !this.data.by_year || this.data.by_year.length === 0) {
        console.log('createDonutChartFromYears: no ctx or data')
        return
      }

      // Use all years, generate enough colors
      const sortedData = [...this.data.by_year].sort((a, b) => a.year - b.year)
      const labels = sortedData.map(d => String(Math.floor(d.year)))
      const values = sortedData.map(d => d.value || 0)
      
      // Generate colors for all years
      const baseColors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(199, 199, 199, 0.7)',
        'rgba(83, 102, 255, 0.7)',
        'rgba(255, 99, 255, 0.7)',
        'rgba(99, 255, 132, 0.7)',
        'rgba(132, 99, 255, 0.7)',
        'rgba(255, 206, 132, 0.7)',
        'rgba(132, 206, 255, 0.7)',
        'rgba(206, 132, 255, 0.7)',
        'rgba(99, 206, 255, 0.7)',
      ]
      const colors = labels.map((_, i) => baseColors[i % baseColors.length])

      this.charts.donut = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{ data: values, backgroundColor: colors, borderWidth: 1 }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { position: 'right' } },
        },
      })
    },

    createBarChart(ctx) {
      if (!ctx || !this.data.by_commune) return

      const labels = this.data.by_commune.map(d => d.commune_name || d.category_name || 'Unknown').slice(0, 10)
      const values = this.getChartValues('primary')

      this.charts.bar = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: this.getChartLabel(),
              data: values.slice(0, 10),
              backgroundColor: 'rgba(75, 192, 192, 0.7)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      })
    },

    createLineChart(ctx) {
      if (!ctx || !this.data.by_year || this.data.by_year.length === 0) {
        return
      }

      // Sort by year and extract values
      const sortedData = [...this.data.by_year].sort((a, b) => a.year - b.year)
      const labels = sortedData.map(d => String(Math.floor(d.year)))
      const values = sortedData.map(d => d.value || 0)

      this.charts.line = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: this.getChartLabel() + ' (Trend)',
              data: values,
              borderColor: 'rgba(54, 162, 235, 1)',
              backgroundColor: 'rgba(54, 162, 235, 0.1)',
              borderWidth: 2,
              fill: false,
              tension: 0.4,
              pointRadius: 4,
              pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      })
    },

    createDonutChart(ctx) {
      if (!ctx) return

      const data = this.groupBy === 'commune' ? this.data.by_commune : this.data.by_category
      if (!data) return

      const labels = data.map(d => d.commune_name || d.category_name || 'Unknown').slice(0, 8)
      const values = this.getChartValues('primary').slice(0, 8)
      const colors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(199, 199, 199, 0.7)',
        'rgba(83, 102, 255, 0.7)',
      ]

      this.charts.donut = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [
            {
              data: values,
              backgroundColor: colors,
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              position: 'right',
            },
          },
        },
      })
    },

    createAreaChart(ctx) {
      if (!ctx || !this.data.by_year || this.data.by_year.length === 0) {
        console.log('createAreaChart: no ctx or data')
        return
      }

      const sortedData = [...this.data.by_year].sort((a, b) => a.year - b.year)
      const labels = sortedData.map(d => String(Math.floor(d.year)))
      const values = sortedData.map(d => d.value || 0)

      this.charts.area = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: this.getChartLabel() + ' (Cumulative)',
              data: values,
              borderColor: 'rgba(255, 99, 132, 1)',
              backgroundColor: 'rgba(255, 99, 132, 0.3)',
              borderWidth: 2,
              fill: true,
              tension: 0.4,
              pointRadius: 3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            y: {
              beginAtZero: true,
              stacked: false,
            },
          },
        },
      })
    },

    createStackedChart(ctx) {
      if (!ctx || !this.data.by_year || this.data.by_year.length === 0) {
        console.log('createStackedChart: no ctx or data')
        return
      }

      const sortedData = [...this.data.by_year].sort((a, b) => a.year - b.year)
      const labels = sortedData.map(d => String(Math.floor(d.year)))
      
      let datasets
      if (this.activeSector === 'business') {
        datasets = [
          {
            label: 'Revenue (B XOF)',
            data: sortedData.map(d => (d.revenue || 0) / 1e9),
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
          },
          {
            label: 'Employees (K)',
            data: sortedData.map(d => (d.employees || 0) / 1000),
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
          },
        ]
      } else if (this.activeSector === 'realestate') {
        datasets = [
          {
            label: 'Transactions',
            data: sortedData.map(d => d.transactions || 0),
            backgroundColor: 'rgba(255, 206, 86, 0.7)',
          },
          {
            label: 'Rental Yield (%)',
            data: sortedData.map(d => (d.rental_yield || 0) * 100),
            backgroundColor: 'rgba(153, 102, 255, 0.7)',
          },
        ]
      } else if (this.activeSector === 'employment') {
        datasets = [
          {
            label: 'Employment (M)',
            data: sortedData.map(d => (d.value || 0) / 1e6),
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
          },
          {
            label: 'Salary (K XOF)',
            data: sortedData.map(d => (d.salary || 0) / 1000),
            backgroundColor: 'rgba(255, 159, 64, 0.7)',
          },
        ]
      } else {
        // Agriculture
        datasets = [
          {
            label: 'Production (K tonnes)',
            data: sortedData.map(d => (d.value || 0) / 1000),
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
          },
        ]
      }

      this.charts.stacked = new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            x: { stacked: true },
            y: { stacked: true, beginAtZero: true },
          },
        },
      })
    },

    createBubbleChart(ctx) {
      if (!ctx || !this.data.by_commune || this.data.by_commune.length === 0) return

      const data = this.data.by_commune.slice(0, 15).map((d, i) => ({
        x: i + 1,
        y: d.production_tonnes || d.avg_median_price || d.total_employed || d.num_businesses || 0,
        r: 8,
        label: d.commune_name || 'Commune ' + (i + 1),
      }))

      this.charts.bubble = new Chart(ctx, {
        type: 'bubble',
        data: {
          datasets: [
            {
              label: 'Communes',
              data,
              backgroundColor: 'rgba(75, 192, 192, 0.5)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            x: { beginAtZero: true },
            y: { beginAtZero: true },
          },
        },
      })
    },

    createSimpleBarChart(ctx) {
      if (!ctx) return

      const labels = ['Total Value']
      const value = this.getChartValue(this.data)

      this.charts.bar = new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: this.getChartLabel(),
              data: [value],
              backgroundColor: 'rgba(75, 192, 192, 0.7)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      })
    },

    createSimpleDonutChart(ctx) {
      if (!ctx) return

      const value = this.getChartValue(this.data)
      const remaining = Math.max(0, value * 0.3)

      this.charts.donut = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: [this.getChartLabel(), 'Remaining'],
          datasets: [
            {
              data: [value, remaining],
              backgroundColor: ['rgba(75, 192, 192, 0.7)', 'rgba(200, 200, 200, 0.3)'],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
        },
      })
    },

    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          chart.destroy()
        }
      })
      this.charts = {
        bar: null,
        line: null,
        donut: null,
        area: null,
        stacked: null,
        bubble: null,
      }
    },

    getChartLabel() {
      const labels = {
        agriculture: 'Production (tons)',
        realestate: 'Median Price (XOF)',
        employment: 'Total Employed',
        business: 'Number of Businesses',
      }
      return labels[this.activeSector] || 'Value'
    },

    getChartValue(item) {
      if (!item) return 0
      // Use 'value' from normalized data, or fallback to actual API field names
      if (item.value !== undefined) return item.value
      if (this.activeSector === 'agriculture') return item.production_tonnes || 0
      if (this.activeSector === 'realestate') return item.avg_median_price || 0
      if (this.activeSector === 'employment') return item.total_employed || 0
      if (this.activeSector === 'business') return item.total_businesses || 0
      return 0
    },

    getChartValues(type = 'primary') {
      if (!this.data) return []
      
      const data = this.groupBy === 'year' ? this.data.by_year : 
                   this.groupBy === 'commune' ? this.data.by_commune :
                   this.groupBy === 'category' ? this.data.by_category : []

      return data.map(d => this.getChartValue(d))
    },

    formatNumber(value) {
      if (!value && value !== 0) return 'N/A'
      return formatPrice(value)
    },

    formatTableCell(value, colName) {
      if (!value && value !== 0) return 'N/A'
      // Year column should be integer
      if (colName === 'year') return String(Math.floor(value))
      if (typeof value === 'number') {
        // Check if it's a year-like value (between 2000-2030)
        if (value >= 2000 && value <= 2030) return String(Math.floor(value))
        // Use formatPrice for price-like values
        if (value > 1000) return formatPrice(value)
        if (value > 100) return value.toFixed(2)
        return value.toFixed(3)
      }
      return String(value)
    },
  },

  beforeUnmount() {
    this.destroyCharts()
  },
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.header h1 {
  font-size: 2.5em;
  margin: 0;
  font-weight: 700;
  color: #1a5f7a;
}

.subtitle {
  font-size: 1.1em;
  color: #666;
  margin: 10px 0 0 0;
}

/* Filters Panel */
.filters-panel {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.sector-selector {
  margin-bottom: 20px;
}

.sector-selector label {
  display: block;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.sector-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.sector-btn {
  padding: 10px 20px;
  border: 2px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  text-transform: uppercase;
  font-size: 0.9em;
}

.sector-btn:hover {
  border-color: #1a5f7a;
  color: #1a5f7a;
}

.sector-btn.active {
  background: #1a5f7a;
  color: white;
  border-color: #1a5f7a;
}

.filter-controls {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
}

.filter-group input,
.filter-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9em;
}

.filter-group input[type="number"] {
  width: 100px;
}

.btn-refresh {
  padding: 8px 16px;
  background: #1a5f7a;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-refresh:hover {
  background: #153d52;
  transform: scale(1.05);
}

/* Loading */
.loading {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ddd;
  border-top-color: #1a5f7a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #1a5f7a;
  transition: transform 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.kpi-card h3 {
  margin: 0 0 10px 0;
  font-size: 0.9em;
  color: #666;
  text-transform: uppercase;
}

.kpi-value {
  font-size: 2em;
  font-weight: 700;
  color: #1a5f7a;
  margin: 10px 0;
}

.kpi-unit {
  font-size: 0.8em;
  color: #999;
  margin-bottom: 10px;
}

.kpi-change {
  font-size: 0.85em;
  font-weight: 600;
}

.kpi-change.positive {
  color: #27ae60;
}

.kpi-change.negative {
  color: #e74c3c;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  min-height: 300px;
}

.chart-card h3 {
  margin-top: 0;
  color: #333;
  font-size: 1em;
  border-bottom: 2px solid #1a5f7a;
  padding-bottom: 10px;
}

.chart-card canvas {
  max-height: 300px;
}

/* Data Table */
.data-table-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.data-table-section h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #1a5f7a;
  padding-bottom: 10px;
}

.table-scroll {
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.data-table thead {
  position: sticky;
  top: 0;
  background: #f5f5f5;
}

.data-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #ddd;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  color: #666;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    flex-direction: column;
  }

  .filter-group input,
  .filter-group select {
    width: 100%;
  }

  .kpi-cards {
    grid-template-columns: 1fr;
  }
}
</style>
