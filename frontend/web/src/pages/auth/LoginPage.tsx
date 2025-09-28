import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Button from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { CardContent, CardHeader } from "../../components/ui/Card";
import Card from "../../components/ui/Card";

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8">
        <Card>
          <CardHeader>
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Sign in to NEXUS Platform
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Enter your credentials to access your account
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-4">
                <Input
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(value) => setEmail(value as string)}
                  required
                  placeholder="Enter your email"
                />
                <Input
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(value) => setPassword(value as string)}
                  required
                  placeholder="Enter your password"
                />
              </div>

              {error && (
                <div className="text-red-600 text-sm text-center bg-red-50 dark:bg-red-900/20 p-3 rounded-md">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                loading={loading}
                className="w-full"
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign In"}
              </Button>

              <div className="text-center">
                <Link
                  to="/register"
                  className="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                >
                  Don&apos;t have an account? Sign up
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="text-center text-xs text-gray-500 dark:text-gray-400">
          <p>Demo credentials:</p>
          <p>Email: admin@nexus.com, Password: secret</p>
          <p>Email: user1@nexus.com, Password: secret</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
