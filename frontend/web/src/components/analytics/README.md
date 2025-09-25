# Analytics Configuration

This directory contains analytics-related components and configuration for the NEXUS platform.

## Google Analytics Setup

To enable Google Analytics tracking:

1. Create a Google Analytics 4 property at https://analytics.google.com/
2. Get your Measurement ID (format: G-XXXXXXXXXX)
3. Set the environment variable:
   ```
   REACT_APP_GA_MEASUREMENT_ID=G-XXXXXXXXXX
   ```
4. Or update the default in `config/analytics.ts`

## Configuration Options

- **Google Analytics**: Primary analytics tracking
- **Custom Analytics**: Optional custom endpoint for additional tracking
- **Privacy Settings**: Respect Do Not Track, anonymize IP
- **Event Tracking**: Page views, clicks, form submissions, errors, performance

## Usage

```typescript
import { defaultAnalyticsConfig } from '../config/analytics';

// Use the config in your analytics service
```

## Components

- `AnalyticsDashboard.tsx`: Main analytics dashboard component