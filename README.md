# NoSpamProxy Tenant Manager

A Python GUI application for managing NoSpamProxy tenants. Allows you to view, create, and configure tenants, assign user roles, and manage whitelisted IPs — without writing PowerShell manually.

## Requirements

- Windows with PowerShell
- NoSpamProxy installed and the intranet role reachable
- Python 3 (tkinter is included in the standard library)

## Installation

No installation needed. Clone or download the repository and run the script directly.

```
git clone https://github.com/karlocizma/nsp-tenant-manager.git
cd nsp-tenant-manager
python tenant-creation-script.py
```

## Usage

On startup the application connects to NoSpamProxy via `connect-nsp -IgnoreServerCertificateErrors` and loads the tenant list automatically. Every action that talks to NoSpamProxy runs in the background so the window stays responsive.

---

### Mandantenübersicht (Tenant List)

Displays all existing tenants with their Id, Name, Primary Domain, Primary Contact, and license counts for Protection Users and Encryption Users.

- **Aktualisieren** — reloads the list from NoSpamProxy.

The list refreshes automatically after a new tenant is created.

---

### Mandant erstellen (Create Tenant)

Creates a new tenant using `New-NspTenant`.

| Field | Required | Description |
|---|---|---|
| Tenant Name | Yes | No spaces allowed |
| Primary Domain | Yes | Main domain for the tenant |
| Primary Contact | Yes | Contact email address |
| Disclaimer Users | — | Number of disclaimer licences (default 0) |
| Encryption Users | — | Number of encryption licences (default 0) |
| Protection Users | — | Number of protection licences (default 0) |
| Large Files Users | — | Number of large files licences (default 0) |
| Managed Certificates | — | Number of managed certificate licences (default 0) |

After a successful creation the app switches back to the tenant list and refreshes it.

---

### IP Whitelist

Adds an IP address to the NoSpamProxy whitelist using `New-NspWhitelistedIP`.

Enter the IP address and click **IP hinzufügen**.

---

### Benutzerrollen (User Roles)

Assigns one or more roles to a user on a specific tenant using `New-NspUserRoleAssignment`.

1. Select the tenant from the dropdown (populated from the tenant list).
2. Enter the user identity (Windows username, e.g. `Administrator`).
3. Check one or more roles to assign:
   - **GlobalAdministrator** — can view and manage all tenants (use TenantId 0)
   - **ConfigurationAdministrator** — manages tenant configuration
   - **DisclaimerAdministrator** — manages disclaimer settings
   - **IdentityAdministrator** — manages identities and domains
   - **MonitoringAdministrator** — read-only monitoring access
4. Click **Rollen zuweisen**. Each selected role is assigned in a single PowerShell call.

On success the form clears and the roles are ready to assign to another user.

---

## PowerShell commands used

| Action | Command |
|---|---|
| Connect | `connect-nsp -IgnoreServerCertificateErrors` |
| List tenants | `Get-NspTenant` |
| Create tenant | `New-NspTenant` |
| Assign role | `New-NspUserRoleAssignment` |
| Add whitelisted IP | `New-NspWhitelistedIP` |
