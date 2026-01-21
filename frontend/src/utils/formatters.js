/**
 * Utility functions for formatting numbers and prices
 */

/**
 * Format a number with French-style spacing (1 000)
 * @param {number} value - The number to format
 * @returns {string} Formatted number with spaces
 */
export function formatWithSpaces(value) {
  if (value === null || value === undefined) return 'N/A'
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

/**
 * Format a price with k/M/B suffix and French spacing
 * Examples: 1500 -> "1 500", 15000 -> "15k", 1500000 -> "1 500k", 1500000000 -> "1 500M"
 * @param {number} value - The price to format
 * @param {boolean} showDecimals - Whether to show decimals (default: false)
 * @returns {string} Formatted price string
 */
export function formatPrice(value) {
  if (value === null || value === undefined || isNaN(value)) return 'N/A'
  
  const absValue = Math.abs(value)
  const sign = value < 0 ? '-' : ''
  
  // Billions (B)
  if (absValue >= 1e9) {
    const formatted = (absValue / 1e9)
    if (formatted >= 1000) {
      return sign + formatWithSpaces(Math.round(formatted)) + 'B'
    }
    return sign + (formatted % 1 === 0 ? formatted.toFixed(0) : formatted.toFixed(1)) + 'B'
  }
  
  // Millions (M)
  if (absValue >= 1e6) {
    const formatted = (absValue / 1e6)
    if (formatted >= 1000) {
      return sign + formatWithSpaces(Math.round(formatted)) + 'M'
    }
    return sign + (formatted % 1 === 0 ? formatted.toFixed(0) : formatted.toFixed(1)) + 'M'
  }
  
  // Thousands (k)
  if (absValue >= 1e3) {
    const formatted = (absValue / 1e3)
    if (formatted >= 1000) {
      return sign + formatWithSpaces(Math.round(formatted)) + 'k'
    }
    return sign + (formatted % 1 === 0 ? formatted.toFixed(0) : formatted.toFixed(1)) + 'k'
  }
  
  // Less than 1000, just format with spaces if needed
  return sign + (absValue % 1 === 0 ? absValue.toFixed(0) : absValue.toFixed(1))
}

/**
 * Format a number with suffix for dashboard display
 * @param {number} value - The number to format
 * @returns {string} Formatted number with B/M/K suffix
 */
export function formatNumber(value) {
  if (!value && value !== 0) return 'N/A'
  if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B'
  if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M'
  if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K'
  return value.toFixed(2)
}

/**
 * Format percentage
 * @param {number} value - The percentage value (0-100 or 0-1)
 * @param {boolean} isDecimal - Whether the value is in decimal form (0-1)
 * @returns {string} Formatted percentage string
 */
export function formatPercent(value, isDecimal = false) {
  if (value === null || value === undefined) return 'N/A'
  const pct = isDecimal ? value * 100 : value
  return pct.toFixed(1) + '%'
}

/**
 * Format currency in XOF with French formatting
 * @param {number} value - The amount in XOF
 * @returns {string} Formatted currency string
 */
export function formatCurrency(value) {
  if (value === null || value === undefined) return 'N/A'
  return formatPrice(value) + ' XOF'
}
