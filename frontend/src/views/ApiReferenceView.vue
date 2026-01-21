<template>
  <div class="page-container">
    <div class="page-header">
      <h1>API Reference</h1>
      <p class="subtitle">Complete API documentation for developers</p>
    </div>

    <div class="api-content">
      <!-- Authentication -->
      <section class="api-section">
        <h2>Authentication</h2>
        <div class="api-card">
          <p>All API requests require an API key passed in the header:</p>
          <div class="code-block">
            <code>X-API-KEY: your_api_key_here</code>
          </div>
          <p>Generate API keys from your <router-link to="/api-keys">API Keys dashboard</router-link>.</p>
        </div>
      </section>

      <!-- Base URL -->
      <section class="api-section">
        <h2>Base URL</h2>
        <div class="api-card">
          <div class="code-block">
            <code>http://localhost:5000/api/v1</code>
          </div>
        </div>
      </section>

      <!-- Endpoints -->
      <section class="api-section">
        <h2>Endpoints</h2>

        <!-- Agriculture -->
        <div class="endpoint-group">
          <h3>🌾 Agriculture</h3>
          
          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/agriculture/stats</code>
            </div>
            <p>Get agriculture statistics with filters</p>
            <div class="params">
              <h4>Query Parameters:</h4>
              <ul>
                <li><code>commune_id</code> - Filter by commune ID</li>
                <li><code>crop_id</code> - Filter by crop ID</li>
                <li><code>year</code> - Filter by year</li>
                <li><code>page</code> - Page number (default: 1)</li>
                <li><code>per_page</code> - Items per page (default: 20)</li>
              </ul>
            </div>
          </div>

          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/agriculture/stats/aggregated</code>
            </div>
            <p>Get aggregated agriculture data</p>
            <div class="params">
              <h4>Query Parameters:</h4>
              <ul>
                <li><code>group_by</code> - Group by: year, commune, crop</li>
                <li><code>year_from</code> - Start year</li>
                <li><code>year_to</code> - End year</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Real Estate -->
        <div class="endpoint-group">
          <h3>🏠 Real Estate</h3>
          
          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/realestate/stats</code>
            </div>
            <p>Get real estate statistics with filters</p>
            <div class="params">
              <h4>Query Parameters:</h4>
              <ul>
                <li><code>commune_id</code> - Filter by commune ID</li>
                <li><code>property_type_id</code> - Filter by property type</li>
                <li><code>year</code> - Filter by year</li>
                <li><code>geo_zone</code> - Filter: urban, peri_urban, rural</li>
              </ul>
            </div>
          </div>

          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/realestate/stats/aggregated</code>
            </div>
            <p>Get aggregated real estate data</p>
          </div>
        </div>

        <!-- Employment -->
        <div class="endpoint-group">
          <h3>💼 Employment</h3>
          
          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/employment/stats</code>
            </div>
            <p>Get employment statistics with filters</p>
            <div class="params">
              <h4>Query Parameters:</h4>
              <ul>
                <li><code>commune_id</code> - Filter by commune ID</li>
                <li><code>job_category_id</code> - Filter by job category</li>
                <li><code>year</code> - Filter by year</li>
                <li><code>sector</code> - Filter: primary, secondary, tertiary</li>
              </ul>
            </div>
          </div>

          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/employment/stats/aggregated</code>
            </div>
            <p>Get aggregated employment data</p>
          </div>
        </div>

        <!-- Business -->
        <div class="endpoint-group">
          <h3>🏢 Business</h3>
          
          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/business/stats</code>
            </div>
            <p>Get business statistics with filters</p>
            <div class="params">
              <h4>Query Parameters:</h4>
              <ul>
                <li><code>commune_id</code> - Filter by commune ID</li>
                <li><code>sector_id</code> - Filter by business sector</li>
                <li><code>year</code> - Filter by year</li>
                <li><code>market_saturation</code> - Filter saturation level</li>
              </ul>
            </div>
          </div>

          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/business/stats/aggregated</code>
            </div>
            <p>Get aggregated business data</p>
          </div>
        </div>

        <!-- Geo -->
        <div class="endpoint-group">
          <h3>🗺️ Geographic</h3>
          
          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/geo/communes</code>
            </div>
            <p>Get list of all communes</p>
          </div>

          <div class="endpoint">
            <div class="endpoint-header">
              <span class="method get">GET</span>
              <code>/geo/communes/{id}</code>
            </div>
            <p>Get commune details by ID</p>
          </div>
        </div>
      </section>

      <!-- Response Format -->
      <section class="api-section">
        <h2>Response Format</h2>
        <div class="api-card">
          <p>All responses are in JSON format:</p>
          <div class="code-block">
<pre>{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}</pre>
          </div>
        </div>
      </section>

      <!-- Rate Limiting -->
      <section class="api-section">
        <h2>Rate Limiting</h2>
        <div class="api-card">
          <ul>
            <li><strong>Default limit:</strong> 100 requests per minute</li>
            <li><strong>Bulk operations:</strong> 10 requests per minute</li>
            <li>Rate limit headers included in responses</li>
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

.api-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.api-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #10b981;
}

.api-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.api-card p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.api-card ul {
  color: #555;
  padding-left: 1.5rem;
  line-height: 1.8;
}

.code-block {
  background: #1a1a2e;
  color: #10b981;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.875rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.code-block pre {
  margin: 0;
  white-space: pre-wrap;
}

.endpoint-group {
  margin-bottom: 2rem;
}

.endpoint-group h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d5a27;
  margin-bottom: 1rem;
}

.endpoint {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.endpoint-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.method {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.method.get {
  background: #d1fae5;
  color: #065f46;
}

.endpoint-header code {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.9rem;
  color: #1a1a2e;
}

.endpoint > p {
  color: #666;
  margin-bottom: 1rem;
}

.params h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #444;
  margin-bottom: 0.5rem;
}

.params ul {
  list-style: none;
  padding: 0;
}

.params li {
  font-size: 0.875rem;
  color: #555;
  padding: 0.25rem 0;
}

.params li code {
  background: #f3f4f6;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #2d5a27;
}
</style>
