import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import threading

NSP_CONNECT = "connect-nsp -IgnoreServerCertificateErrors; "

_tenant_map = {}  # display label -> tenant Id


def run_powershell(script, callback):
    def _run():
        try:
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True, text=True, shell=True
            )
            if result.returncode != 0:
                callback(None, result.stderr.strip() or "Unbekannter Fehler")
            else:
                callback(result.stdout.strip(), None)
        except Exception as e:
            callback(None, str(e))
    threading.Thread(target=_run, daemon=True).start()


# --- Tenant List ---

def refresh_tenants():
    btn_refresh.config(state="disabled", text="Lädt...")
    tree.delete(*tree.get_children())

    def on_done(output, error):
        btn_refresh.config(state="normal", text="Aktualisieren")
        if error:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Mandanten:\n{error}")
            return
        if not output:
            return
        try:
            data = json.loads(output)
            if isinstance(data, dict):
                data = [data]
            _tenant_map.clear()
            for t in data:
                tree.insert("", "end", values=(
                    t.get("Id", ""),
                    t.get("Name", ""),
                    t.get("PrimaryDomain", ""),
                    t.get("PrimaryContact", ""),
                    t.get("NumberOfProtectionUsers", ""),
                    t.get("NumberOfEncryptionUsers", ""),
                ))
                label = f"{t.get('Name', '?')} (Id: {t.get('Id', '?')})"
                _tenant_map[label] = t.get("Id", "")
            combo_tenant["values"] = list(_tenant_map.keys())
            if _tenant_map:
                combo_tenant.current(0)
        except json.JSONDecodeError:
            messagebox.showerror("Fehler", "Mandantenliste konnte nicht gelesen werden.")

    run_powershell(
        NSP_CONNECT + "Get-NspTenant | ConvertTo-Json -Depth 2",
        lambda out, err: root.after(0, on_done, out, err)
    )


# --- Create Tenant ---

def create_tenant():
    tenant_name = entry_tenant_name.get().strip()
    primary_domain = entry_primary_domain.get().strip()
    primary_contact = entry_primary_contact.get().strip()
    disclaimer_users = entry_disclaimer_users.get().strip()
    encryption_users = entry_encryption_users.get().strip()
    protection_users = entry_protection_users.get().strip()
    largefiles_users = entry_largefiles_users.get().strip()
    managed_certificates = entry_managed_certificates.get().strip()

    if not tenant_name or not primary_domain or not primary_contact:
        messagebox.showerror("Fehler", "Alle Pflichtfelder müssen ausgefüllt werden.")
        return
    if " " in tenant_name:
        messagebox.showerror("Fehler", "Der Tenant-Name darf keine Leerzeichen enthalten.")
        return

    numeric_fields = {
        "Disclaimer Users": disclaimer_users,
        "Encryption Users": encryption_users,
        "Protection Users": protection_users,
        "Large Files Users": largefiles_users,
        "Managed Certificates": managed_certificates,
    }
    for label, val in numeric_fields.items():
        if not val.isdigit():
            messagebox.showerror("Fehler", f"{label} muss eine ganze Zahl sein.")
            return

    btn_create.config(state="disabled")

    script = (
        f'{NSP_CONNECT}'
        f'New-NspTenant -Name "{tenant_name}" -PrimaryDomain "{primary_domain}" '
        f'-PrimaryContact "{primary_contact}" '
        f'-NumberOfDisclaimerUsers {disclaimer_users} '
        f'-NumberOfEncryptionUsers {encryption_users} '
        f'-NumberOfProtectionUsers {protection_users} '
        f'-NumberOfLargeFilesUsers {largefiles_users} '
        f'-NumberManagedCertificates {managed_certificates} '
        f'-PrimaryDomainIsVerified'
    )

    def on_done(output, error):
        btn_create.config(state="normal")
        if error:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Tenants:\n{error}")
        else:
            messagebox.showinfo("Erfolg", "Tenant wurde erfolgreich erstellt!")
            refresh_tenants()
            notebook.select(tab_list)

    run_powershell(script, lambda out, err: root.after(0, on_done, out, err))


# --- IP Whitelist ---

def add_whitelist_ip():
    ip = entry_ip.get().strip()
    if not ip:
        messagebox.showerror("Fehler", "Bitte eine IP-Adresse eingeben.")
        return

    btn_whitelist.config(state="disabled")

    def on_done(output, error):
        btn_whitelist.config(state="normal")
        if error:
            messagebox.showerror("Fehler", f"Fehler beim Hinzufügen der IP:\n{error}")
        else:
            messagebox.showinfo("Erfolg", f"IP {ip} wurde zur Whitelist hinzugefügt.")
            entry_ip.delete(0, tk.END)

    run_powershell(
        NSP_CONNECT + f"New-NspWhitelistedIP {ip}",
        lambda out, err: root.after(0, on_done, out, err)
    )


# --- User Role Assignment ---

ROLES = [
    "GlobalAdministrator",
    "ConfigurationAdministrator",
    "DisclaimerAdministrator",
    "IdentityAdministrator",
    "MonitoringAdministrator",
]


