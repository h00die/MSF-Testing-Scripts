# General Settings

| Description     | JtR            | hashcat           |
|-----------------|----------------|-------------------|
| session         | --session      | --session         |
| no logging      | --nolog        | --logfile-disable |
| config file     | --config       | (n/a)             |
| previous cracks | --pot          | --potfile-path    |
| type of hashes  | --format       | --hash-type       |
| wordlist        | --wordlist     | (last parameter)  |
| incremental     | --incremental  | --increment       |
| rules           | --rules        | --rules-file      |
| max run time    | --max-run-time | --runtime         |
| show results    | --show         | --show            |

# Hash Setting

| Hash              | JtR john --list=formats |  hashcathashcat -h |
|-------------------|-------------------------|--------------------|
| des               | descrypt                | 14000              |
| md5               | md5crypt                | 500                |
| sha1              |                         | 100                |
| bsdi              | bsdicrypt               | 12400              |
| sha256            | sha256crypt             | 7400               |
| sha512            | sha512crypt             | 1800               |
| blowfish          | bcrypt                  | 3200               |
| lanman            | lm                      | 3000               |
| NTLM              | nt                      | 1000               |
| mssql (05)        | mssql                   | 131                |
| mssql12           | mssql12                 | 1731               |
| mssql (2012/2014) | mssql05                 | 132                |
| oracle (10)       | oracle                  | 3100               |
| oracle 11         | oracle11                | 112                |
| oracle 12         | oracle12c               | 12300              |
| postgres          | dynamic_1034            | 12                 |
| mysql             | mysql                   | 200                |
| mysql-sha1        | mysql-sha1              | 300                |
