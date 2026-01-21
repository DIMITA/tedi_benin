<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Support</h1>
      <p class="subtitle">Get help with the TEDI platform</p>
    </div>

    <div class="support-content">
      <!-- Contact Options -->
      <section class="support-section">
        <h2>Contact Us</h2>
        <div class="contact-grid">
          <div class="contact-card">
            <div class="contact-icon">📧</div>
            <h3>Email Support</h3>
            <p>For general inquiries and technical support</p>
            <a href="mailto:support@tedi-platform.com" class="contact-link">
              support@tedi-platform.com
            </a>
          </div>
          
          <div class="contact-card">
            <div class="contact-icon">💬</div>
            <h3>Community Forum</h3>
            <p>Connect with other users and developers</p>
            <span class="coming-soon">Coming Soon</span>
          </div>
          
          <div class="contact-card">
            <div class="contact-icon">📚</div>
            <h3>Documentation</h3>
            <p>Comprehensive guides and tutorials</p>
            <router-link to="/documentation" class="contact-link">
              View Documentation →
            </router-link>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section class="support-section">
        <h2>Frequently Asked Questions</h2>
        
        <div class="faq-list">
          <div class="faq-item">
            <h3>How do I get API access?</h3>
            <p>After logging in, navigate to the <router-link to="/api-keys">API Keys</router-link> page to generate your API key. You can create multiple keys with different scopes for various applications.</p>
          </div>
          
          <div class="faq-item">
            <h3>What data is available?</h3>
            <p>TEDI provides data across four sectors: Agriculture, Real Estate, Employment, and Business. Data covers all 77 communes of Benin from 2010 to the present.</p>
          </div>
          
          <div class="faq-item">
            <h3>How often is the data updated?</h3>
            <p>Data is updated regularly from our sources. Agricultural data is typically updated annually, while other indicators may be updated more frequently as new data becomes available.</p>
          </div>
          
          <div class="faq-item">
            <h3>What does the data quality score mean?</h3>
            <p>Each data point includes a quality score from 0 to 1. Scores above 0.9 indicate verified data, while lower scores indicate estimated or interpolated values. See our <router-link to="/data-quality">Data Quality</router-link> page for details.</p>
          </div>
          
          <div class="faq-item">
            <h3>Can I download the data?</h3>
            <p>Yes! You can export data to CSV from any data view using the "Export CSV" button. For programmatic access, use our REST API with your API key.</p>
          </div>
          
          <div class="faq-item">
            <h3>Is there a rate limit on the API?</h3>
            <p>Yes, the API has rate limits to ensure fair usage: 100 requests per minute for standard endpoints and 10 requests per minute for bulk operations.</p>
          </div>
        </div>
      </section>

      <!-- Report Issue -->
      <section class="support-section">
        <h2>Report an Issue</h2>
        <div class="report-card">
          <p>Found a bug or have a feature request? We'd love to hear from you.</p>
          <div class="report-options">
            <a href="mailto:bugs@tedi-platform.com" class="report-btn">
              🐛 Report a Bug
            </a>
            <a href="mailto:features@tedi-platform.com" class="report-btn secondary">
              💡 Request a Feature
            </a>
          </div>
        </div>
      </section>

      <!-- System Status -->
      <section class="support-section">
        <h2>System Status</h2>
        <div class="status-card">
          <div class="status-indicator online">
            <span class="status-dot"></span>
            All Systems Operational
          </div>
          <div class="status-services">
            <div class="service">
              <span class="service-name">API</span>
              <span class="service-status online">Operational</span>
            </div>
            <div class="service">
              <span class="service-name">Database</span>
              <span class="service-status online">Operational</span>
            </div>
            <div class="service">
              <span class="service-name">Dashboard</span>
              <span class="service-status online">Operational</span>
            </div>
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

.support-content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.support-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #10b981;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.contact-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.contact-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.contact-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.contact-card p {
  color: #666;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.contact-link {
  color: #2d5a27;
  font-weight: 600;
  text-decoration: none;
}

.contact-link:hover {
  color: #10b981;
}

.coming-soon {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #fef3c7;
  color: #92400e;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.faq-item h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.faq-item p {
  color: #555;
  line-height: 1.6;
  margin: 0;
}

.faq-item a {
  color: #2d5a27;
  font-weight: 500;
}

.report-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.report-card p {
  color: #555;
  margin-bottom: 1rem;
}

.report-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.report-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #2d5a27;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.2s;
}

.report-btn:hover {
  background: #10b981;
}

.report-btn.secondary {
  background: #f3f4f6;
  color: #1a1a2e;
}

.report-btn.secondary:hover {
  background: #e5e7eb;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  font-size: 1.125rem;
  margin-bottom: 1.5rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.online .status-dot {
  background: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-services {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.service {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.service-name {
  font-weight: 500;
  color: #1a1a2e;
}

.service-status {
  font-size: 0.875rem;
  font-weight: 600;
}

.service-status.online {
  color: #10b981;
}
</style>
