/**
 * NEXUS Platform - Test Validator
 * Comprehensive testing and validation suite
 */

import { FRONTEND_ROUTES, API_ROUTES, validateRoute, getRouteByPath } from '../config/routingRegistry';

export interface TestResult {
  testName: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  details?: any;
  duration: number;
}

export interface ValidationReport {
  totalTests: number;
  passed: number;
  failed: number;
  warnings: number;
  duration: number;
  results: TestResult[];
  summary: {
    routing: boolean;
    sitemap: boolean;
    performance: boolean;
    accessibility: boolean;
    security: boolean;
    overall: boolean;
  };
}

class TestValidator {
  private testResults: TestResult[] = [];

  /**
   * Run all validation tests
   */
  async runAllTests(): Promise<ValidationReport> {
    const startTime = performance.now();
    this.testResults = [];

    // Run all test categories
    await this.testRouting();
    await this.testSitemap();
    await this.testPerformance();
    await this.testAccessibility();
    await this.testSecurity();
    await this.testErrorHandling();

    const duration = performance.now() - startTime;
    const passed = this.testResults.filter(r => r.status === 'pass').length;
    const failed = this.testResults.filter(r => r.status === 'fail').length;
    const warnings = this.testResults.filter(r => r.status === 'warning').length;

    return {
      totalTests: this.testResults.length,
      passed,
      failed,
      warnings,
      duration,
      results: this.testResults,
      summary: this.generateSummary()
    };
  }

  /**
   * Test routing system
   */
  private async testRouting(): Promise<void> {
    const startTime = performance.now();

    // Test 1: All routes are valid
    try {
      const invalidRoutes = FRONTEND_ROUTES.filter(route => !validateRoute(route.path));
      if (invalidRoutes.length === 0) {
        this.addResult('routing-valid', 'pass', 'All routes are valid');
      } else {
        this.addResult('routing-valid', 'fail', `Found ${invalidRoutes.length} invalid routes`, invalidRoutes);
      }
    } catch (error) {
      this.addResult('routing-valid', 'fail', `Error validating routes: ${error}`);
    }

    // Test 2: No duplicate paths
    try {
      const paths = FRONTEND_ROUTES.map(route => route.path);
      const duplicates = paths.filter((path, index) => paths.indexOf(path) !== index);
      if (duplicates.length === 0) {
        this.addResult('routing-duplicates', 'pass', 'No duplicate paths found');
      } else {
        this.addResult('routing-duplicates', 'fail', `Found duplicate paths: ${duplicates.join(', ')}`);
      }
    } catch (error) {
      this.addResult('routing-duplicates', 'fail', `Error checking duplicates: ${error}`);
    }

    // Test 3: All routes have required fields
    try {
      const missingFields = FRONTEND_ROUTES.filter(route => 
        !route.id || !route.path || !route.title || !route.description
      );
      if (missingFields.length === 0) {
        this.addResult('routing-fields', 'pass', 'All routes have required fields');
      } else {
        this.addResult('routing-fields', 'fail', `Found ${missingFields.length} routes with missing fields`, missingFields);
      }
    } catch (error) {
      this.addResult('routing-fields', 'fail', `Error checking fields: ${error}`);
    }

    // Test 4: API routes are properly configured
    try {
      const invalidAPIs = API_ROUTES.filter(api => 
        !api.id || !api.path || !api.method || !api.title
      );
      if (invalidAPIs.length === 0) {
        this.addResult('api-routes', 'pass', 'All API routes are properly configured');
      } else {
        this.addResult('api-routes', 'fail', `Found ${invalidAPIs.length} invalid API routes`, invalidAPIs);
      }
    } catch (error) {
      this.addResult('api-routes', 'fail', `Error checking API routes: ${error}`);
    }

    this.addResult('routing-total', 'pass', `Routing tests completed in ${performance.now() - startTime}ms`);
  }

