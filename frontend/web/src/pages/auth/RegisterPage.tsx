import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import Button from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { CardContent, CardHeader } from "../../components/ui/Card";
import Card from "../../components/ui/Card";

const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long");
      setLoading(false);
      return;
    }

    try {
      await register(formData);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full space-y-8">
        <Card>
          <CardHeader>
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                Create your NEXUS account
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Join the financial management platform
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="First Name"
                  value={formData.firstName}
                  onChange={(value) =>
                    handleInputChange("firstName", value as string)
                  }
                  required
                  placeholder="John"
                />
                <Input
                  label="Last Name"
                  value={formData.lastName}
                  onChange={(value) =>
                    handleInputChange("lastName", value as string)
                  }
                  required
                  placeholder="Doe"
                />
              </div>

              <Input
                label="Username"
                type="text"
                value={formData.username}
                onChange={(value) =>
                  handleInputChange("username", value as string)
                }
                required
                placeholder="johndoe"
              />

              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={(value) =>
                  handleInputChange("email", value as string)
                }
                required
                placeholder="john@example.com"
              />

              <Input
                label="Password"
                type="password"
                value={formData.password}
                onChange={(value) =>
                  handleInputChange("password", value as string)
                }
                required
                placeholder="Enter your password"
              />

              <Input
                label="Confirm Password"
                type="password"
                value={formData.confirmPassword}
                onChange={(value) =>
                  handleInputChange("confirmPassword", value as string)
                }
                required
                placeholder="Confirm your password"
              />

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
                {loading ? "Creating Account..." : "Create Account"}
              </Button>

              <div className="text-center">
                <Link
                  to="/login"
                  className="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                >
                  Already have an account? Sign in
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;
