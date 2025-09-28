# NEXUS Platform Design System Guide

## Overview

The NEXUS Platform Design System provides a comprehensive set of reusable UI components built with TypeScript, styled-components, and accessibility best practices. This guide covers component usage, theming, and development patterns.

## Design Principles

### 1. Accessibility First

- All components meet WCAG 2.1 AA standards
- Keyboard navigation support
- Screen reader compatibility
- High contrast support

### 2. Consistency

- Unified design language across all components
- Consistent spacing, typography, and color usage
- Standardized interaction patterns

### 3. Performance

- Lazy loading for heavy components
- Optimized re-renders with React.memo
- Minimal bundle size impact

### 4. Type Safety

- Full TypeScript support
- Strict type checking
- IntelliSense support in IDEs

## Component Categories

### Form Components

#### Button

Primary action component with multiple variants and sizes.

```tsx
import { Button } from '@nexus/design-system';

// Basic usage
<Button onClick={handleClick}>Click me</Button>

// Variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="success">Success</Button>
<Button variant="warning">Warning</Button>
<Button variant="error">Error</Button>
<Button variant="ghost">Ghost</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// States
<Button loading>Loading...</Button>
<Button disabled>Disabled</Button>
<Button fullWidth>Full Width</Button>
```

**Props:**

- `variant`: `'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'ghost'`
- `size`: `'sm' | 'md' | 'lg'`
- `loading`: `boolean`
- `fullWidth`: `boolean`
- `children`: `ReactNode`

#### Input

Text input component with validation and accessibility features.

```tsx
import { Input } from '@nexus/design-system';

// Basic usage
<Input placeholder="Enter your name" />

// With label and validation
<Input
  label="Email Address"
  type="email"
  helperText="We'll never share your email"
  error={hasError}
  fullWidth
/>

// Controlled input
const [value, setValue] = useState('');
<Input
  value={value}
  onChange={(e) => setValue(e.target.value)}
  label="Username"
/>
```

**Props:**

- `size`: `'sm' | 'md' | 'lg'`
- `error`: `boolean`
- `fullWidth`: `boolean`
- `label`: `string`
- `helperText`: `string`
- `type`: `string`

#### Select

Dropdown selection component with search and multi-select support.

```tsx
import { Select } from "@nexus/design-system";

const options = [
  { value: "checking", label: "Checking Account" },
  { value: "savings", label: "Savings Account" },
  { value: "credit", label: "Credit Card" },
];

<Select
  label="Account Type"
  options={options}
  value={selectedValue}
  onChange={setSelectedValue}
  fullWidth
/>;
```

**Props:**

- `options`: `SelectOption[]`
- `size`: `'sm' | 'md' | 'lg'`
- `error`: `boolean`
- `fullWidth`: `boolean`
- `label`: `string`
- `helperText`: `string`

#### Textarea

Multi-line text input with auto-resize.

```tsx
import { Textarea } from "@nexus/design-system";

<Textarea
  label="Description"
  placeholder="Enter a detailed description..."
  rows={4}
  resize="vertical"
  fullWidth
/>;
```

**Props:**

- `size`: `'sm' | 'md' | 'lg'`
- `error`: `boolean`
- `fullWidth`: `boolean`
- `label`: `string`
- `helperText`: `string`
- `resize`: `'none' | 'vertical' | 'horizontal' | 'both'`

#### Checkbox

Boolean input with custom styling.

```tsx
import { Checkbox } from "@nexus/design-system";

<Checkbox
  label="I agree to the terms and conditions"
  checked={agreed}
  onChange={(e) => setAgreed(e.target.checked)}
  error={!agreed && showError}
/>;
```

#### Radio

Single selection from multiple options.

```tsx
import { Radio } from "@nexus/design-system";

<Radio
  label="Option 1"
  name="options"
  value="option1"
  checked={selected === "option1"}
  onChange={(e) => setSelected(e.target.value)}
/>;
```

#### Switch

Toggle switch for boolean values.

```tsx
import { Switch } from "@nexus/design-system";

<Switch
  label="Enable notifications"
  checked={notificationsEnabled}
  onChange={(e) => setNotificationsEnabled(e.target.checked)}
/>;
```

### Layout Components

#### Card

Container component for grouping related content.

```tsx
import { Card } from "@nexus/design-system";

<Card variant="elevated" padding="md">
  <h3>Card Title</h3>
  <p>Card content goes here...</p>
</Card>;
```

**Props:**

- `variant`: `'default' | 'elevated' | 'outlined'`
- `padding`: `'none' | 'sm' | 'md' | 'lg'`

#### Modal

Overlay dialog for focused interactions.

```tsx
import { Modal, Button } from "@nexus/design-system";

<Modal
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
  size="md"
>
  <p>Are you sure you want to proceed?</p>
  <div style={{ display: "flex", gap: "1rem", justifyContent: "flex-end" }}>
    <Button variant="secondary" onClick={() => setIsOpen(false)}>
      Cancel
    </Button>
    <Button onClick={handleConfirm}>Confirm</Button>
  </div>
</Modal>;
```

**Props:**

