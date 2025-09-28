import { useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";

export const useNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const goTo = useCallback(
    (path: string) => {
      navigate(path);
    },
    [navigate],
  );

  const goBack = useCallback(() => {
    navigate(-1);
  }, [navigate]);

  const goForward = useCallback(() => {
    navigate(1);
  }, [navigate]);

  const replace = useCallback(
    (path: string) => {
      navigate(path, { replace: true });
    },
    [navigate],
  );

  const isActive = useCallback(
    (path: string) => {
      return location.pathname === path;
    },
    [location.pathname],
  );

  return {
    goTo,
    goBack,
    goForward,
    replace,
    isActive,
    currentPath: location.pathname,
  };
};
