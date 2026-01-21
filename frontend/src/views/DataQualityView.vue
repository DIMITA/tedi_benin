<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Data Quality</h1>
      <p class="subtitle">Understanding our data quality standards and methodology</p>
    </div>

    <div class="content-grid">
      <!-- Quality Score -->
      <section class="quality-section">
        <h2>Quality Score System</h2>
        <div class="quality-card">
          <p>Every data point in TEDI includes a quality score (0.0 - 1.0) indicating reliability:</p>
          
          <div class="score-levels">
            <div class="score-level excellent">
              <span class="score-badge">0.9 - 1.0</span>
              <div class="score-info">
                <strong>Excellent</strong>
                <p>Verified data from official sources, recent collection</p>
              </div>
            </div>
            
            <div class="score-level good">
              <span class="score-badge">0.7 - 0.89</span>
              <div class="score-info">
                <strong>Good</strong>
                <p>Reliable data with minor gaps, cross-validated</p>
              </div>
            </div>
            
            <div class="score-level moderate">
              <span class="score-badge">0.5 - 0.69</span>
              <div class="score-info">
                <strong>Moderate</strong>
                <p>Estimated or interpolated data, use with caution</p>
              </div>
            </div>
            
            <div class="score-level low">
              <span class="score-badge">&lt; 0.5</span>
              <div class="score-info">
                <strong>Low</strong>
                <p>Limited data, projections, or outdated sources</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Data Sources -->
      <section class="quality-section">
        <h2>Data Sources</h2>
        <div class="sources-grid">
          <div class="source-card">
            <h3>FAO</h3>
            <p>Food and Agriculture Organization</p>
            <ul>
              <li>Agricultural production data</li>
              <li>Crop statistics</li>
              <li>Land use information</li>
            </ul>
          </div>
          
          <div class="source-card">
            <h3>World Bank</h3>
            <p>World Development Indicators</p>
            <ul>
              <li>Economic indicators</li>
              <li>Development metrics</li>
              <li>Population data</li>
            </ul>
          </div>
          
          <div class="source-card">
            <h3>ILO</h3>
            <p>International Labour Organization</p>
            <ul>
              <li>Employment statistics</li>
              <li>Labor market data</li>
              <li>Wage information</li>
            </ul>
          </div>
          
          <div class="source-card">
            <h3>INSAE</h3>
            <p>Institut National de la Statistique</p>
            <ul>
              <li>National census data</li>
              <li>Economic surveys</li>
              <li>Regional statistics</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Methodology -->
      <section class="quality-section">
        <h2>Methodology</h2>
        <div class="quality-card">
          <h3>Data Collection</h3>
          <ul>
            <li>Automated ingestion from official APIs</li>
            <li>Regular updates (monthly for most indicators)</li>
            <li>Version control and change tracking</li>
          </ul>
        </div>
        
        <div class="quality-card">
          <h3>Data Validation</h3>
          <ul>
            <li>Cross-source validation</li>
            <li>Outlier detection algorithms</li>
            <li>Historical trend analysis</li>
            <li>Manual review for anomalies</li>
          </ul>
        </div>
        
        <div class="quality-card">
          <h3>Gap Filling</h3>
          <ul>
            <li>Linear interpolation for time series</li>
            <li>Regional averaging for spatial gaps</li>
            <li>Machine learning estimation (clearly marked)</li>
          </ul>
        </div>
      </section>

      <!-- Transparency -->
      <section class="quality-section">
        <h2>Data Transparency</h2>
        <div class="quality-card">
          <p>Each data record includes:</p>
          <ul>
            <li><strong>is_estimated</strong> - Flag indicating estimated vs actual data</li>
            <li><strong>data_quality_score</strong> - Numerical quality rating</li>
            <li><strong>source</strong> - Original data source reference</li>
            <li><strong>last_updated</strong> - Most recent update timestamp</li>
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
  max-width: 1000px;
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

.quality-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #10b981;
}

.quality-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.quality-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d5a27;
  margin-bottom: 0.75rem;
}

.quality-card p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.quality-card ul {
  color: #555;
  padding-left: 1.5rem;
  line-height: 1.8;
}

.score-levels {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
}

.score-level {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f9fafb;
}

.score-badge {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.875rem;
  min-width: 100px;
  text-align: center;
}

.score-level.excellent .score-badge {
  background: #d1fae5;
  color: #065f46;
}

.score-level.good .score-badge {
  background: #dbeafe;
  color: #1e40af;
}

.score-level.moderate .score-badge {
  background: #fef3c7;
  color: #92400e;
}

.score-level.low .score-badge {
  background: #fee2e2;
  color: #991b1b;
}

.score-info strong {
  display: block;
  color: #1a1a2e;
  margin-bottom: 0.25rem;
}

.score-info p {
  margin: 0;
  font-size: 0.875rem;
  color: #666;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.source-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.source-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d5a27;
  margin-bottom: 0.25rem;
}

.source-card > p {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 1rem;
}

.source-card ul {
  font-size: 0.875rem;
  color: #555;
  padding-left: 1.25rem;
  line-height: 1.6;
}
</style>
