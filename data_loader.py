import json
import time
import requests

# Server address
API_URL = "http://localhost:8000"

# Sample data
sample_policy_content = """
DATA PRIVACY POLICY

Last Updated: April 1, 2025

1. INTRODUCTION

Welcome to our Data Privacy Policy. This policy explains how we collect, use, and protect your personal information when you use our services.

2. INFORMATION WE COLLECT

We may collect the following types of information:
- Personal information such as name, email address, and contact details
- Usage information about how you interact with our services
- Device information including IP address and browser type
- Cookies and similar tracking technologies

3. HOW WE USE YOUR INFORMATION

We use your information to:
- Provide and improve our services
- Communicate with you about updates or changes
- Personalize content and recommendations
- Maintain security and prevent fraud

4. DATA SHARING AND DISCLOSURE

We may share your information with:
- Service providers who help us deliver our services
- Legal authorities when required by law
- Business partners with your consent

5. YOUR RIGHTS AND CHOICES

You have the right to:
- Access your personal information
- Correct inaccuracies in your data
- Delete your data in certain circumstances
- Opt out of marketing communications

6. SECURITY MEASURES

We implement appropriate technical and organizational measures to protect your personal information.

7. INTERNATIONAL TRANSFERS

Your information may be transferred to countries with different data protection laws.

8. RETENTION PERIOD

We will retain your information only for as long as necessary to fulfill the purposes outlined in this policy.

9. CHANGES TO THIS POLICY

We may update this policy from time to time. We will notify you of any significant changes.

10. CONTACT US

If you have any questions about this policy, please contact us at privacy@example.com.
"""

# Save the policy content to a file
with open("sample_policy.txt", "w") as f:
    f.write(sample_policy_content)

print("Generated sample policy file")

# Add code to upload via API (if needed)
print("Set up data complete. You can now interact with the UI to see the features.")
