# SecretSanta
Auto-assign Secret Santa/Mystery Maccabee participants  and/or categories randomly
Usage:
```
python secretSanta.py -h
usage: secretSanta.py [-h] -c CATEGORIES -p PARTICIPANTS [-o]
                      [-of OUTPUT_PATH] [-v] [-vv]

optional arguments:
  -h, --help            show this help message and exit
  -c, --categories      New-line separated list/comma separated list of categories
  -p, --participants    New-line separated list/comma separated list of participants/CSV  of participant, email
  -o, --output_files    Output each participant's assignments to a separate
                        file
  -of, --output_path    Change directory to save files
  -v, --verbose         Set logging level to info
  -vv, --very_verbose   Set logging level to debug
  
```
Example:
```
python secretSanta.py -p participants.txt -c categories.txt -o
```
