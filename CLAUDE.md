# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Python/tkinter GUI application that creates NoSpamProxy tenants by constructing and executing PowerShell commands via `subprocess`. Designed to run on Windows (requires PowerShell with the NoSpamProxy module installed).

## Running the script

```bash
python tenant-creation-script.py
```

Requires Python 3 with `tkinter` (standard library). On Windows, PowerShell must have access to `connect-nsp` and `New-NspTenant` cmdlets from the NoSpamProxy module.

## Architecture

Single-file script (`tenant-creation-script.py`) with two concerns:

1. **GUI** — built with `tkinter`, defined in module-level code after the `create_tenant` function. Labels and error messages are in German.
2. **Execution** — `create_tenant()` reads all field values, validates them (no spaces in tenant name, required fields), then builds a multi-line PowerShell script string and runs it via `subprocess.run(["powershell", "-Command", ...])`.

The PowerShell command calls `connect-nsp -IgnoreServerCertificateErrors` followed by `New-NspTenant` with the form values interpolated directly into the command string.
