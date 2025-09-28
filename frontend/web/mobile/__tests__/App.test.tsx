/**
 * Mobile App Tests
 * Basic tests for React Native/Expo app
 */

import React from "react";
import { render } from "@testing-library/react-native";
import App from "../app/index";

// Mock Expo modules
jest.mock("expo-router", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  useLocalSearchParams: () => ({}),
}));

jest.mock("expo-splash-screen", () => ({
  hideAsync: jest.fn(),
  preventAutoHideAsync: jest.fn(),
}));

describe("Mobile App", () => {
  it("renders without crashing", () => {
    const { getByTestId } = render(<App />);
    expect(getByTestId).toBeDefined();
  });
});
