<template>
  <div class="page-container">
    <div class="page-header">
      <h1>License</h1>
      <p class="subtitle">Data and Software Licensing Information</p>
    </div>

    <div class="license-content">
      <!-- Platform License -->
      <section class="license-section">
        <h2>Platform License</h2>
        <div class="license-card">
          <div class="license-badge">MIT License</div>
          <p>The TEDI Platform software is released under the MIT License, which permits:</p>
          <ul>
            <li>✓ Commercial use</li>
            <li>✓ Modification</li>
            <li>✓ Distribution</li>
            <li>✓ Private use</li>
          </ul>
          <div class="license-text">
            <p>Copyright © 2026 TEDI Platform</p>
            <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>
            <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>
            <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.</p>
          </div>
        </div>
      </section>

      <!-- Data Licenses -->
      <section class="license-section">
        <h2>Data Licenses</h2>
        <p class="section-intro">The data provided through TEDI comes from various sources, each with their own licensing terms:</p>
        
        <div class="data-license-card">
          <h3>FAO Data</h3>
          <div class="license-badge secondary">CC BY-NC-SA 3.0 IGO</div>
          <p>Food and Agriculture Organization data is available under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 IGO license.</p>
          <a href="https://www.fao.org/contact-us/terms/en/" target="_blank" class="license-link">
            View FAO Terms →
          </a>
        </div>
        
        <div class="data-license-card">
          <h3>World Bank Data</h3>
          <div class="license-badge secondary">CC BY 4.0</div>
          <p>World Bank Open Data is available under the Creative Commons Attribution 4.0 International license.</p>
          <a href="https://datacatalog.worldbank.org/public-licenses" target="_blank" class="license-link">
            View World Bank License →
          </a>
        </div>
        
        <div class="data-license-card">
          <h3>ILO Data</h3>
          <div class="license-badge secondary">CC BY 4.0</div>
          <p>ILOSTAT data is available under the Creative Commons Attribution 4.0 International license.</p>
          <a href="https://ilostat.ilo.org/resources/concepts-and-definitions/description-data-and-metadata/" target="_blank" class="license-link">
            View ILO Terms →
          </a>
        </div>
        
        <div class="data-license-card">
          <h3>OpenStreetMap Data</h3>
          <div class="license-badge secondary">ODbL</div>
          <p>Geographic data from OpenStreetMap is available under the Open Database License (ODbL).</p>
          <a href="https://www.openstreetmap.org/copyright" target="_blank" class="license-link">
            View OSM License →
          </a>
        </div>
      </section>

      <!-- Attribution Requirements -->
      <section class="license-section">
        <h2>Attribution Requirements</h2>
        <div class="license-card">
          <p>When using data from TEDI, please include appropriate attribution:</p>
          <div class="attribution-example">
            <code>Data source: TEDI Platform (tedi-platform.com), incorporating data from FAO, World Bank, ILO, and OpenStreetMap.</code>
          </div>
          <p>For specific data sources, additional attribution may be required per their license terms.</p>
        </div>
      </section>

      <!-- API Usage -->
      <section class="license-section">
        <h2>API Usage Terms</h2>
        <div class="license-card">
          <p>Use of the TEDI API is subject to:</p>
          <ul>
            <li>Rate limits as specified in documentation</li>
            <li>Attribution requirements when displaying data</li>
            <li>Compliance with underlying data source licenses</li>
            <li>Prohibition of reselling raw data downloads</li>
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
  max-width: 900px;
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

.license-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.license-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #10b981;
}

.section-intro {
  color: #555;
  margin-bottom: 1.5rem;
}

.license-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.license-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  background: #d1fae5;
  color: #065f46;
  border-radius: 50px;
  font-size: 0.875rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.license-badge.secondary {
  background: #dbeafe;
  color: #1e40af;
}

.license-card p,
.data-license-card p {
  color: #555;
  line-height: 1.7;
  margin-bottom: 0.75rem;
}

.license-card ul {
  color: #555;
  padding-left: 1.5rem;
  line-height: 1.8;
  margin-bottom: 0.75rem;
}

.license-text {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #666;
  line-height: 1.6;
}

.license-text p {
  margin-bottom: 0.75rem;
  font-size: 0.8rem;
}

.data-license-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.data-license-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.license-link {
  display: inline-block;
  color: #2d5a27;
  font-weight: 600;
  text-decoration: none;
  margin-top: 0.5rem;
}

.license-link:hover {
  color: #10b981;
}

.attribution-example {
  background: #1a1a2e;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.attribution-example code {
  color: #10b981;
  font-size: 0.875rem;
  font-family: 'Monaco', 'Menlo', monospace;
}
</style>
