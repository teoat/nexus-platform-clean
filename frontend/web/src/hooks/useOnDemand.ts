import { useState, useCallback } from "react";

export const useOnDemand = <T>(loader: () => Promise<T>, initialData?: T) => {
  const [data, setData] = useState<T | undefined>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const load = useCallback(async () => {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      const result = await loader();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setLoading(false);
    }
  }, [loader, loading]);

  const reload = useCallback(() => {
    setData(undefined);
    load();
  }, [load]);

  const clear = useCallback(() => {
    setData(undefined);
    setError(null);
  }, []);

  const loadFeature = useCallback(
    async (featureName: string) => {
      await load();
    },
    [load],
  );

  const saveFeature = useCallback(async (featureName: string, data: any) => {
    setData(data);
  }, []);

  return {
    data,
    loading,
    error,
    load,
    reload,
    clear,
    loadFeature,
    saveFeature,
  };
};
