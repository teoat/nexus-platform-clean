module.exports = {
  budgets: {
    bundleSize: { maxSize: "250kb", maxGzippedSize: "75kb" },
    chunks: {
      main: { maxSize: "150kb", maxGzippedSize: "45kb" },
      vendor: { maxSize: "200kb", maxGzippedSize: "60kb" },
      common: { maxSize: "50kb", maxGzippedSize: "15kb" },
    },
    assets: {
      images: { maxSize: "100kb", maxGzippedSize: "30kb" },
      fonts: { maxSize: "50kb", maxGzippedSize: "15kb" },
      css: { maxSize: "30kb", maxGzippedSize: "10kb" },
    },
    performance: {
      firstContentfulPaint: "1.8s",
      largestContentfulPaint: "2.5s",
      firstInputDelay: "100ms",
      cumulativeLayoutShift: "0.1",
      timeToInteractive: "3.8s",
    },
  },
  webVitals: {
    CLS: { good: 0.1, needsImprovement: 0.25 },
    FID: { good: 100, needsImprovement: 300 },
    FCP: { good: 1800, needsImprovement: 3000 },
    LCP: { good: 2500, needsImprovement: 4000 },
    TTFB: { good: 800, needsImprovement: 1800 },
    INP: { good: 200, needsImprovement: 500 },
  },
  lighthouse: {
    performance: 90,
    accessibility: 90,
    bestPractices: 90,
    seo: 90,
  },
};