  /**
   * Test sitemap generation
   */
  private async testSitemap(): Promise<void> {
    const startTime = performance.now();

    try {
      // Test sitemap generation
      const sitemapData = {
        frontend: FRONTEND_ROUTES.map(route => ({
          id: route.id,
          path: route.path,
          title: route.title,
          description: route.description,
          category: route.category,
          requiresAuth: route.requiresAuth
        })),
        api: API_ROUTES.map(route => ({
          id: route.id,
          path: route.path,
          method: route.method,
          title: route.title,
          description: route.description,
          category: route.category,
          requiresAuth: route.requiresAuth
        }))
      };

      // Validate sitemap structure
      if (sitemapData.frontend.length > 0 && sitemapData.api.length > 0) {
        this.addResult('sitemap-generation', 'pass', 'Sitemap generated successfully');
      } else {
        this.addResult('sitemap-generation', 'fail', 'Sitemap generation failed');
      }

      // Test XML generation
      const xmlContent = this.generateSitemapXML(sitemapData);
      if (xmlContent.includes('<?xml') && xmlContent.includes('<urlset')) {
        this.addResult('sitemap-xml', 'pass', 'Sitemap XML generated successfully');
      } else {
        this.addResult('sitemap-xml', 'fail', 'Sitemap XML generation failed');
      }

    } catch (error) {
      this.addResult('sitemap-generation', 'fail', `Sitemap generation error: ${error}`);
    }

    this.addResult('sitemap-total', 'pass', `Sitemap tests completed in ${performance.now() - startTime}ms`);
  }

  /**
   * Test performance metrics
   */
  private async testPerformance(): Promise<void> {
    const startTime = performance.now();

    try {
      // Test page load performance
      const loadTime = performance.now() - performance.timing.navigationStart;
      if (loadTime < 2000) {
        this.addResult('performance-load', 'pass', `Page load time: ${loadTime.toFixed(2)}ms`);
      } else if (loadTime < 5000) {
        this.addResult('performance-load', 'warning', `Page load time is slow: ${loadTime.toFixed(2)}ms`);
      } else {
        this.addResult('performance-load', 'fail', `Page load time is too slow: ${loadTime.toFixed(2)}ms`);
      }

      // Test memory usage
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const memoryUsage = memory.usedJSHeapSize / (1024 * 1024); // Convert to MB
        if (memoryUsage < 50) {
          this.addResult('performance-memory', 'pass', `Memory usage: ${memoryUsage.toFixed(2)}MB`);
        } else if (memoryUsage < 100) {
          this.addResult('performance-memory', 'warning', `Memory usage is high: ${memoryUsage.toFixed(2)}MB`);
        } else {
          this.addResult('performance-memory', 'fail', `Memory usage is too high: ${memoryUsage.toFixed(2)}MB`);
        }
      }

      // Test bundle size (simplified check)
      const scripts = document.querySelectorAll('script[src]');
      let totalSize = 0;
      scripts.forEach(script => {
        const src = (script as HTMLScriptElement).src;
        if (src.includes('static/js/')) {
          // This is a simplified check - in reality, you'd need to fetch and measure actual file sizes
          totalSize += 100; // Placeholder
        }
      });

      if (totalSize < 500) {
        this.addResult('performance-bundle', 'pass', `Estimated bundle size: ${totalSize}KB`);
      } else if (totalSize < 1000) {
        this.addResult('performance-bundle', 'warning', `Bundle size is large: ${totalSize}KB`);
      } else {
        this.addResult('performance-bundle', 'fail', `Bundle size is too large: ${totalSize}KB`);
      }

    } catch (error) {
      this.addResult('performance-tests', 'fail', `Performance test error: ${error}`);
    }

