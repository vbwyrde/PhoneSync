# PhoneSync - File Organization Script
# Organizes JPG and MP4 files into date-based folders with Wudan rules
# Author: Generated for PhoneSync Project
# Date: 2025-08-31

param(
    [string]$ConfigPath = "config.json",
    [switch]$DryRun,
    [switch]$Verbose
)

# Global variables
$script:Config = $null
$script:LogFile = $null
$script:ExistingFilesCache = @{}

# Function to write log messages
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Write to console
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
        "INFO"  { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage }
    }
    
    # Write to log file if enabled
    if ($script:Config.logging.enabled -and $script:LogFile) {
        Add-Content -Path $script:LogFile -Value $logMessage
    }
}

# Function to load configuration
function Load-Configuration {
    param([string]$ConfigPath)
    
    try {
        if (-not (Test-Path $ConfigPath)) {
            throw "Configuration file not found: $ConfigPath"
        }
        
        $configContent = Get-Content $ConfigPath -Raw | ConvertFrom-Json
        Write-Log "Configuration loaded successfully from $ConfigPath"
        return $configContent
    }
    catch {
        Write-Log "Failed to load configuration: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Function to initialize logging
function Initialize-Logging {
    if ($script:Config.logging.enabled) {
        $script:LogFile = $script:Config.logging.logPath
        
        # Create log directory if it doesn't exist
        $logDir = Split-Path $script:LogFile -Parent
        if ($logDir -and -not (Test-Path $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        
        # Rotate log if it's too large
        if (Test-Path $script:LogFile) {
            $logSize = (Get-Item $script:LogFile).Length / 1MB
            if ($logSize -gt $script:Config.logging.maxLogSizeMB) {
                $backupLog = $script:LogFile -replace '\.log$', "_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
                Move-Item $script:LogFile $backupLog
                Write-Log "Log rotated to $backupLog"
            }
        }
        
        Write-Log "=== PhoneSync Started ===" "INFO"
    }
}

# Function to build cache of existing files in target directories
function Build-ExistingFilesCache {
    Write-Log "Building cache of existing files in target directories..."

    $script:ExistingFilesCache = @{}
    $totalFiles = 0

    # Get all target paths
    $targetPaths = @(
        $script:Config.targetPaths.pictures,
        $script:Config.targetPaths.videos,
        $script:Config.targetPaths.wudanVideos
    )

    foreach ($targetPath in $targetPaths) {
        if (Test-Path $targetPath) {
            Write-Log "Scanning existing files in: $targetPath"

            try {
                $existingFiles = Get-ChildItem -Path $targetPath -Recurse -File -ErrorAction SilentlyContinue

                foreach ($file in $existingFiles) {
                    $fileKey = "$($file.Name)|$($file.Length)"

                    if (-not $script:ExistingFilesCache.ContainsKey($fileKey)) {
                        $script:ExistingFilesCache[$fileKey] = @()
                    }

                    # Extract the date pattern from the directory name for flexible matching
                    $directoryName = Split-Path $file.DirectoryName -Leaf
                    $datePattern = $null
                    if ($directoryName -match '^(\d{4}_\d{2}_\d{2})') {
                        $datePattern = $matches[1]
                    }

                    $script:ExistingFilesCache[$fileKey] += @{
                        Path = $file.FullName
                        LastWriteTime = $file.LastWriteTime
                        Directory = $file.DirectoryName
                        DatePattern = $datePattern
                        FullDirectoryName = $directoryName
                    }

                    $totalFiles++
                }
            }
            catch {
                Write-Log "Error scanning $targetPath`: $($_.Exception.Message)" "WARN"
            }
        }
        else {
            Write-Log "Target path does not exist, will be created: $targetPath" "INFO"
        }
    }

    Write-Log "Cache built successfully. Found $totalFiles existing files across all target directories."
}

# Function to check if file already exists in target
function Test-FileExistsInTarget {
    param(
        [string]$FileName,
        [long]$FileSize,
        [DateTime]$FileDate,
        [string]$TargetDirectory
    )

    if (-not $script:Config.options.enableDeduplication) {
        return $false
    }

    $fileKey = "$FileName|$FileSize"

    if ($script:ExistingFilesCache.ContainsKey($fileKey)) {
        $matchingFiles = $script:ExistingFilesCache[$fileKey]

        # Extract the expected date pattern from the target directory
        $targetDirectoryName = Split-Path $TargetDirectory -Leaf
        $expectedDatePattern = $null
        if ($targetDirectoryName -match '^(\d{4}_\d{2}_\d{2})') {
            $expectedDatePattern = $matches[1]
        }

        foreach ($existingFile in $matchingFiles) {
            # Check if the file is in a directory with the same date pattern
            $matchFound = $false

            if ($expectedDatePattern -and $existingFile.DatePattern) {
                # Compare date patterns (flexible matching)
                if ($existingFile.DatePattern -eq $expectedDatePattern) {
                    $matchFound = $true
                    Write-Log "Found existing file in date-matched folder: $FileName in $($existingFile.FullDirectoryName)" "INFO"
                }
            }
            elseif ($existingFile.Directory -eq $TargetDirectory) {
                # Exact directory match (fallback)
                $matchFound = $true
            }

            if ($matchFound) {
                # If forceRecopyIfNewer is enabled, check modification dates
                if ($script:Config.options.forceRecopyIfNewer) {
                    if ($FileDate -gt $existingFile.LastWriteTime) {
                        Write-Log "File exists but source is newer: $FileName" "INFO"
                        return $false  # File exists but source is newer, so copy it
                    }
                }

                Write-Log "File already exists in target: $FileName (Size: $FileSize bytes)" "INFO"
                return $true
            }
        }
    }

    return $false
}

# Function to find existing folder with date pattern
function Find-ExistingDateFolder {
    param(
        [string]$BasePath,
        [string]$DatePattern
    )

    if (-not (Test-Path $BasePath)) {
        return $null
    }

    try {
        # Look for folders that start with the date pattern
        $matchingFolders = Get-ChildItem -Path $BasePath -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match "^$([regex]::Escape($DatePattern))(_.*)?$" }

        if ($matchingFolders) {
            # Return the first matching folder (or could implement logic to choose preferred one)
            $selectedFolder = $matchingFolders[0]
            Write-Log "Found existing date folder: $($selectedFolder.Name) for pattern $DatePattern"
            return $selectedFolder.FullName
        }
    }
    catch {
        Write-Log "Error searching for existing date folders in $BasePath`: $($_.Exception.Message)" "WARN"
    }

    return $null
}

# Function to get file hash for comparison
function Get-FileHashQuick {
    param([string]$FilePath)

    try {
        # Use a quick hash of first and last 1KB for large files
        $fileInfo = Get-Item $FilePath
        if ($fileInfo.Length -gt 2048) {
            # For large files, hash first 1KB + last 1KB + file size
            $firstBytes = Get-Content $FilePath -Encoding Byte -TotalCount 1024
            $lastBytes = Get-Content $FilePath -Encoding Byte -Tail 1024
            $combinedBytes = $firstBytes + $lastBytes + [System.Text.Encoding]::UTF8.GetBytes($fileInfo.Length.ToString())
            $hash = [System.Security.Cryptography.SHA256]::Create().ComputeHash($combinedBytes)
        }
        else {
            # For small files, hash the entire file
            $hash = Get-FileHash $FilePath -Algorithm SHA256
            return $hash.Hash
        }

        return [System.BitConverter]::ToString($hash) -replace '-', ''
    }
    catch {
        Write-Log "Error computing hash for $FilePath`: $($_.Exception.Message)" "WARN"
        return $null
    }
}

# Function to check if file matches Wudan time rules
function Test-WudanTimeRules {
    param(
        [DateTime]$FileDate
    )

    $year = $FileDate.Year
    $dayOfWeek = [int]$FileDate.DayOfWeek  # Sunday = 0, Monday = 1, etc.
    $timeOfDay = $FileDate.ToString("HH:mm")

    # Determine which rule set to use
    $rules = if ($year -lt 2021) {
        $script:Config.wudanRules.before2021
    } else {
        $script:Config.wudanRules.after2021
    }

    # Check if day of week matches
    if ($dayOfWeek -notin $rules.daysOfWeek) {
        return $false
    }

    # Handle different time range structures
    if ($year -lt 2021) {
        # Before 2021: Simple array of time ranges for all specified days
        foreach ($timeRange in $rules.timeRanges) {
            if ($timeOfDay -ge $timeRange.start -and $timeOfDay -le $timeRange.end) {
                return $true
            }
        }
    } else {
        # After 2021: Day-specific time ranges
        $dayTimeRanges = $rules.timeRanges.$dayOfWeek
        if ($dayTimeRanges) {
            foreach ($timeRange in $dayTimeRanges) {
                if ($timeOfDay -ge $timeRange.start -and $timeOfDay -le $timeRange.end) {
                    return $true
                }
            }
        }
    }

    return $false
}

# Function to get target folder path
function Get-TargetFolderPath {
    param(
        [string]$FilePath,
        [DateTime]$FileDate
    )

    $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
    $datePattern = $FileDate.ToString("yyyy_MM_dd")

    # Determine base target path
    $basePath = $null
    if ($extension -in $script:Config.fileExtensions.pictures) {
        $basePath = $script:Config.targetPaths.pictures
    }
    elseif ($extension -in $script:Config.fileExtensions.videos) {
        # Check Wudan rules for videos
        if (Test-WudanTimeRules -FileDate $FileDate) {
            $basePath = $script:Config.targetPaths.wudanVideos
        }
        else {
            $basePath = $script:Config.targetPaths.videos
        }
    }
    else {
        Write-Log "Unsupported file extension: $extension for file $FilePath" "WARN"
        return $null
    }

    # Look for existing folder with the date pattern
    $existingFolder = Find-ExistingDateFolder -BasePath $basePath -DatePattern $datePattern

    if ($existingFolder) {
        return $existingFolder
    }
    else {
        # Return the standard date folder path if no existing folder found
        return Join-Path $basePath $datePattern
    }
}

# Function to ensure target directory exists
function Ensure-TargetDirectory {
    param([string]$TargetPath)
    
    if (-not (Test-Path $TargetPath)) {
        if ($script:Config.options.createMissingFolders) {
            try {
                New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
                Write-Log "Created directory: $TargetPath"
                return $true
            }
            catch {
                Write-Log "Failed to create directory $TargetPath`: $($_.Exception.Message)" "ERROR"
                return $false
            }
        }
        else {
            Write-Log "Target directory does not exist and creation is disabled: $TargetPath" "WARN"
            return $false
        }
    }
    return $true
}

# Function to copy file to target location
function Copy-FileToTarget {
    param(
        [string]$SourcePath,
        [string]$TargetPath,
        [string]$FileName,
        [System.IO.FileInfo]$SourceFileInfo
    )

    # Check if file already exists using deduplication cache
    if (Test-FileExistsInTarget -FileName $FileName -FileSize $SourceFileInfo.Length -FileDate $SourceFileInfo.LastWriteTime -TargetDirectory $TargetPath) {
        Write-Log "Skipping duplicate file: $FileName"
        return $true
    }

    $targetFile = Join-Path $TargetPath $FileName

    # Check if file exists at target location (for files not in cache or different location)
    if (Test-Path $targetFile) {
        $sourceSize = $SourceFileInfo.Length
        $targetSize = (Get-Item $targetFile).Length

        if ($sourceSize -eq $targetSize) {
            # If hash comparison is enabled, compare hashes
            if ($script:Config.options.useHashComparison) {
                $sourceHash = Get-FileHashQuick -FilePath $SourcePath
                $targetHash = Get-FileHashQuick -FilePath $targetFile

                if ($sourceHash -and $targetHash -and $sourceHash -eq $targetHash) {
                    Write-Log "File already exists with same hash, skipping: $FileName"
                    return $true
                }
                else {
                    Write-Log "File exists with same size but different hash: $FileName" "WARN"
                }
            }
            else {
                Write-Log "File already exists with same size, skipping: $FileName"
                return $true
            }
        }

        # Create unique filename if sizes differ or hash comparison failed
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
        $extension = [System.IO.Path]::GetExtension($FileName)
        $counter = 1

        do {
            $newFileName = "${baseName}_${counter}${extension}"
            $targetFile = Join-Path $TargetPath $newFileName
            $counter++
        } while (Test-Path $targetFile)

        Write-Log "File exists with different size/hash, creating unique name: $newFileName"
        $FileName = $newFileName
    }

    try {
        if ($script:Config.options.copyFiles -and -not $DryRun) {
            Copy-Item -Path $SourcePath -Destination $targetFile -Force
            Write-Log "Copied: $SourcePath -> $targetFile"

            # Update cache with newly copied file
            $fileKey = "$FileName|$($SourceFileInfo.Length)"
            if (-not $script:ExistingFilesCache.ContainsKey($fileKey)) {
                $script:ExistingFilesCache[$fileKey] = @()
            }
            $script:ExistingFilesCache[$fileKey] += @{
                Path = $targetFile
                LastWriteTime = $SourceFileInfo.LastWriteTime
                Directory = $TargetPath
            }
        }
        else {
            Write-Log "[DRY RUN] Would copy: $SourcePath -> $targetFile"
        }
        return $true
    }
    catch {
        Write-Log "Failed to copy file $SourcePath to $targetFile`: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Function to process files in a directory
function Process-Directory {
    param([string]$SourcePath)

    Write-Log "Processing directory: $SourcePath"

    if (-not (Test-Path $SourcePath)) {
        Write-Log "Source directory does not exist: $SourcePath" "ERROR"
        return
    }

    # Get all supported files recursively
    $allExtensions = $script:Config.fileExtensions.pictures + $script:Config.fileExtensions.videos
    $files = Get-ChildItem -Path $SourcePath -Recurse -File | Where-Object {
        $_.Extension.ToLower() -in $allExtensions
    }

    Write-Log "Found $($files.Count) files to process"

    # Pre-filter files using deduplication if enabled
    $filesToProcess = @()
    $skippedCount = 0

    if ($script:Config.options.enableDeduplication) {
        Write-Log "Pre-filtering files using deduplication cache..."

        foreach ($file in $files) {
            try {
                $fileDate = $file.LastWriteTime
                $targetFolder = Get-TargetFolderPath -FilePath $file.FullName -FileDate $fileDate

                if ($targetFolder) {
                    if (-not (Test-FileExistsInTarget -FileName $file.Name -FileSize $file.Length -FileDate $fileDate -TargetDirectory $targetFolder)) {
                        $filesToProcess += $file
                    }
                    else {
                        $skippedCount++
                    }
                }
                else {
                    $filesToProcess += $file  # Include files with unsupported extensions for error reporting
                }
            }
            catch {
                Write-Log "Error during pre-filtering for file $($file.FullName): $($_.Exception.Message)" "WARN"
                $filesToProcess += $file  # Include problematic files for processing
            }
        }

        Write-Log "Pre-filtering complete. Will process $($filesToProcess.Count) files, skipping $skippedCount duplicates."
    }
    else {
        $filesToProcess = $files
        Write-Log "Deduplication disabled. Processing all $($filesToProcess.Count) files."
    }

    $processedCount = 0
    $errorCount = 0
    $actuallySkippedCount = 0

    foreach ($file in $filesToProcess) {
        try {
            # Get file's last modified date
            $fileDate = $file.LastWriteTime

            # Get target folder path
            $targetFolder = Get-TargetFolderPath -FilePath $file.FullName -FileDate $fileDate

            if ($targetFolder) {
                # Ensure target directory exists
                if (Ensure-TargetDirectory -TargetPath $targetFolder) {
                    # Copy file (this will do final duplicate check)
                    $copyResult = Copy-FileToTarget -SourcePath $file.FullName -TargetPath $targetFolder -FileName $file.Name -SourceFileInfo $file

                    if ($copyResult) {
                        $processedCount++
                    }
                    else {
                        $errorCount++
                    }
                }
                else {
                    $errorCount++
                }
            }
            else {
                $errorCount++
            }

            # Progress reporting
            if ($Verbose -or $script:Config.options.verboseLogging) {
                $totalProcessed = $processedCount + $errorCount
                $progress = [math]::Round($totalProcessed / $filesToProcess.Count * 100, 1)
                Write-Log "Progress: $progress% ($totalProcessed/$($filesToProcess.Count))"
            }
        }
        catch {
            Write-Log "Error processing file $($file.FullName): $($_.Exception.Message)" "ERROR"
            $errorCount++
        }
    }

    # Final statistics
    $totalSkipped = $skippedCount + $actuallySkippedCount
    Write-Log "Directory processing complete."
    Write-Log "  Total files found: $($files.Count)"
    Write-Log "  Files skipped (duplicates): $totalSkipped"
    Write-Log "  Files processed: $processedCount"
    Write-Log "  Errors: $errorCount"

    if ($totalSkipped -gt 0) {
        $timeSavedPercent = [math]::Round(($totalSkipped / $files.Count) * 100, 1)
        Write-Log "  Deduplication saved processing $timeSavedPercent% of files!"
    }
}

# Main execution function
function Main {
    try {
        # Load configuration
        $script:Config = Load-Configuration -ConfigPath $ConfigPath

        # Override config with command line parameters
        if ($DryRun) {
            $script:Config.options.dryRun = $true
        }
        if ($Verbose) {
            $script:Config.options.verboseLogging = $true
        }

        # Initialize logging
        Initialize-Logging

        Write-Log "Starting PhoneSync with configuration from $ConfigPath"

        if ($script:Config.options.dryRun) {
            Write-Log "DRY RUN MODE - No files will be copied" "WARN"
        }

        # Build cache of existing files if deduplication is enabled
        if ($script:Config.options.enableDeduplication) {
            Build-ExistingFilesCache
        }
        else {
            Write-Log "Deduplication is disabled in configuration"
        }

        # Process each source folder
        foreach ($sourceFolder in $script:Config.sourceFolders) {
            Process-Directory -SourcePath $sourceFolder
        }

        Write-Log "=== PhoneSync Completed ===" "INFO"
    }
    catch {
        Write-Log "Fatal error: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# Execute main function
Main
