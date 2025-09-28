/**
 * NEXUS Platform - Sitemap Generator
 * Auto-generates sitemap.json and sitemap.xml from routing registry
 */

import { FRONTEND_ROUTES, API_ROUTES, generateSitemap, generateSitemapXML } from '../config/routingRegistry';

export interface SitemapEntry {
  id: string;
  path: string;
  title: string;
  description: string;
  category: string;
  requiresAuth: boolean;
  lastModified: string;
  changeFrequency: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  priority: number;
  features?: string[];
  metadata?: {
    seo?: {
      title?: string;
      description?: string;
      keywords?: string[];
    };
    permissions?: string[];
    roles?: string[];
  };
}

export interface SitemapData {
  frontend: SitemapEntry[];
  api: {
    id: string;
    path: string;
    method: string;
    title: string;
    description: string;
    category: string;
    requiresAuth: boolean;
  }[];
  generatedAt: string;
  version: string;
  totalPages: number;
  totalAPIs: number;
}

class SitemapGenerator {
  private baseUrl: string;
  private version: string;

  constructor(baseUrl: string = process.env.REACT_APP_BASE_URL || 'https://nexus-platform.com') {
    this.baseUrl = baseUrl;
    this.version = '2.1.0';
  }

  /**
   * Generate complete sitemap data
   */
  generateSitemapData(): SitemapData {
    const frontendEntries = this.generateFrontendEntries();
    const apiEntries = this.generateAPIEntries();

    return {
      frontend: frontendEntries,
      api: apiEntries,
      generatedAt: new Date().toISOString(),
      version: this.version,
      totalPages: frontendEntries.length,
      totalAPIs: apiEntries.length
    };
  }

  /**
   * Generate frontend sitemap entries
   */
  private generateFrontendEntries(): SitemapEntry[] {
    return FRONTEND_ROUTES.map(route => ({
      id: route.id,
      path: route.path,
      title: route.title,
      description: route.description,
      category: route.category,
      requiresAuth: route.requiresAuth,
      lastModified: new Date().toISOString(),
      changeFrequency: this.getChangeFrequency(route.category),
      priority: this.getPriority(route.category, route.requiresAuth),
      features: route.features,
      metadata: route.metadata
    }));
  }

  /**
   * Generate API sitemap entries
   */
  private generateAPIEntries() {
    return API_ROUTES.map(route => ({
      id: route.id,
      path: route.path,
      method: route.method,
      title: route.title,
      description: route.description,
      category: route.category,
      requiresAuth: route.requiresAuth
    }));
  }

  /**
   * Generate sitemap.json
   */
  generateSitemapJSON(): string {
    const sitemapData = this.generateSitemapData();
    return JSON.stringify(sitemapData, null, 2);
  }

  /**
   * Generate sitemap.xml
   */
  generateSitemapXML(): string {
    const sitemapData = this.generateSitemapData();
    const publicPages = sitemapData.frontend.filter(page => !page.requiresAuth);

    const urls = publicPages.map(page => {
      const url = `${this.baseUrl}${page.path}`;
      const lastMod = new Date(page.lastModified).toISOString().split('T')[0];
      
      return `  <url>
    <loc>${url}</loc>
    <lastmod>${lastMod}</lastmod>
    <changefreq>${page.changeFrequency}</changefreq>
    <priority>${page.priority}</priority>
  </url>`;
    }).join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;
  }

  /**
   * Generate navigation map for agents and UI
   */
  generateNavigationMap(): any {
    const sitemapData = this.generateSitemapData();
    
    // Group by category
    const navigationMap = sitemapData.frontend.reduce((acc, page) => {
      if (!acc[page.category]) {
        acc[page.category] = [];
      }
      acc[page.category].push({
        id: page.id,
        path: page.path,
        title: page.title,
        description: page.description,
        requiresAuth: page.requiresAuth,
        features: page.features
      });
      return acc;
    }, {} as Record<string, any[]>);

    return {
      categories: navigationMap,
      totalPages: sitemapData.totalPages,
      generatedAt: sitemapData.generatedAt,
      version: sitemapData.version
    };
  }

  /**
   * Generate API documentation map
   */
  generateAPIDocumentationMap(): any {
    const sitemapData = this.generateSitemapData();
    
    // Group APIs by category
    const apiMap = sitemapData.api.reduce((acc, api) => {
      if (!acc[api.category]) {
        acc[api.category] = [];
      }
      acc[api.category].push({
        id: api.id,
        path: api.path,
        method: api.method,
        title: api.title,
        description: api.description,
        requiresAuth: api.requiresAuth
      });
      return acc;
    }, {} as Record<string, any[]>);

    return {
      categories: apiMap,
      totalAPIs: sitemapData.totalAPIs,
      generatedAt: sitemapData.generatedAt,
      version: sitemapData.version
    };
  }

  /**
   * Validate sitemap for broken links
   */
  async validateSitemap(): Promise<{
    valid: boolean;
    brokenLinks: string[];
    warnings: string[];
  }> {
    const sitemapData = this.generateSitemapData();
    const brokenLinks: string[] = [];
    const warnings: string[] = [];

    // Check for duplicate paths
    const paths = sitemapData.frontend.map(page => page.path);
    const duplicatePaths = paths.filter((path, index) => paths.indexOf(path) !== index);
    
    if (duplicatePaths.length > 0) {
      warnings.push(`Duplicate paths found: ${duplicatePaths.join(', ')}`);
    }

    // Check for missing required fields
    sitemapData.frontend.forEach(page => {
      if (!page.title) {
        warnings.push(`Missing title for path: ${page.path}`);
      }
      if (!page.description) {
        warnings.push(`Missing description for path: ${page.path}`);
      }
    });

    // Check for circular references (simplified check)
    const circularRefs = this.checkCircularReferences(sitemapData.frontend);
    if (circularRefs.length > 0) {
      warnings.push(`Potential circular references: ${circularRefs.join(', ')}`);
    }

    return {
      valid: warnings.length === 0 && brokenLinks.length === 0,
      brokenLinks,
      warnings
    };
  }

