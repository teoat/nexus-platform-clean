import React, { memo, useState, useCallback } from "react";
import {
  CardHeader,
  CardContent,
  Button,
  Input,
  Select,
  Textarea,
} from "@/components/ui";
import Card from "@/components/ui/Card";
import { useTranslationHook } from "../../contexts/I18nContext";
import {
  USER_ROLES,
  DEPARTMENTS,
  LANGUAGE_CODES,
  TIMEZONE_CODES,
  CURRENCY_CODES,
} from "../../constants";

interface Option {
  value: string;
  label: string;
}

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  department: string;
  phone?: string;
  avatar?: string;
  bio?: string;
  preferences: {
    language: string;
    timezone: string;
    dateFormat: string;
    currency: string;
    theme: "light" | "dark" | "system";
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
    };
  };
  security: {
    twoFactorEnabled: boolean;
    lastLogin: string;
    loginAttempts: number;
  };
}

interface UserProfileProps {
  user?: User;
  onSave?: (userData: Partial<User>) => void;
  onChangePassword?: (currentPassword: string, newPassword: string) => void;
  onEnable2FA?: () => void;
  onDisable2FA?: () => void;
  loading?: boolean;
  className?: string;
}

const DEFAULT_USER: User = {
  id: "1",
  email: "john.doe@company.com",
  firstName: "John",
  lastName: "Doe",
  role: USER_ROLES.MANAGER,
  department: DEPARTMENTS.FINANCE,
  phone: "+1 (555) 123-4567",
  bio: "Experienced finance manager with 8+ years in financial planning and analysis.",
  preferences: {
    language: LANGUAGE_CODES.EN,
    timezone: TIMEZONE_CODES.AMERICA_NEW_YORK,
    dateFormat: "MM/dd/yyyy",
    currency: CURRENCY_CODES.USD,
    theme: "system",
    notifications: {
      email: true,
      push: true,
      sms: false,
    },
  },
  security: {
    twoFactorEnabled: false,
    lastLogin: "2024-01-20T14:30:00Z",
    loginAttempts: 0,
  },
};

const ROLES: Option[] = [
  { value: USER_ROLES.ADMIN, label: "Administrator" },
  { value: USER_ROLES.MANAGER, label: "Manager" },
  { value: USER_ROLES.USER, label: "User" },
  { value: USER_ROLES.VIEWER, label: "Viewer" },
];

const DEPARTMENT_OPTIONS: Option[] = Object.values(DEPARTMENTS).map(
  (dept: string) => ({
    value: dept,
    label: dept,
  }),
);

const LANGUAGES: Option[] = [
  { value: LANGUAGE_CODES.EN, label: "English" },
  { value: LANGUAGE_CODES.ES, label: "Spanish" },
  { value: LANGUAGE_CODES.FR, label: "French" },
  { value: LANGUAGE_CODES.DE, label: "German" },
  { value: LANGUAGE_CODES.ZH, label: "Chinese" },
];

const TIMEZONES: Option[] = [
  { value: TIMEZONE_CODES.AMERICA_NEW_YORK, label: "Eastern Time (ET)" },
  { value: TIMEZONE_CODES.AMERICA_CHICAGO, label: "Central Time (CT)" },
  { value: TIMEZONE_CODES.AMERICA_DENVER, label: "Mountain Time (MT)" },
  { value: TIMEZONE_CODES.AMERICA_LOS_ANGELES, label: "Pacific Time (PT)" },
  { value: TIMEZONE_CODES.EUROPE_LONDON, label: "Greenwich Mean Time (GMT)" },
  { value: TIMEZONE_CODES.EUROPE_PARIS, label: "Central European Time (CET)" },
  { value: TIMEZONE_CODES.ASIA_TOKYO, label: "Japan Standard Time (JST)" },
];

