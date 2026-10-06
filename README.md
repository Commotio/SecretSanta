# SecretSanta
Auto-assign Secret Santa/Mystery Maccabee participants  and/or categories randomly
usage: 
```
secretSanta.py [-h] [-c CATEGORIES] -p PARTICIPANTS [-o]
                      [-of OUTPUT_PATH] [--send_emails]
                      [--email_template EMAIL_TEMPLATE] [-v] [-vv]

optional arguments:
  -h, --help            show this help message and exit
  -c CATEGORIES, --categories CATEGORIES
                        File or comma-separated list of categories
  -p PARTICIPANTS, --participants PARTICIPANTS
                        File or comma-separated list of participants
  -o, --output_files    Save assignments to files
  -of OUTPUT_PATH, --output_path OUTPUT_PATH
                        Directory to save files (Requires -o)
  --send_emails         Send emails
  --email_template EMAIL_TEMPLATE
                        Path to HTML email template
  -v, --verbose
  -vv, --very_verbose
  
```
Example:
```
python secretSanta.py -p participants.txt -c categories.txt -o
```