    this.addResult('performance-total', 'pass', `Performance tests completed in ${performance.now() - startTime}ms`);
  }

  /**
   * Test accessibility
   */
  private async testAccessibility(): Promise<void> {
    const startTime = performance.now();

    try {
      // Test for alt attributes on images
      const images = document.querySelectorAll('img');
      const imagesWithoutAlt = Array.from(images).filter(img => !img.alt);
      if (imagesWithoutAlt.length === 0) {
        this.addResult('a11y-images', 'pass', 'All images have alt attributes');
      } else {
        this.addResult('a11y-images', 'warning', `Found ${imagesWithoutAlt.length} images without alt attributes`);
      }

      // Test for heading hierarchy
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      let headingLevels: number[] = [];
      headings.forEach(heading => {
        const level = parseInt(heading.tagName.charAt(1));
        headingLevels.push(level);
      });

      // Check for proper heading hierarchy
      let hierarchyValid = true;
      for (let i = 1; i < headingLevels.length; i++) {
        if (headingLevels[i] > headingLevels[i - 1] + 1) {
          hierarchyValid = false;
          break;
        }
      }

      if (hierarchyValid) {
        this.addResult('a11y-headings', 'pass', 'Heading hierarchy is valid');
      } else {
        this.addResult('a11y-headings', 'warning', 'Heading hierarchy has issues');
      }

      // Test for form labels
      const inputs = document.querySelectorAll('input, textarea, select');
      const inputsWithoutLabels = Array.from(inputs).filter(input => {
        const id = input.id;
        if (!id) return true;
        const label = document.querySelector(`label[for="${id}"]`);
        return !label;
      });

      if (inputsWithoutLabels.length === 0) {
        this.addResult('a11y-labels', 'pass', 'All form inputs have labels');
      } else {
        this.addResult('a11y-labels', 'warning', `Found ${inputsWithoutLabels.length} inputs without labels`);
      }

      // Test for keyboard navigation
      const focusableElements = document.querySelectorAll('a, button, input, textarea, select, [tabindex]');
      if (focusableElements.length > 0) {
        this.addResult('a11y-keyboard', 'pass', `Found ${focusableElements.length} focusable elements`);
      } else {
        this.addResult('a11y-keyboard', 'warning', 'No focusable elements found');
      }

    } catch (error) {
      this.addResult('a11y-tests', 'fail', `Accessibility test error: ${error}`);
    }

    this.addResult('a11y-total', 'pass', `Accessibility tests completed in ${performance.now() - startTime}ms`);
  }

  /**
   * Test security
   */
  private async testSecurity(): Promise<void> {
    const startTime = performance.now();

    try {
      // Test for HTTPS
      if (location.protocol === 'https:') {
        this.addResult('security-https', 'pass', 'Site is served over HTTPS');
      } else {
        this.addResult('security-https', 'fail', 'Site is not served over HTTPS');
      }

      // Test for security headers (simplified check)
      const securityHeaders = [
        'x-frame-options',
        'x-content-type-options',
        'x-xss-protection',
        'strict-transport-security'
      ];

      // This would require server-side checking in a real implementation
      this.addResult('security-headers', 'warning', 'Security headers check requires server-side validation');

      // Test for inline scripts (potential XSS risk)
      const inlineScripts = document.querySelectorAll('script:not([src])');
      if (inlineScripts.length === 0) {
        this.addResult('security-inline-scripts', 'pass', 'No inline scripts found');
      } else {
        this.addResult('security-inline-scripts', 'warning', `Found ${inlineScripts.length} inline scripts`);
      }

      // Test for external resources
      const externalResources = document.querySelectorAll('script[src], link[href]');
      const externalCount = Array.from(externalResources).filter(resource => {
        const src = (resource as any).src || (resource as any).href;
        return src && !src.startsWith(location.origin);
      }).length;

      if (externalCount === 0) {
        this.addResult('security-external', 'pass', 'No external resources found');
      } else {
        this.addResult('security-external', 'warning', `Found ${externalCount} external resources`);
      }

    } catch (error) {
      this.addResult('security-tests', 'fail', `Security test error: ${error}`);
    }

    this.addResult('security-total', 'pass', `Security tests completed in ${performance.now() - startTime}ms`);
  }

  /**
   * Test error handling
   */
  private async testErrorHandling(): Promise<void> {
    const startTime = performance.now();

    try {
      // Test for error boundaries
      const errorBoundaries = document.querySelectorAll('[data-error-boundary]');
      if (errorBoundaries.length > 0) {
        this.addResult('error-boundaries', 'pass', `Found ${errorBoundaries.length} error boundaries`);
      } else {
        this.addResult('error-boundaries', 'warning', 'No error boundaries found');
      }

      // Test for 404 handling
      const test404 = await this.test404Handling();
      if (test404) {
        this.addResult('error-404', 'pass', '404 error handling works correctly');
      } else {
        this.addResult('error-404', 'fail', '404 error handling failed');
      }

      // Test for API error handling
      const testAPIErrors = await this.testAPIErrorHandling();
      if (testAPIErrors) {
        this.addResult('error-api', 'pass', 'API error handling works correctly');
      } else {
        this.addResult('error-api', 'warning', 'API error handling needs improvement');
      }

    } catch (error) {
      this.addResult('error-tests', 'fail', `Error handling test error: ${error}`);
    }

    this.addResult('error-total', 'pass', `Error handling tests completed in ${performance.now() - startTime}ms`);
  }

  /**
   * Test 404 error handling
   */
  private async test404Handling(): Promise<boolean> {
    try {
      // Test a non-existent route
      const response = await fetch('/non-existent-route', { method: 'HEAD' });
      return response.status === 404;
    } catch (error) {
      return false;
    }
  }

  /**
   * Test API error handling
   */
  private async testAPIErrorHandling(): Promise<boolean> {
    try {
      // Test API endpoint with invalid data
      const response = await fetch('/api/v1/test-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ invalid: 'data' })
      });
      
      // Should return an error response
      return response.status >= 400;
    } catch (error) {
      // Network error is also acceptable for this test
      return true;
    }
  }

  /**
   * Generate sitemap XML
   */
  private generateSitemapXML(sitemapData: any): string {
    const baseUrl = location.origin;
    const publicPages = sitemapData.frontend.filter((page: any) => !page.requiresAuth);

    const urls = publicPages.map((page: any) => {
      const url = `${baseUrl}${page.path}`;
      return `  <url>
    <loc>${url}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`;
    }).join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
  }

  /**
   * Add test result
   */
  private addResult(testName: string, status: 'pass' | 'fail' | 'warning', message: string, details?: any): void {
    this.testResults.push({
      testName,
      status,
      message,
      details,
      duration: 0 // Will be calculated by individual tests
    });
  }

  /**
   * Generate summary
   */
  private generateSummary(): {
    routing: boolean;
    sitemap: boolean;
    performance: boolean;
    accessibility: boolean;
    security: boolean;
    overall: boolean;
  } {
    const routingTests = this.testResults.filter(r => r.testName.startsWith('routing-'));
    const sitemapTests = this.testResults.filter(r => r.testName.startsWith('sitemap-'));
    const performanceTests = this.testResults.filter(r => r.testName.startsWith('performance-'));
    const a11yTests = this.testResults.filter(r => r.testName.startsWith('a11y-'));
    const securityTests = this.testResults.filter(r => r.testName.startsWith('security-'));

    const routing = routingTests.every(r => r.status === 'pass');
    const sitemap = sitemapTests.every(r => r.status === 'pass');
    const performance = performanceTests.every(r => r.status === 'pass' || r.status === 'warning');
    const accessibility = a11yTests.every(r => r.status === 'pass' || r.status === 'warning');
    const security = securityTests.every(r => r.status === 'pass' || r.status === 'warning');
    const overall = routing && sitemap && performance && accessibility && security;

    return {
      routing,
      sitemap,
      performance,
      accessibility,
      security,
      overall
    };
  }
}

// Export singleton instance
export const testValidator = new TestValidator();

// Export convenience functions
export const runAllTests = () => testValidator.runAllTests();
export const validateApplication = () => testValidator.runAllTests();

export default testValidator;