const CURRENCIES: Option[] = [
  { value: CURRENCY_CODES.USD, label: "US Dollar (USD)" },
  { value: CURRENCY_CODES.EUR, label: "Euro (EUR)" },
  { value: CURRENCY_CODES.GBP, label: "British Pound (GBP)" },
  { value: CURRENCY_CODES.JPY, label: "Japanese Yen (JPY)" },
  { value: CURRENCY_CODES.CAD, label: "Canadian Dollar (CAD)" },
  { value: CURRENCY_CODES.AUD, label: "Australian Dollar (AUD)" },
];

const UserProfile: React.FC<UserProfileProps> = memo(
  ({
    user = DEFAULT_USER,
    onSave,
    onChangePassword,
    onEnable2FA,
    onDisable2FA,
    loading = false,
    className = "",
  }) => {
    const { t } = useTranslationHook();
    const formatDate = (date: Date, options?: Intl.DateTimeFormatOptions) =>
      new Intl.DateTimeFormat("en-US", options).format(date);
    const [activeTab, setActiveTab] = useState<
      "profile" | "preferences" | "security"
    >("profile");
    const [formData, setFormData] = useState<Partial<User>>(user);
    const [showPasswordForm, setShowPasswordForm] = useState(false);
    const [passwordData, setPasswordData] = useState({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });

    // Handle form input changes
    const handleInputChange = useCallback((field: keyof User, value: any) => {
      setFormData((prev) => ({ ...prev, [field]: value }));
    }, []);

    const handlePreferenceChange = useCallback((field: string, value: any) => {
      setFormData((prev) => ({
        ...prev,
        preferences: {
          ...prev.preferences!,
          [field]: value,
        },
      }));
    }, []);

    const handleNotificationChange = useCallback(
      (type: string, enabled: boolean) => {
        setFormData((prev) => ({
          ...prev,
          preferences: {
            ...prev.preferences!,
            notifications: {
              ...prev.preferences!.notifications,
              [type]: enabled,
            },
          },
        }));
      },
      [],
    );

    // Handle save
    const handleSave = useCallback(() => {
      onSave?.(formData);
    }, [formData, onSave]);

    // Handle password change
    const handlePasswordChange = useCallback(() => {
      if (passwordData.newPassword !== passwordData.confirmPassword) {
        alert("New passwords do not match");
        return;
      }

      onChangePassword?.(
        passwordData.currentPassword,
        passwordData.newPassword,
      );
      setShowPasswordForm(false);
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    }, [passwordData, onChangePassword]);

    // Get role badge variant
    const getRoleBadgeVariant = useCallback((role: User["role"]) => {
      switch (role) {
        case USER_ROLES.ADMIN:
          return "error";
        case USER_ROLES.MANAGER:
          return "warning";
        case USER_ROLES.USER:
          return "info";
        case USER_ROLES.VIEWER:
          return "secondary";
        default:
          return "secondary";
      }
    }, []);

    if (loading) {
      return (
        <div className="space-y-6">
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="h-64 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="h-64 bg-gray-200 rounded animate-pulse"></div>
          </div>
        </div>
      );
    }

    return (
      <div className={`space-y-6 ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t("profile.title")}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {t("profile.subtitle")}
            </p>
          </div>

          <Button variant="primary" onClick={handleSave}>
            {t("profile.saveChanges")}
          </Button>
        </div>

        {/* Profile Overview Card */}
        <Card>
          <CardContent>
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                {user.avatar ? (
                  <img
                    className="h-16 w-16 rounded-full"
                    src={user.avatar}
                    alt={`${user.firstName} ${user.lastName}`}
                  />
                ) : (
                  <div className="h-16 w-16 rounded-full bg-gray-300 flex items-center justify-center">
                    <span className="text-2xl font-medium text-gray-700">
                      {user.firstName[0]}
                      {user.lastName[0]}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="text-xl font-medium text-gray-900 dark:text-white">
                    {user.firstName} {user.lastName}
                  </h3>
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.role === USER_ROLES.ADMIN
                        ? "bg-red-100 text-red-800"
                        : user.role === USER_ROLES.MANAGER
                          ? "bg-yellow-100 text-yellow-800"
                          : user.role === USER_ROLES.USER
                            ? "bg-blue-100 text-blue-800"
                            : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {t(`profile.role.${user.role}`)}
                  </span>
                </div>
                <p className="text-gray-600 dark:text-gray-400">{user.email}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {user.department}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: "profile", label: t("profile.tabs.profile") },
              { key: "preferences", label: t("profile.tabs.preferences") },
              { key: "security", label: t("profile.tabs.security") },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? "border-blue-500 text-blue-600 dark:text-blue-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {activeTab === "profile" && (
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-medium">
                    {t("profile.personalInfo")}
                  </h3>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label={t("profile.firstName")}
                      value={formData.firstName || ""}
                      onChange={(value: string | number | boolean) =>
                        handleInputChange("firstName", value as string)
                      }
                    />

                    <Input
                      label={t("profile.lastName")}
                      value={formData.lastName || ""}
                      onChange={(value: string | number | boolean) =>
                        handleInputChange("lastName", value as string)
                      }
                    />
                  </div>

                  <Input
                    label={t("profile.email")}
                    type="email"
                    value={formData.email || ""}
                    onChange={(value: string | number | boolean) =>
                      handleInputChange("email", value as string)
                    }
                  />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label={t("profile.phone")}
                      value={formData.phone || ""}
                      onChange={(value: string | number | boolean) =>
                        handleInputChange("phone", value as string)
                      }
                    />

                    <Select
                      label={t("profile.department")}
                      value={formData.department || ""}
                      onChange={(value: string | number | boolean) =>
                        handleInputChange("department", value as string)
                      }
                      options={DEPARTMENT_OPTIONS}
                    />
                  </div>

                  <Textarea
                    label={t("profile.bio")}
                    value={formData.bio || ""}
                    onChange={(value: string | number | boolean) =>
                      handleInputChange("bio", value as string)
                    }
                    rows={4}
                  />
                </CardContent>
              </Card>
            )}

            {activeTab === "preferences" && (
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-medium">
                    {t("profile.preferences")}
                  </h3>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Select
                      label={t("profile.language")}
                      value={formData.preferences?.language || ""}
                      onChange={(value: string | number | boolean) =>
                        handlePreferenceChange("language", value as string)
                      }
                      options={LANGUAGES}
                    />

                    <Select
                      label={t("profile.timezone")}
                      value={formData.preferences?.timezone || ""}
                      onChange={(value: string | number | boolean) =>
                        handlePreferenceChange("timezone", value as string)
                      }
                      options={TIMEZONES}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Select
                      label={t("profile.dateFormat")}
                      value={formData.preferences?.dateFormat || ""}
                      onChange={(value: string | number | boolean) =>
                        handlePreferenceChange("dateFormat", value as string)
                      }
                      options={[
                        { value: "MM/DD/YYYY", label: "MM/DD/YYYY" },
                        { value: "DD/MM/YYYY", label: "DD/MM/YYYY" },
                        { value: "YYYY-MM-DD", label: "YYYY-MM-DD" },
                      ]}
                    />

                    <Select
                      label={t("profile.currency")}
                      value={formData.preferences?.currency || ""}
                      onChange={(value: string | number | boolean) =>
                        handlePreferenceChange("currency", value as string)
                      }
                      options={CURRENCIES}
                    />
                  </div>

                  <Select
                    label={t("profile.theme")}
                    value={formData.preferences?.theme || ""}
                    onChange={(value: string | number | boolean) =>
                      handlePreferenceChange("theme", value as string)
                    }
                    options={[
                      { value: "light", label: "Light" },
                      { value: "dark", label: "Dark" },
                      { value: "system", label: "System" },
                    ]}
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                      {t("profile.notifications")}
                    </label>
                    <div className="space-y-2">
                      {Object.entries(
                        formData.preferences?.notifications || {},
                      ).map(([type, enabled]) => (
                        <label key={type} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={enabled}
                            onChange={(e) =>
                              handleNotificationChange(type, e.target.checked)
                            }
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <span className="ml-2 text-sm text-gray-700 dark:text-gray-300 capitalize">
                            {t(`profile.notification.${type}`)}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {activeTab === "security" && (
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-medium">
                    {t("profile.security")}
                  </h3>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Two-Factor Authentication */}
                  <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                        {t("profile.twoFactorAuth")}
                      </h4>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {user.security.twoFactorEnabled
                          ? t("profile.twoFactorEnabled")
                          : t("profile.twoFactorDisabled")}
                      </p>
                    </div>
                    <Button
                      variant={
                        user.security.twoFactorEnabled ? "outlined" : "primary"
                      }
                      size="small"
                      onClick={
                        user.security.twoFactorEnabled
                          ? onDisable2FA
                          : onEnable2FA
                      }
                    >
                      {user.security.twoFactorEnabled
                        ? t("profile.disable2FA")
                        : t("profile.enable2FA")}
                    </Button>
                  </div>

                  {/* Password Change */}
                  <div>
                    <Button
                      variant="outlined"
                      onClick={() => setShowPasswordForm(!showPasswordForm)}
                    >
                      {t("profile.changePassword")}
                    </Button>

                    {showPasswordForm && (
                      <div className="mt-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-4">
                        <Input
                          label={t("profile.currentPassword")}
                          type="password"
                          value={passwordData.currentPassword}
                          onChange={(value: string | number | boolean) =>
                            setPasswordData((prev) => ({
                              ...prev,
                              currentPassword: value as string,
                            }))
                          }
                        />

                        <Input
                          label={t("profile.newPassword")}
                          type="password"
                          value={passwordData.newPassword}
                          onChange={(value: string | number | boolean) =>
                            setPasswordData((prev) => ({
                              ...prev,
                              newPassword: value as string,
                            }))
                          }
                        />

                        <Input
                          label={t("profile.confirmPassword")}
                          type="password"
                          value={passwordData.confirmPassword}
                          onChange={(value: string | number | boolean) =>
                            setPasswordData((prev) => ({
                              ...prev,
                              confirmPassword: value as string,
                            }))
                          }
                        />

                        <div className="flex space-x-2">
                          <Button
                            variant="primary"
                            size="small"
                            onClick={handlePasswordChange}
                          >
                            {t("profile.updatePassword")}
                          </Button>
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => setShowPasswordForm(false)}
                          >
                            {t("common.cancel")}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Security Info */}
                  <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex justify-between">
                      <span>{t("profile.lastLogin")}:</span>
                      <span>
                        {formatDate(
                          new Date(new Date(user.security.lastLogin)),
                        )}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>{t("profile.loginAttempts")}:</span>
                      <span>{user.security.loginAttempts}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <h3 className="text-lg font-medium">
                  {t("profile.quickStats")}
                </h3>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {user.role === USER_ROLES.ADMIN ? "∞" : "25"}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {t("profile.projects")}
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {user.role === USER_ROLES.ADMIN ? "∞" : "100"}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {t("profile.reports")}
                  </div>
                </div>

                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {Math.floor(Math.random() * 100) + 50}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {t("profile.hoursLogged")}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <h3 className="text-lg font-medium">
                  {t("profile.recentActivity")}
                </h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-600 dark:text-gray-400">
                      {t("profile.loggedIn")}
                    </span>
                    <span className="text-gray-500 dark:text-gray-500 ml-auto">
                      {formatDate(new Date(new Date()))}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-600 dark:text-gray-400">
                      {t("profile.profileUpdated")}
                    </span>
                    <span className="text-gray-500 dark:text-gray-500 ml-auto">
                      2 days ago
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <span className="text-gray-600 dark:text-gray-400">
                      {t("profile.passwordChanged")}
                    </span>
                    <span className="text-gray-500 dark:text-gray-500 ml-auto">
                      1 week ago
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  },
);

UserProfile.displayName = "UserProfile";

export default UserProfile;
