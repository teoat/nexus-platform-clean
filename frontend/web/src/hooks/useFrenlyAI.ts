import { useState, useCallback } from "react";

export interface FrenlyAIResponse {
  message: string;
  confidence: number;
  suggestions?: string[];
}

export const useFrenlyAI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askQuestion = useCallback(
    async (question: string): Promise<FrenlyAIResponse | null> => {
      setIsLoading(true);
      setError(null);

      try {
        // Simulate AI response
        await new Promise((resolve) => setTimeout(resolve, 1000));

        const response: FrenlyAIResponse = {
          message: `AI Response to: ${question}`,
          confidence: Math.random() * 100,
          suggestions: ["Suggestion 1", "Suggestion 2"],
        };

        return response;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    askQuestion,
    clearError,
  };
};
