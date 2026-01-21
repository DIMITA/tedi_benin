<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Terms of Service</h1>
      <p class="subtitle">Last updated: January 2026</p>
    </div>

    <div class="legal-content">
      <section class="legal-section">
        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using the TEDI Platform ("Service"), you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.</p>
      </section>

      <section class="legal-section">
        <h2>2. Description of Service</h2>
        <p>TEDI (Territorial & Economic Data Intelligence) is a platform providing economic and territorial data for Benin. The Service includes:</p>
        <ul>
          <li>Access to aggregated data dashboards</li>
          <li>Interactive data visualization tools</li>
          <li>API access for programmatic data retrieval</li>
          <li>Data export capabilities</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>3. User Accounts</h2>
        <p>To access certain features, you must create an account. You agree to:</p>
        <ul>
          <li>Provide accurate and complete registration information</li>
          <li>Maintain the security of your account credentials</li>
          <li>Accept responsibility for all activities under your account</li>
          <li>Notify us immediately of any unauthorized access</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>4. Acceptable Use</h2>
        <p>You agree not to:</p>
        <ul>
          <li>Use the Service for any unlawful purpose</li>
          <li>Attempt to gain unauthorized access to our systems</li>
          <li>Interfere with or disrupt the Service</li>
          <li>Exceed rate limits or abuse the API</li>
          <li>Resell or redistribute data without authorization</li>
          <li>Use automated tools to scrape data excessively</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>5. API Usage</h2>
        <p>API access is subject to:</p>
        <ul>
          <li>Rate limits as specified in the API documentation</li>
          <li>Scope restrictions based on your API key permissions</li>
          <li>Attribution requirements when displaying data publicly</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>6. Data Accuracy</h2>
        <p>While we strive to provide accurate data:</p>
        <ul>
          <li>Data is provided "as is" without warranties</li>
          <li>Some data may be estimated or interpolated</li>
          <li>Quality scores indicate data reliability</li>
          <li>We are not liable for decisions based on the data</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>7. Intellectual Property</h2>
        <p>The Service and its content are protected by copyright and other intellectual property laws. You may use the data subject to:</p>
        <ul>
          <li>Personal and commercial use with attribution</li>
          <li>Compliance with source data licenses (FAO, World Bank, etc.)</li>
          <li>Not claiming ownership of the underlying data</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>8. Termination</h2>
        <p>We reserve the right to suspend or terminate your account if you violate these terms. Upon termination:</p>
        <ul>
          <li>Your API keys will be revoked</li>
          <li>Access to the Service will be disabled</li>
          <li>Your data may be deleted after a grace period</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>9. Limitation of Liability</h2>
        <p>To the maximum extent permitted by law, TEDI Platform shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service.</p>
      </section>

      <section class="legal-section">
        <h2>10. Changes to Terms</h2>
        <p>We may modify these terms at any time. Continued use of the Service after changes constitutes acceptance of the new terms.</p>
      </section>

      <section class="legal-section">
        <h2>11. Contact</h2>
        <p>For questions about these terms, contact us at:</p>
        <p><strong>Email:</strong> legal@tedi-platform.com</p>
      </section>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.page-container {
  max-width: 800px;
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
  font-size: 1rem;
  color: #666;
}

.legal-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.legal-section {
  margin-bottom: 2rem;
}

.legal-section:last-child {
  margin-bottom: 0;
}

.legal-section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.legal-section p {
  color: #555;
  line-height: 1.7;
  margin-bottom: 0.75rem;
}

.legal-section ul {
  color: #555;
  padding-left: 1.5rem;
  line-height: 1.8;
  margin-bottom: 0.75rem;
}
</style>
