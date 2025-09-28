# Security Policies

This document outlines the security policies for the network segments in the NEXUS platform.

## VLAN 1 (Public)

This VLAN is for public-facing services.

| Service | Protocol | Port    | Source    | Destination | Description                                        |
| ------- | -------- | ------- | --------- | ----------- | -------------------------------------------------- |
| Kong    | TCP      | 80, 443 | 0.0.0.0/0 | Kong        | Allow inbound HTTP/HTTPS traffic from the internet |
| Kong    | TCP      | 8001    | 127.0.0.1 | Kong        | Allow admin access from localhost only             |

## VLAN 2 (Application)

This VLAN is for the application microservices.

| Service      | Protocol | Port | Source       | Destination  | Description                        |
| ------------ | -------- | ---- | ------------ | ------------ | ---------------------------------- |
| auth_service | TCP      | 5000 | Kong         | auth_service | Allow inbound traffic from Kong    |
| auth_service | TCP      | 8080 | auth_service | Keycloak     | Allow outbound traffic to Keycloak |

## VLAN 3 (Data)

This VLAN is for the data services.

| Service    | Protocol | Port | Source       | Destination | Description                                 |
| ---------- | -------- | ---- | ------------ | ----------- | ------------------------------------------- |
| Keycloak   | TCP      | 8080 | auth_service | Keycloak    | Allow inbound traffic from the auth_service |
| PostgreSQL | TCP      | 5432 | Keycloak     | PostgreSQL  | Allow inbound traffic from Keycloak         |
