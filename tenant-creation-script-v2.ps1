Add-Type -AssemblyName PresentationFramework

# XAML for GUI
[xml]$XAML = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        Title="NoSpamProxy - Neuer Mandant" Height="500" Width="400">
    <Grid>
        <TextBlock Text="Mandantenname:" Margin="10,10,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="TenantName" Margin="10,30,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Primaerdomain:" Margin="10,70,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="PrimaryDomain" Margin="10,90,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Primaerer Kontakt:" Margin="10,130,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="PrimaryContact" Margin="10,150,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Disclaimer Nutzer:" Margin="10,190,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="DisclaimerUsers" Text="0" Margin="10,210,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Verschluesselungs Nutzer:" Margin="10,240,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="EncryptionUsers" Text="0" Margin="10,260,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Schutz Nutzer:" Margin="10,290,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="ProtectionUsers" Text="0" Margin="10,310,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Grosse Dateien Nutzer:" Margin="10,340,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="LargeFilesUsers" Text="0" Margin="10,360,10,0" VerticalAlignment="Top"/>
        
        <TextBlock Text="Verwaltete Zertifikate:" Margin="10,390,0,0" HorizontalAlignment="Left" VerticalAlignment="Top"/>
        <TextBox Name="ManagedCertificates" Text="0" Margin="10,410,10,0" VerticalAlignment="Top"/>
        
        <Button Content="Mandant erstellen" Name="CreateTenant" Margin="10,440,10,0" VerticalAlignment="Top" Height="30"/>
        
        <TextBlock Name="StatusLabel" Foreground="Red" Margin="10,480,10,0" VerticalAlignment="Top"/>
    </Grid>
</Window>
"@

# Load XAML
$reader = (New-Object System.Xml.XmlNodeReader $XAML)
$Window = [Windows.Markup.XamlReader]::Load($reader)

# Get UI Elements
$TenantName = $Window.FindName("TenantName")
$PrimaryDomain = $Window.FindName("PrimaryDomain")
$PrimaryContact = $Window.FindName("PrimaryContact")
$DisclaimerUsers = $Window.FindName("DisclaimerUsers")
$EncryptionUsers = $Window.FindName("EncryptionUsers")
$ProtectionUsers = $Window.FindName("ProtectionUsers")
$LargeFilesUsers = $Window.FindName("LargeFilesUsers")
$ManagedCertificates = $Window.FindName("ManagedCertificates")
$CreateTenant = $Window.FindName("CreateTenant")
$StatusLabel = $Window.FindName("StatusLabel")

# Function to send email notification
function Send-NotificationEmail {
    param (
        [string]$Tenant,
        [string]$Domain,
        [string]$Contact,
        [int]$DisclaimerUsers,
        [int]$EncryptionUsers,
        [int]$ProtectionUsers,
        [int]$LargeFilesUsers,
        [int]$ManagedCertificates
    )
    
    $SMTPServer = "exitus.ctl.de"  # Replace with actual SMTP server
    $From = "seekopf@ctl.de"  # Replace with actual sender email
    $To = "webservices@ctl.de"  # Replace with recipient email
    $Subject = "Neuer Mandant Erstellt: $Tenant"
    $Body = "Ein neuer Mandant wurde erstellt:

    $SMTPServer = "exitus.ctl.de"  # Replace with actual SMTP server
    $SMTPPort = 25  # Adjust if needed (e.g., 465 for SSL, 25 for non-authenticated)
    $From = "seekopf@ctl.de"  # Replace with actual sender email
    $To = "webservices@ctl.de"  # Replace with recipient email
    $Username = "ctl_webservices"  # SMTP username
    $Password = "62QzMOqcmgVbLz/ZaztiBVdr4EXY"  # SMTP password (consider securing this!)
    $SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force
    $Credential = New-Object System.Management.Automation.PSCredential ($Username, $SecurePassword)


Mandantenname: $Tenant
Primaerdomain: $Domain
Primaerer Kontakt: $Contact

Disclaimer Nutzer: $DisclaimerUsers
Verschluesselungs Nutzer: $EncryptionUsers
Schutz Nutzer: $ProtectionUsers
Grosse Dateien Nutzer: $LargeFilesUsers
Verwaltete Zertifikate: $ManagedCertificates"
    
    Send-MailMessage -SmtpServer $SMTPServer -Port $SMTPPort -UseSsl `
        -Credential $Credential -From $From -To $To -Subject $Subject -Body $Body -BodyAsText
}

# Validate and create tenant function
$CreateTenant.Add_Click({
    $Tenant = $TenantName.Text -replace '\s+', ''  # Remove spaces
    $Domain = $PrimaryDomain.Text
    $Contact = $PrimaryContact.Text
    
    if (-not $Tenant -or -not $Domain -or -not $Contact) {
        $StatusLabel.Text = "Alle Felder sind erforderlich!"
        return
    }
    
    try {
        connect-nsp -IgnoreServerCertificateErrors
        New-NspTenant -Name $Tenant -PrimaryDomain $Domain -PrimaryContact $Contact \
            -NumberOfDisclaimerUsers [int]$DisclaimerUsers.Text \
            -NumberOfEncryptionUsers [int]$EncryptionUsers.Text \
            -NumberOfProtectionUsers [int]$ProtectionUsers.Text \
            -NumberOfLargeFilesUsers [int]$LargeFilesUsers.Text \
            -NumberManagedCertificates [int]$ManagedCertificates.Text \
            -PrimaryDomainIsVerified
        
        # Send notification email
        Send-NotificationEmail -Tenant $Tenant -Domain $Domain -Contact $Contact \
            -DisclaimerUsers [int]$DisclaimerUsers.Text \
            -EncryptionUsers [int]$EncryptionUsers.Text \
            -ProtectionUsers [int]$ProtectionUsers.Text \
            -LargeFilesUsers [int]$LargeFilesUsers.Text \
            -ManagedCertificates [int]$ManagedCertificates.Text
        
        $StatusLabel.Foreground = "Green"
        $StatusLabel.Text = "Mandant erfolgreich erstellt!"
    } catch {
        $StatusLabel.Foreground = "Red"
        $StatusLabel.Text = "Fehler beim Erstellen des Mandanten: $_"
    }
})

# Show Window
$Window.ShowDialog()