- `isOpen`: `boolean`
- `onClose`: `() => void`
- `title`: `string`
- `size`: `'sm' | 'md' | 'lg' | 'xl'`
- `showCloseButton`: `boolean`

### Data Display Components

#### Table

Data table with sorting, pagination, and accessibility.

```tsx
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableHeader,
  TableCell,
} from "@nexus/design-system";

<Table>
  <TableHead>
    <TableRow>
      <TableHeader>Name</TableHeader>
      <TableHeader>Email</TableHeader>
      <TableHeader>Status</TableHeader>
    </TableRow>
  </TableHead>
  <TableBody>
    {data.map((item) => (
      <TableRow key={item.id}>
        <TableCell>{item.name}</TableCell>
        <TableCell>{item.email}</TableCell>
        <TableCell>{item.status}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>;
```

#### Badge

Status indicator and labeling component.

```tsx
import { Badge } from '@nexus/design-system';

<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Failed</Badge>
```

**Props:**

- `variant`: `'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'`
- `size`: `'sm' | 'md'`

#### Alert

Notification and feedback messages.

```tsx
import { Alert } from '@nexus/design-system';

<Alert variant="success" title="Success!">
  Your changes have been saved successfully.
</Alert>

<Alert variant="error" dismissible onDismiss={() => setShowError(false)}>
  An error occurred while processing your request.
</Alert>
```

**Props:**

- `variant`: `'success' | 'warning' | 'error' | 'info'`
- `size`: `'sm' | 'md'`
- `title`: `string`
- `dismissible`: `boolean`
- `onDismiss`: `() => void`

#### Spinner

Loading indicator with multiple sizes.

```tsx
import { Spinner } from "@nexus/design-system";

<Spinner size="md" />;
```

**Props:**

- `size`: `'sm' | 'md' | 'lg'`
- `color`: `string`

#### Tooltip

Contextual help and information.

```tsx
import { Tooltip } from "@nexus/design-system";

<Tooltip content="This is a helpful tooltip message">
  <Button>Hover me</Button>
</Tooltip>;
```

**Props:**

- `content`: `string`
- `position`: `'top' | 'bottom' | 'left' | 'right'`
- `delay`: `number`

## Theming

### CSS Custom Properties

The design system uses CSS custom properties for theming:

```css
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-error: #dc3545;
  --color-info: #17a2b8;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 3rem;

  /* Typography */
  --font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;

  /* Font weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Border radius */
  --border-radius-sm: 0.125rem;
  --border-radius-md: 0.25rem;
  --border-radius-lg: 0.5rem;
  --border-radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

### Dark Mode Support

The design system supports automatic dark mode:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #1a1a1a;
    --color-text-primary: #ffffff;
    --color-text-secondary: #cccccc;
    --color-border: #333333;
  }
}
```

## Accessibility Guidelines

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Tab order follows logical reading order
- Enter/Space activate buttons
- Arrow keys navigate select options and menus

### Screen Reader Support

- Semantic HTML elements used appropriately
- ARIA labels and descriptions provided
- Focus management in modals and overlays
- Live regions for dynamic content updates

### Color Contrast

- All text meets WCAG AA contrast ratios
- Focus indicators are clearly visible
- Error states use high-contrast colors

### Motion Preferences

- Respects `prefers-reduced-motion` setting
- Animations can be disabled for accessibility

## Development Workflow

### Component Creation

1. Create component in `nexus_backend/design-system/components/`
2. Add TypeScript types
3. Implement accessibility features
4. Add unit tests
5. Update component index
6. Add Storybook stories

### Testing

```tsx
// Component test example
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "./Button";

describe("Button", () => {
  it("renders with correct text", () => {
    render(<Button>Click me</Button>);
    expect(
      screen.getByRole("button", { name: /click me/i }),
    ).toBeInTheDocument();
  });

  it("handles click events", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Storybook Integration

```tsx
// Button.stories.tsx
import { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta: Meta<typeof Button> = {
  title: "Components/Button",
  component: Button,
  parameters: {
    docs: {
      description: {
        component: "Primary action component with multiple variants.",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: "Primary Button",
    variant: "primary",
  },
};

export const Secondary: Story = {
  args: {
    children: "Secondary Button",
    variant: "secondary",
  },
};
```

## Performance Considerations

### Bundle Size

- Components are tree-shakeable
- Dynamic imports for heavy components
- Minimal dependencies

### Rendering Optimization

- React.memo for expensive components
- useCallback for event handlers
- useMemo for computed values

### Accessibility Performance

- Reduced motion respected
- Focus management optimized
- Screen reader announcements batched

## Migration Guide

### From Legacy Components

```tsx
// Before
<button className="btn btn-primary">Click me</button>;

// After
import { Button } from "@nexus/design-system";
<Button variant="primary">Click me</Button>;
```

### Breaking Changes

- Props API changes for consistency
- Required accessibility attributes
- TypeScript strict mode enabled

## Support

For design system questions and contributions:

- 📖 [Design System Documentation](./README.md)
- 🐛 [Report Issues](https://github.com/nexus-platform/design-system/issues)
- 💬 [Discussions](https://github.com/nexus-platform/design-system/discussions)