def assign_roles():
    selected_label = combo_tenant.get()
    identity = entry_identity.get().strip()

    if not selected_label:
        messagebox.showerror("Fehler", "Bitte einen Mandanten auswählen.")
        return
    if not identity:
        messagebox.showerror("Fehler", "Bitte einen Benutzer eingeben.")
        return

    selected_roles = [role for role, var in role_vars.items() if var.get()]
    if not selected_roles:
        messagebox.showerror("Fehler", "Bitte mindestens eine Rolle auswählen.")
        return

    tenant_id = _tenant_map[selected_label]
    btn_assign.config(state="disabled")

    commands = "; ".join(
        f'New-NspUserRoleAssignment -TenantId {tenant_id} -Identity "{identity}" -Role {role}'
        for role in selected_roles
    )
    script = NSP_CONNECT + commands

    def on_done(output, error):
        btn_assign.config(state="normal")
        if error:
            messagebox.showerror("Fehler", f"Fehler beim Zuweisen der Rollen:\n{error}")
        else:
            messagebox.showinfo("Erfolg", f"Rollen für '{identity}' wurden erfolgreich zugewiesen.")
            for var in role_vars.values():
                var.set(False)
            entry_identity.delete(0, tk.END)

    run_powershell(script, lambda out, err: root.after(0, on_done, out, err))


# --- GUI ---

root = tk.Tk()
root.title("NoSpamProxy Verwaltung")
root.geometry("750x480")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Tab 1: Tenant list
tab_list = ttk.Frame(notebook)
notebook.add(tab_list, text="Mandantenübersicht")

columns = ("Id", "Name", "Primary Domain", "Primary Contact", "Protection Users", "Encryption Users")
tree = ttk.Treeview(tab_list, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110)
tree.pack(fill="both", expand=True, padx=5, pady=(5, 0))

btn_refresh = ttk.Button(tab_list, text="Aktualisieren", command=refresh_tenants)
btn_refresh.pack(pady=6)

# Tab 2: Create tenant
tab_create = ttk.Frame(notebook)
notebook.add(tab_create, text="Mandant erstellen")

form_fields = [
    ("Tenant Name *",        "entry_tenant_name",        ""),
    ("Primary Domain *",     "entry_primary_domain",     ""),
    ("Primary Contact *",    "entry_primary_contact",    ""),
    ("Disclaimer Users",     "entry_disclaimer_users",   "0"),
    ("Encryption Users",     "entry_encryption_users",   "0"),
    ("Protection Users",     "entry_protection_users",   "0"),
    ("Large Files Users",    "entry_largefiles_users",   "0"),
    ("Managed Certificates", "entry_managed_certificates", "0"),
]

_entries = {}
for i, (label, name, default) in enumerate(form_fields):
    ttk.Label(tab_create, text=label).grid(row=i, column=0, sticky="e", padx=10, pady=4)
    e = ttk.Entry(tab_create, width=32)
    if default:
        e.insert(0, default)
    e.grid(row=i, column=1, padx=10, pady=4, sticky="w")
    _entries[name] = e

entry_tenant_name        = _entries["entry_tenant_name"]
entry_primary_domain     = _entries["entry_primary_domain"]
entry_primary_contact    = _entries["entry_primary_contact"]
entry_disclaimer_users   = _entries["entry_disclaimer_users"]
entry_encryption_users   = _entries["entry_encryption_users"]
entry_protection_users   = _entries["entry_protection_users"]
entry_largefiles_users   = _entries["entry_largefiles_users"]
entry_managed_certificates = _entries["entry_managed_certificates"]

btn_create = ttk.Button(tab_create, text="Tenant erstellen", command=create_tenant)
btn_create.grid(row=len(form_fields), column=0, columnspan=2, pady=12)

# Tab 3: IP Whitelist
tab_ip = ttk.Frame(notebook)
notebook.add(tab_ip, text="IP Whitelist")

ttk.Label(tab_ip, text="IP-Adresse:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
entry_ip = ttk.Entry(tab_ip, width=32)
entry_ip.grid(row=0, column=1, padx=10, pady=8, sticky="w")

btn_whitelist = ttk.Button(tab_ip, text="IP hinzufügen", command=add_whitelist_ip)
btn_whitelist.grid(row=1, column=0, columnspan=2, pady=6)

# Tab 4: User role assignment
tab_roles = ttk.Frame(notebook)
notebook.add(tab_roles, text="Benutzerrollen")

ttk.Label(tab_roles, text="Mandant:").grid(row=0, column=0, padx=10, pady=6, sticky="e")
combo_tenant = ttk.Combobox(tab_roles, width=34, state="readonly")
combo_tenant.grid(row=0, column=1, padx=10, pady=6, sticky="w")

ttk.Label(tab_roles, text="Benutzer (Identity):").grid(row=1, column=0, padx=10, pady=6, sticky="e")
entry_identity = ttk.Entry(tab_roles, width=36)
entry_identity.grid(row=1, column=1, padx=10, pady=6, sticky="w")

ttk.Label(tab_roles, text="Rollen:").grid(row=2, column=0, padx=10, pady=(10, 2), sticky="ne")
roles_frame = ttk.Frame(tab_roles)
roles_frame.grid(row=2, column=1, padx=10, pady=(10, 2), sticky="w")

role_vars = {}
for role in ROLES:
    var = tk.BooleanVar()
    ttk.Checkbutton(roles_frame, text=role, variable=var).pack(anchor="w")
    role_vars[role] = var

btn_assign = ttk.Button(tab_roles, text="Rollen zuweisen", command=assign_roles)
btn_assign.grid(row=3, column=0, columnspan=2, pady=12)

refresh_tenants()
root.mainloop()
