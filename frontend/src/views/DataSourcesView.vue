<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Data Sources</h1>
      <p class="subtitle">Our trusted data providers and sources</p>
    </div>

    <div class="sources-content">
      <!-- Primary Sources -->
      <section class="sources-section">
        <h2>Primary Data Sources</h2>
        
        <div class="source-card featured">
          <div class="source-logo">
            <span class="logo-text">FAO</span>
          </div>
          <div class="source-details">
            <h3>Food and Agriculture Organization</h3>
            <p>The FAO is a specialized agency of the United Nations that leads international efforts to defeat hunger and improve nutrition and food security.</p>
            <div class="source-data">
              <span class="data-tag">Agricultural Production</span>
              <span class="data-tag">Crop Statistics</span>
              <span class="data-tag">Trade Data</span>
            </div>
            <a href="https://www.fao.org/faostat" target="_blank" class="source-link">
              Visit FAOSTAT →
            </a>
          </div>
        </div>

        <div class="source-card featured">
          <div class="source-logo">
            <span class="logo-text">WB</span>
          </div>
          <div class="source-details">
            <h3>World Bank</h3>
            <p>The World Bank provides free and open access to global development data through its Open Data initiative.</p>
            <div class="source-data">
              <span class="data-tag">Economic Indicators</span>
              <span class="data-tag">Development Data</span>
              <span class="data-tag">Population</span>
            </div>
            <a href="https://data.worldbank.org" target="_blank" class="source-link">
              Visit World Bank Data →
            </a>
          </div>
        </div>

        <div class="source-card featured">
          <div class="source-logo">
            <span class="logo-text">ILO</span>
          </div>
          <div class="source-details">
            <h3>International Labour Organization</h3>
            <p>ILOSTAT provides comprehensive labor statistics for countries worldwide.</p>
            <div class="source-data">
              <span class="data-tag">Employment</span>
              <span class="data-tag">Unemployment</span>
              <span class="data-tag">Wages</span>
            </div>
            <a href="https://ilostat.ilo.org" target="_blank" class="source-link">
              Visit ILOSTAT →
            </a>
          </div>
        </div>
      </section>

      <!-- National Sources -->
      <section class="sources-section">
        <h2>National Sources (Benin)</h2>
        
        <div class="source-card">
          <div class="source-logo secondary">
            <span class="logo-text">INSAE</span>
          </div>
          <div class="source-details">
            <h3>Institut National de la Statistique et de l'Analyse Économique</h3>
            <p>Benin's national statistics office provides official statistics on demographics, economy, and social indicators.</p>
            <div class="source-data">
              <span class="data-tag">Census Data</span>
              <span class="data-tag">Economic Surveys</span>
              <span class="data-tag">Regional Data</span>
            </div>
          </div>
        </div>

        <div class="source-card">
          <div class="source-logo secondary">
            <span class="logo-text">MAEP</span>
          </div>
          <div class="source-details">
            <h3>Ministère de l'Agriculture, de l'Élevage et de la Pêche</h3>
            <p>Official agricultural statistics and policies from Benin's Ministry of Agriculture.</p>
            <div class="source-data">
              <span class="data-tag">Agricultural Policy</span>
              <span class="data-tag">Production Stats</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Geographic Sources -->
      <section class="sources-section">
        <h2>Geographic Data</h2>
        
        <div class="source-card">
          <div class="source-logo geo">
            <span class="logo-text">OSM</span>
          </div>
          <div class="source-details">
            <h3>OpenStreetMap</h3>
            <p>OpenStreetMap is a collaborative project to create a free editable geographic database of the world.</p>
            <div class="source-data">
              <span class="data-tag">Boundaries</span>
              <span class="data-tag">Infrastructure</span>
              <span class="data-tag">Points of Interest</span>
            </div>
            <a href="https://www.openstreetmap.org" target="_blank" class="source-link">
              Visit OpenStreetMap →
            </a>
          </div>
        </div>
      </section>

      <!-- Data Coverage -->
      <section class="sources-section">
        <h2>Data Coverage</h2>
        <div class="coverage-grid">
          <div class="coverage-card">
            <div class="coverage-value">77</div>
            <div class="coverage-label">Communes</div>
            <p>All communes of Benin</p>
          </div>
          <div class="coverage-card">
            <div class="coverage-value">15</div>
            <div class="coverage-label">Years</div>
            <p>2010 - Present</p>
          </div>
          <div class="coverage-card">
            <div class="coverage-value">4</div>
            <div class="coverage-label">Sectors</div>
            <p>Agriculture, Real Estate, Employment, Business</p>
          </div>
          <div class="coverage-card">
            <div class="coverage-value">68k+</div>
            <div class="coverage-label">Data Points</div>
            <p>And growing</p>
          </div>
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

.sources-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.sources-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #10b981;
}

.source-card {
  display: flex;
  gap: 1.5rem;
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.source-logo {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #2d5a27, #10b981);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.source-logo.secondary {
  background: linear-gradient(135deg, #1e40af, #3b82f6);
}

.source-logo.geo {
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
}

.logo-text {
  color: white;
  font-weight: 700;
  font-size: 1rem;
}

.source-details h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.source-details > p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.source-data {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.data-tag {
  padding: 0.25rem 0.75rem;
  background: #f0fdf4;
  color: #166534;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
}

.source-link {
  display: inline-block;
  color: #2d5a27;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.source-link:hover {
  color: #10b981;
}

.coverage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.coverage-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.coverage-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #10b981;
  margin-bottom: 0.25rem;
}

.coverage-label {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.coverage-card p {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}

@media (max-width: 640px) {
  .source-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .source-data {
    justify-content: center;
  }
}
</style>
