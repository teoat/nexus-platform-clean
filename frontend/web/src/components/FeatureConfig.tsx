import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, Typography } from "@mui/material";
import { useOnDemand } from "../hooks/useOnDemand";

interface FeatureConfigProps {
  // Add props here
}

interface FeatureConfiguration {
  enabled: boolean;
  settings: Record<string, any>;
}

const FeatureConfig: React.FC<FeatureConfigProps> = () => {
  const [config] = useState<FeatureConfiguration>({
    enabled: false,
    settings: {},
  });
  const { loadFeature, saveFeature } = useOnDemand(async () => {
    // Mock feature loading
    return { enabled: false, settings: {} };
  });

  const loadFeatureConfig = useCallback(async () => {
    try {
      console.log("Loading feature configuration...");
      await loadFeature("featureConfig");
      // Configuration will be available in the data property from useOnDemand
    } catch (error) {
      console.error("Failed to load feature config:", error);
    }
  }, [loadFeature]);

  useEffect(() => {
    loadFeatureConfig();
  }, [loadFeatureConfig]);

  const saveFeatureConfig = async () => {
    try {
      console.log("Saving feature configuration...");
      await saveFeature("featureConfig", config);
    } catch (error) {
      console.error("Failed to save feature config:", error);
    }
  };

  return (
    <div className="featureconfig">
      <h2>Feature Configuration</h2>
      <Card>
        <CardContent>
          <Typography variant="h6">Feature Settings</Typography>
          <button onClick={loadFeatureConfig}>Load Config</button>
          <button onClick={saveFeatureConfig}>Save Config</button>
          <pre>{JSON.stringify(config, null, 2)}</pre>
        </CardContent>
      </Card>
    </div>
  );
};

export default FeatureConfig;
