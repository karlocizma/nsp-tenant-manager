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
        
        $StatusLabel.Foreground = "Green"
        $StatusLabel.Text = "Mandant erfolgreich erstellt!"
    } catch {
        $StatusLabel.Foreground = "Red"
        $StatusLabel.Text = "Fehler beim Erstellen des Mandanten: $_"
    }
})

# Show Window
$Window.ShowDialog()
