# OTP Manager
## Overview
The OTP Manager is a Python application that provides a graphical user interface (GUI) for managing one-time passwords (OTPs) using time-based (TOTP) or counter-based (HOTP) algorithms. The application is built with Tkinter for the GUI and integrates libraries like pyotp for OTP generation and qrcode for generating QR codes.

## Features
* Add OTP: Create a new OTP using either TOTP or HOTP.
* Generate Secret Key: Automatically generate a Base32-encoded secret key for OTPs.
* View OTPs: Display all added OTPs with their corresponding codes.
* QR Code Generation: Generate and display QR codes for each OTP, which can be scanned by an authentication app.
* Automatic OTP Updates: Refresh OTP codes at regular intervals for time-based OTPs.
* Support for both TOTP and HOTP: Allows switching between time-based and counter-based OTPs.
## Prerequisites
Before running the application, ensure you have the following dependencies installed:
```bash
pip install -r requirements.txt 
```

## How to Use
1. Running the Application

Run the main Python script to launch the OTP Manager:

```bash
python runner.py
```

2. Adding a New OTP
* In the GUI, enter a label to identify the OTP.
* Generate or input a secret key (Base32 encoded).
* Choose whether the OTP should be time-based (TOTP) or counter-based (HOTP).
* For HOTP, a counter value must be provided.
3. Viewing OTPs

Once an OTP is added, it will be displayed in the main window. For TOTP, the OTP code will refresh every 30 seconds. For HOTP, the counter is incremented manually.

4. Generating QR Codes

Click the Generate QR button for any added OTP to display a QR code that can be scanned by an authentication app like Google Authenticator or Authy.

5. Deleting an OTP

To remove an OTP from the list, click the Delete button next to the respective OTP.

6. HOTP Counter Management

If you're using HOTP, click the Generate button to increment the counter and generate the next OTP.

## Configuration
The application uses several configurable parameters:

* Title: The window title of the application (title).
* Window Geometry: Defines the size of the main application window (geometry).
* QR Code Path: Directory where QR codes will be saved (qrcodes_path).
* OTP Interval: Time in seconds for TOTP to refresh (seconds).
These can be adjusted in the variables.py file.

## Requirements
Python 3.6 or higher
Tkinter (comes pre-installed with Python)