  /**
   * Check for circular references in routes
   */
  private checkCircularReferences(pages: SitemapEntry[]): string[] {
    const circularRefs: string[] = [];
    
    // Simple check for obvious circular references
    pages.forEach(page => {
      if (page.path.includes('//') || page.path.endsWith('/') && page.path.length > 1) {
        circularRefs.push(page.path);
      }
    });

    return circularRefs;
  }

  /**
   * Get change frequency based on category
   */
  private getChangeFrequency(category: string): 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never' {
    switch (category) {
      case 'main':
        return 'daily';
      case 'financial':
        return 'daily';
      case 'analytics':
        return 'hourly';
      case 'admin':
        return 'weekly';
      case 'user':
        return 'weekly';
      case 'auth':
        return 'monthly';
      case 'system':
        return 'daily';
      case 'forensic':
        return 'daily';
      default:
        return 'weekly';
    }
  }

  /**
   * Get priority based on category and auth requirement
   */
  private getPriority(category: string, requiresAuth: boolean): number {
    let basePriority = 0.5;

    // Adjust based on category
    switch (category) {
      case 'main':
        basePriority = 1.0;
        break;
      case 'financial':
        basePriority = 0.9;
        break;
      case 'analytics':
        basePriority = 0.8;
        break;
      case 'forensic':
        basePriority = 0.9;
        break;
      case 'admin':
        basePriority = 0.3;
        break;
      case 'user':
        basePriority = 0.6;
        break;
      case 'auth':
        basePriority = 0.7;
        break;
      case 'system':
        basePriority = 0.4;
        break;
      default:
        basePriority = 0.5;
    }

    // Reduce priority for auth-required pages (SEO consideration)
    if (requiresAuth) {
      basePriority *= 0.8;
    }

    return Math.round(basePriority * 10) / 10; // Round to 1 decimal place
  }

  /**
   * Generate robots.txt content
   */
  generateRobotsTxt(): string {
    const sitemapUrl = `${this.baseUrl}/sitemap.xml`;
    
    return `User-agent: *
Allow: /

# Sitemap
Sitemap: ${sitemapUrl}

# Disallow admin and system pages
Disallow: /admin/
Disallow: /api/
Disallow: /ssot/
Disallow: /monitoring/
Disallow: /audit-logs/

# Allow public pages
Allow: /dashboard
Allow: /accounts
Allow: /transactions
Allow: /analytics
Allow: /reports
Allow: /login
Allow: /register`;
  }

  /**
   * Generate human-readable sitemap documentation
   */
  generateSitemapDocumentation(): string {
    const sitemapData = this.generateSitemapData();
    
    let doc = `# NEXUS Platform Sitemap Documentation\n\n`;
    doc += `Generated: ${sitemapData.generatedAt}\n`;
    doc += `Version: ${sitemapData.version}\n`;
    doc += `Total Pages: ${sitemapData.totalPages}\n`;
    doc += `Total APIs: ${sitemapData.totalAPIs}\n\n`;

    // Group by category
    const categories = sitemapData.frontend.reduce((acc, page) => {
      if (!acc[page.category]) {
        acc[page.category] = [];
      }
      acc[page.category].push(page);
      return acc;
    }, {} as Record<string, SitemapEntry[]>);

    Object.entries(categories).forEach(([category, pages]) => {
      doc += `## ${category.charAt(0).toUpperCase() + category.slice(1)} Pages\n\n`;
      
      pages.forEach(page => {
        doc += `### ${page.title}\n`;
        doc += `- **Path:** \`${page.path}\`\n`;
        doc += `- **Description:** ${page.description}\n`;
        doc += `- **Requires Auth:** ${page.requiresAuth ? 'Yes' : 'No'}\n`;
        doc += `- **Priority:** ${page.priority}\n`;
        doc += `- **Change Frequency:** ${page.changeFrequency}\n`;
        
        if (page.features && page.features.length > 0) {
          doc += `- **Features:**\n`;
          page.features.forEach(feature => {
            doc += `  - ${feature}\n`;
          });
        }
        
        doc += `\n`;
      });
    });

    return doc;
  }

  /**
   * Export all sitemap files
   */
  async exportSitemapFiles(): Promise<{
    sitemapJson: string;
    sitemapXml: string;
    navigationMap: any;
    apiDocumentation: any;
    robotsTxt: string;
    documentation: string;
  }> {
    return {
      sitemapJson: this.generateSitemapJSON(),
      sitemapXml: this.generateSitemapXML(),
      navigationMap: this.generateNavigationMap(),
      apiDocumentation: this.generateAPIDocumentationMap(),
      robotsTxt: this.generateRobotsTxt(),
      documentation: this.generateSitemapDocumentation()
    };
  }
}

// Export singleton instance
export const sitemapGenerator = new SitemapGenerator();

// Export convenience functions
export const generateSitemapFiles = () => sitemapGenerator.exportSitemapFiles();
export const validateSitemap = () => sitemapGenerator.validateSitemap();
export const getNavigationMap = () => sitemapGenerator.generateNavigationMap();
export const getAPIDocumentation = () => sitemapGenerator.generateAPIDocumentationMap();

export default sitemapGenerator;
