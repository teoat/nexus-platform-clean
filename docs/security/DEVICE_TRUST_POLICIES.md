# NEXUS Device Trust Policies

## 1. Introduction

This document defines the device trust policies for the NEXUS platform, to be implemented within Keycloak. These policies will govern access to NEXUS resources based on the trust level of the accessing device, as part of our Zero-Trust Architecture.

## 2. Device Trust Levels (Recap)

As defined in `DEVICE_TRUST_VALIDATION_DESIGN.md`, devices will be categorized into the following trust levels:

- **High Trust:** Managed devices, fully compliant, up-to-date, encrypted, and free of known vulnerabilities.
- **Medium Trust:** Managed devices with minor compliance issues (e.g., outdated software, but still within acceptable limits).
- **Low Trust:** Unmanaged devices, non-compliant, or devices exhibiting suspicious behavior.

## 3. Policy Objectives

- Ensure only authorized and compliant devices access sensitive resources.
- Minimize the attack surface by restricting access for non-compliant devices.
- Provide a seamless experience for high-trust devices while challenging or blocking low-trust devices.
- Enable dynamic access control based on real-time device posture.

## 4. Policy Definitions

### 4.1 General Access Policy

- **Default:** All access attempts from unknown or unclassified devices will be denied by default.
- **Minimum Trust:** A device must have at least a 'Medium Trust' level to access any NEXUS resource.

### 4.2 Resource-Specific Access Policies

#### 4.2.1 Sensitive Data Access (e.g., Financial Records, PII)

- **Requirement:** Only 'High Trust' devices are permitted to access sensitive data.
- **Enforcement:** Keycloak authorization policies will check for the 'High Trust' attribute in the device context. If not present, access is denied.
- **Action on Non-Compliance:** For devices attempting to access sensitive data without 'High Trust':
  - **Deny Access:** Immediately block the access request.
  - **Alert:** Generate a critical alert in the SIEM.
  - **User Notification:** Inform the user of the reason for denial and steps to achieve compliance.

#### 4.2.2 Production Environment Access (e.g., Deployment Tools, Production Dashboards)

- **Requirement:** Only 'High Trust' devices are permitted to access production environment resources.
- **Enforcement:** Keycloak authorization policies will check for the 'High Trust' attribute. Additionally, access may require specific network segments (e.g., corporate VPN).
- **Action on Non-Compliance:** Similar to Sensitive Data Access, with immediate denial and critical alerting.

#### 4.2.3 Development Environment Access

- **Requirement:** Devices with at least 'Medium Trust' are permitted to access development environment resources.
- **Enforcement:** Keycloak authorization policies will check for the 'Medium Trust' attribute.
- **Action on Non-Compliance:** For devices with 'Low Trust':
  - **Deny Access:** Block the access request.
  - **Quarantine:** Potentially move the device to a quarantined network segment.
  - **User Remediation:** Guide the user on steps to improve device trust (e.g., install updates, enable encryption).

### 4.3 Dynamic Policy Adjustments

- **Behavioral Anomalies:** If a device, regardless of its current trust level, exhibits suspicious behavior (e.g., unusual login patterns, access to unauthorized resources), its trust level can be dynamically downgraded, and access policies re-evaluated in real-time.
- **Vulnerability Detection:** Immediate trust level downgrade for devices found to have critical unpatched vulnerabilities.

## 5. Policy Enforcement Points

- **Keycloak Authentication/Authorization Flows:** Primary enforcement point, where device attributes are evaluated against policies.
- **Network Access Control (NAC):** If implemented, NAC will enforce policies at the network layer, preventing non-compliant devices from even reaching Keycloak.
- **Application-Level Enforcement:** Applications may perform additional checks based on device context provided by Keycloak.

## 6. Next Steps

1.  **Integrate EDR/MDM with Keycloak:** Complete the technical integration to feed device attributes into Keycloak.
2.  **Configure Keycloak Policies:** Implement the defined policies within Keycloak's authentication and authorization services.
3.  **Test Policy Enforcement:** Thoroughly test all defined policies with various device trust scenarios.

This document will be updated as policies are refined and new requirements emerge.
