# NEXUS SSOT User Guides

This guide provides step-by-step instructions for users of the NEXUS Single Source of Truth (SSOT) system, including developers, administrators, and end-users.

## Table of Contents

1. [Getting Started](#getting-started)
2. [For Developers](#for-developers)
3. [For Administrators](#for-administrators)
4. [For End Users](#for-end-users)
5. [Best Practices](#best-practices)
6. [FAQ](#faq)

## Getting Started

### What is NEXUS SSOT?

NEXUS SSOT is a centralized system for managing API aliases. It allows you to create user-friendly names for API endpoints and resolve them dynamically based on context.

### Key Benefits

- **Consistency**: Ensures uniform API naming across applications
- **Flexibility**: Easy to change endpoints without updating code
- **Governance**: Centralized control over API aliases
- **Auditability**: Full logging of all alias operations

### Quick Start

1. **Access the System**
   - Navigate to `http://localhost:8000` (development)
   - Or your production URL

2. **Create Your First Alias**

   ```bash
   curl -X POST http://localhost:8000/api/aliases \
     -H "Content-Type: application/json" \
     -d '{
       "alias": "user-profile",
       "canonical": "https://api.nexus.com/v1/users/profile",
       "context": "frontend",
       "description": "User profile endpoint"
     }'
   ```

3. **Resolve an Alias**
   ```bash
   curl http://localhost:8000/api/aliases/resolve/frontend/user-profile
   ```

## For Developers

### Integrating with Your Application

#### Python

```python
import requests

def get_user_profile():
    # Resolve alias
    response = requests.get('http://localhost:8000/api/aliases/resolve/frontend/user-profile')
    endpoint = response.json()['canonical_name']

    # Use the resolved endpoint
    profile_response = requests.get(endpoint)
    return profile_response.json()

# Usage
profile = get_user_profile()
print(profile)
```

#### JavaScript

```javascript
async function getUserProfile() {
  // Resolve alias
  const aliasResponse = await fetch(
    "/api/aliases/resolve/frontend/user-profile",
  );
  const { canonical_name } = await aliasResponse.json();

  // Use the resolved endpoint
  const profileResponse = await fetch(canonical_name);
  return await profileResponse.json();
}

// Usage
const profile = await getUserProfile();
console.log(profile);
```

#### Java

```java
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class SSOTClient {
    private static final String SSOT_BASE_URL = "http://localhost:8000/api/aliases";

    public static String resolveAlias(String context, String alias) throws Exception {
        URL url = new URL(SSOT_BASE_URL + "/resolve/" + context + "/" + alias);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String inputLine;
        StringBuffer response = new StringBuffer();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        // Parse JSON response (simplified)
        return response.toString().split("\"canonical_name\":\"")[1].split("\"")[0];
    }

    public static void main(String[] args) throws Exception {
        String endpoint = resolveAlias("frontend", "user-profile");
        System.out.println("Resolved endpoint: " + endpoint);
    }
}
```

### Error Handling

Always handle potential errors when resolving aliases:

```python
import requests

def safe_resolve_alias(context, alias):
    try:
        response = requests.get(f'http://localhost:8000/api/aliases/resolve/{context}/{alias}')
        response.raise_for_status()
        return response.json()['canonical_name']
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Alias '{alias}' not found in context '{context}'")
        elif e.response.status_code == 400:
            print(f"Alias '{alias}' has expired")
        else:
            print(f"Error resolving alias: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Testing Your Integration

1. **Unit Tests**

   ```python
   def test_alias_resolution():
       endpoint = safe_resolve_alias('frontend', 'user-profile')
       assert endpoint == 'https://api.nexus.com/v1/users/profile'
   ```

2. **Integration Tests**
   ```python
   def test_full_flow():
       # Test the complete flow from alias to API call
       endpoint = safe_resolve_alias('frontend', 'user-profile')
       if endpoint:
           response = requests.get(endpoint)
           assert response.status_code == 200
   ```

## For Administrators

### Managing Aliases

#### Creating Aliases

Use the web interface or API to create new aliases:

1. **Via Web Interface**
   - Go to the SSOT admin panel
   - Click "New Alias"
   - Fill in the details
   - Save

2. **Via API**
   ```bash
   curl -X POST http://localhost:8000/api/aliases \
     -H "Authorization: Bearer <admin-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "alias": "product-list",
       "canonical": "https://api.nexus.com/v1/products",
       "context": "backend",
       "description": "Product listing endpoint"
     }'
   ```

#### Updating Aliases

```bash
curl -X PUT http://localhost:8000/api/aliases/product-list \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "canonical": "https://new-api.nexus.com/v1/products"
  }'
```

#### Deleting Aliases

```bash
curl -X DELETE http://localhost:8000/api/aliases/product-list \
  -H "Authorization: Bearer <admin-token>"
```

### Monitoring the System

#### Health Checks

- Visit `http://localhost:8000/api/aliases/health`
- Check for "status": "ok"

#### Metrics Dashboard

- Access Grafana at `http://localhost:3000`
- Look for SSOT-specific dashboards
- Monitor key metrics:
  - Alias resolution times
  - Error rates
  - Active aliases count

#### Audit Logs

- Review audit logs at `http://localhost:8000/api/aliases/audit`
- Filter by date, user, or action
- Export logs for compliance

### Backup and Recovery

#### Creating Backups

```bash
python scripts/backup_dr.py backup --db-host localhost --db-name nexus_db
```

#### Restoring from Backup

```bash
python scripts/backup_dr.py restore --backup-file backups/backup_manifest_20250127_120000.json
```

#### Rollback Procedures

```bash
python scripts/rollback_automation.py create --components database config
python scripts/rollback_automation.py rollback --rollback-id rollback_20250127_120000
```

### Compliance Management

#### Running Compliance Checks

```bash
python scripts/compliance_check.py --format text
```

#### Validating Standards

```bash
python scripts/compliance_validation.py --standards GDPR HIPAA --format text
```

#### Generating Reports

```bash
python scripts/compliance_check.py --output compliance_report.json --format json
```

## For End Users

### Using the Web Interface

1. **Login**
   - Go to the SSOT web interface
   - Enter your credentials

2. **Search for Aliases**
   - Use the search bar to find aliases
   - Filter by context or status

3. **View Alias Details**
   - Click on an alias to see details
   - View canonical endpoint, context, and history

4. **Request New Aliases**
   - Use the "Request Alias" feature
   - Fill in the required information
   - Submit for approval

### Understanding Contexts

- **Frontend**: For web and mobile applications
- **Backend**: For internal services and APIs
- **System**: For administrative and system-level operations

### Troubleshooting Common Issues

#### "Alias Not Found"

- Check if you're using the correct context
- Verify the alias name spelling
- Contact your administrator

#### "Access Denied"

- Ensure you have the necessary permissions
- Check if your token is valid
- Contact support if issues persist

#### "Endpoint Not Available"

- The canonical endpoint may be down
- Check the status of the target service
- Report issues to the service team

## Best Practices

### For Developers

- Always handle errors when resolving aliases
- Cache resolved endpoints when possible
- Use descriptive alias names
- Test with different contexts

### For Administrators

- Regularly review and clean up unused aliases
- Monitor system performance
- Keep audit logs for compliance
- Train users on proper usage

### For All Users

- Use aliases instead of hard-coded endpoints
- Report issues promptly
- Follow security guidelines
- Keep credentials secure

## FAQ

### What is an alias?

An alias is a user-friendly name that represents a longer API endpoint URL.

### Why use aliases?

Aliases make APIs easier to manage and change without updating all consuming applications.

### How do I create an alias?

Administrators can create aliases through the web interface or API.

### What happens if an alias expires?

Expired aliases will return an error when resolved. They can be renewed or replaced.

### Can I have the same alias in different contexts?

Yes, the same alias name can exist in different contexts with different canonical endpoints.

### How do I monitor alias usage?

Use the metrics dashboard to monitor resolution times, error rates, and usage patterns.

### What if I need to change an endpoint?

Update the canonical endpoint in the alias definition. All applications using the alias will automatically use the new endpoint.

### Is the system secure?

Yes, the system includes authentication, authorization, encryption, and comprehensive audit logging.

### How do I get help?

- Check the troubleshooting guide
- Review the technical documentation
- Contact the support team
- Create a support ticket

This user guide is designed to help you get the most out of the NEXUS SSOT system. For additional support, please contact the system administrators.
