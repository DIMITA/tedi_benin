<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Documentation</h1>
      <p class="subtitle">Learn how to use the TEDI platform effectively</p>
    </div>

    <div class="content-grid">
      <!-- Getting Started -->
      <section class="doc-section">
        <h2>Getting Started</h2>
        <div class="doc-card">
          <h3>Platform Overview</h3>
          <p>TEDI (Territorial & Economic Data Intelligence) is a comprehensive platform providing economic and territorial data for Benin's 77 communes.</p>
          <ul>
            <li>Access 15 years of historical data (2010-present)</li>
            <li>4 major data sectors: Agriculture, Real Estate, Employment, Business</li>
            <li>Interactive maps and visualizations</li>
            <li>RESTful API for programmatic access</li>
          </ul>
        </div>

        <div class="doc-card">
          <h3>Quick Start Guide</h3>
          <ol>
            <li><strong>Create an account</strong> - Sign up to access the platform</li>
            <li><strong>Explore the Dashboard</strong> - View aggregated data across all sectors</li>
            <li><strong>Generate API Keys</strong> - Access data programmatically</li>
            <li><strong>Use the Interactive Map</strong> - Visualize data geographically</li>
          </ol>
        </div>
      </section>

      <!-- Data Sectors -->
      <section class="doc-section">
        <h2>Data Sectors</h2>
        
        <div class="doc-card">
          <h3>🌾 Agriculture Index</h3>
          <p>Agricultural production data including:</p>
          <ul>
            <li>Production volumes (tonnes)</li>
            <li>Crop yields (tonnes/hectare)</li>
            <li>Harvested areas (hectares)</li>
            <li>Market prices (XOF/kg)</li>
          </ul>
        </div>

        <div class="doc-card">
          <h3>🏠 Real Estate Index</h3>
          <p>Property market data including:</p>
          <ul>
            <li>Price per square meter</li>
            <li>Median property prices</li>
            <li>Transaction volumes</li>
            <li>Rental yields</li>
          </ul>
        </div>

        <div class="doc-card">
          <h3>💼 Employment Index</h3>
          <p>Labor market data including:</p>
          <ul>
            <li>Employment statistics</li>
            <li>Unemployment rates</li>
            <li>Median salaries</li>
            <li>Informal sector data</li>
          </ul>
        </div>

        <div class="doc-card">
          <h3>🏢 Business Index</h3>
          <p>Business environment data including:</p>
          <ul>
            <li>Number of businesses</li>
            <li>Revenue estimates</li>
            <li>Market saturation</li>
            <li>Competition intensity</li>
          </ul>
        </div>
      </section>

      <!-- Features -->
      <section class="doc-section">
        <h2>Platform Features</h2>
        
        <div class="doc-card">
          <h3>Dashboard</h3>
          <p>The multi-sector dashboard provides:</p>
          <ul>
            <li>Real-time data visualization</li>
            <li>6 chart types (Bar, Line, Donut, Area, Stacked, Bubble)</li>
            <li>Filter by year range, region, and category</li>
            <li>Export data to CSV</li>
          </ul>
        </div>

        <div class="doc-card">
          <h3>Interactive Map</h3>
          <p>Geographic visualization features:</p>
          <ul>
            <li>All 77 communes of Benin</li>
            <li>Color-coded data indicators</li>
            <li>Click to view detailed statistics</li>
            <li>Layer switching between sectors</li>
          </ul>
        </div>

        <div class="doc-card">
          <h3>API Access</h3>
          <p>Programmatic data access:</p>
          <ul>
            <li>RESTful API endpoints</li>
            <li>JSON response format</li>
            <li>Scope-based access control</li>
            <li>Rate limiting for fair usage</li>
          </ul>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.125rem;
  color: #666;
}

.content-grid {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.doc-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #10b981;
}

.doc-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.doc-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d5a27;
  margin-bottom: 0.75rem;
}

.doc-card p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.doc-card ul,
.doc-card ol {
  color: #555;
  padding-left: 1.5rem;
  line-height: 1.8;
}

.doc-card li {
  margin-bottom: 0.25rem;
}
</style>
