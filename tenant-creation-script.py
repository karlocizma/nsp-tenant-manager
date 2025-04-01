import tkinter as tk
from tkinter import messagebox
import subprocess

def create_tenant():
    tenant_name = entry_tenant_name.get().strip()
    primary_domain = entry_primary_domain.get().strip()
    primary_contact = entry_primary_contact.get().strip()
    disclaimer_users = entry_disclaimer_users.get().strip()
    encryption_users = entry_encryption_users.get().strip()
    protection_users = entry_protection_users.get().strip()
    largefiles_users = entry_largefiles_users.get().strip()
    managed_certificates = entry_managed_certificates.get().strip()
    
    if " " in tenant_name:
        messagebox.showerror("Fehler", "Der Tenant-Name darf keine Leerzeichen enthalten.")
        return
    
    if not tenant_name or not primary_domain or not primary_contact:
        messagebox.showerror("Fehler", "Alle Felder müssen ausgefüllt werden.")
        return
    
    powershell_script = f'''
    connect-nsp -IgnoreServerCertificateErrors;
    New-NspTenant -Name {tenant_name} -PrimaryDomain {primary_domain} -PrimaryContact {primary_contact} \
    -NumberOfDisclaimerUsers {disclaimer_users} -NumberOfEncryptionUsers {encryption_users} -NumberOfProtectionUsers {protection_users} \
    -NumberOfLargeFilesUsers {largefiles_users} -NumberManagedCertificates {managed_certificates} -PrimaryDomainIsVerified
    '''
    
    try:
        subprocess.run(["powershell", "-Command", powershell_script], check=True, shell=True)
        messagebox.showinfo("Erfolg", "Tenant wurde erfolgreich erstellt!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Fehler", f"Fehler beim Erstellen des Tenants: {e}")

# GUI erstellen
root = tk.Tk()
root.title("NoSpamProxy Tenant Ersteller")
root.geometry("400x500")

# Labels und Eingabefelder
tk.Label(root, text="Tenant Name:").pack()
entry_tenant_name = tk.Entry(root)
entry_tenant_name.pack()

tk.Label(root, text="Primary Domain:").pack()
entry_primary_domain = tk.Entry(root)
entry_primary_domain.pack()

tk.Label(root, text="Primary Contact:").pack()
entry_primary_contact = tk.Entry(root)
entry_primary_contact.pack()

tk.Label(root, text="Disclaimer Users:").pack()
entry_disclaimer_users = tk.Entry(root)
entry_disclaimer_users.insert(0, "0")
entry_disclaimer_users.pack()

tk.Label(root, text="Encryption Users:").pack()
entry_encryption_users = tk.Entry(root)
entry_encryption_users.insert(0, "0")
entry_encryption_users.pack()

tk.Label(root, text="Protection Users:").pack()
entry_protection_users = tk.Entry(root)
entry_protection_users.insert(0, "0")
entry_protection_users.pack()

tk.Label(root, text="Large Files Users:").pack()
entry_largefiles_users = tk.Entry(root)
entry_largefiles_users.insert(0, "0")
entry_largefiles_users.pack()

tk.Label(root, text="Managed Certificates:").pack()
entry_managed_certificates = tk.Entry(root)
entry_managed_certificates.insert(0, "0")
entry_managed_certificates.pack()

# Button
tk.Button(root, text="Tenant erstellen", command=create_tenant).pack(pady=10)

root.mainloop()
