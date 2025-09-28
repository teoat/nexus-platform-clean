import { useCallback } from "react";
import { handleError, handleApiError, ErrorType } from "../utils/errorHandler";

export const useErrorHandler = () => {
  const handleErrorCallback = useCallback(
    (error: any, type: ErrorType = ErrorType.UNKNOWN) => {
      return handleError(error, type);
    },
    [],
  );

  const handleApiErrorCallback = useCallback((error: any) => {
    return handleApiError(error);
  }, []);

  return {
    handleError: handleErrorCallback,
    handleApiError: handleApiErrorCallback,
  };
};
