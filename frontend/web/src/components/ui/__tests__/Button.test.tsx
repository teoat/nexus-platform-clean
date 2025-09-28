#!/usr/bin/env typescript
/**
 * NEXUS Platform - Button Component Tests
 * Unit tests for the Button component
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import Button from "../Button";

describe("Button Component", () => {
  it("renders with default props", () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole("button", { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass("bg-blue-600");
  });

  it("renders with different variants", () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-blue-600");

    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-gray-600");

    rerender(<Button variant="outlined">Outline</Button>);
    expect(screen.getByRole("button")).toHaveClass("border-gray-300");

    rerender(<Button variant="text">Ghost</Button>);
    expect(screen.getByRole("button")).toHaveClass("bg-transparent");
  });

  it("renders with different sizes", () => {
    const { rerender } = render(<Button size="small">Small</Button>);
    expect(screen.getByRole("button")).toHaveClass("px-3 py-1.5 text-sm");

    rerender(<Button size="medium">Medium</Button>);
    expect(screen.getByRole("button")).toHaveClass("px-4 py-2 text-base");

    rerender(<Button size="large">Large</Button>);
    expect(screen.getByRole("button")).toHaveClass("px-6 py-3 text-lg");
  });

  it("handles click events", () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("can be disabled", () => {
    const handleClick = jest.fn();
    render(
      <Button disabled onClick={handleClick}>
        Disabled
      </Button>,
    );

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveClass("opacity-50", "cursor-not-allowed");

    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("shows loading state", () => {
    render(<Button loading>Loading</Button>);
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button).toHaveClass("opacity-50");
  });

  it("renders with custom className", () => {
    render(<Button className="custom-class">Custom</Button>);
    expect(screen.getByRole("button")).toHaveClass("custom-class");
  });

  it("renders with custom props", () => {
    render(
      <Button data-testid="custom-button" aria-label="Custom button">
        Custom
      </Button>,
    );
    expect(screen.getByTestId("custom-button")).toBeInTheDocument();
    expect(screen.getByLabelText("Custom button")).toBeInTheDocument();
  });

  it("forwards ref correctly", () => {
    const ref = React.createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Ref test</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });
});
