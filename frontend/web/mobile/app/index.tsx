import React, { useEffect } from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function Index() {
  const router = useRouter();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const authData = await AsyncStorage.getItem("auth-storage");
      if (authData) {
        const parsed = JSON.parse(authData);
        if (parsed.state?.isAuthenticated) {
          router.replace("/(tabs)");
          return;
        }
      }
      router.replace("/(auth)/login");
    } catch (error) {
      console.error("Error checking auth status:", error);
      router.replace("/(auth)/login");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>NEXUS Platform</Text>
      <ActivityIndicator size="large" color="#1976d2" style={styles.loader} />
      <Text style={styles.subtitle}>Loading...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#1976d2",
    marginBottom: 20,
  },
  subtitle: {
    fontSize: 16,
    color: "#666",
    marginTop: 10,
  },
  loader: {
    marginVertical: 20,
  },
});
