# Banks, Loans and Simulations

## Description

This is a CLI application that allows you to create users, loans and administrate them via admin panel. By default the application will create 10 random users with that have some loans and some money on their savings account. When the demo DB is populated - user can log in to their system and make actions in their account like deposit, withdraw, take or pay loans. Bank keeps track of the available amount of money and must never go bankrupt (by giving our more loans that there is money and/or disallowing users to withdraw money). The bank administrator can run simulation to see what would be the health status of the bank in a few month.

## How to run

1. Clone this repository
2. Make sure Python 3.9+ is installed
3. Install requirements: `pip install -r requirements.txt`
4. Run `python main.py`

## How to make an executable

Install pyinstaller: `pip install pyinstaller`. Then, depending on your OS, run one of the following commands.
Note that PyInstaller supports making executables for Windows, Linux, and macOS, **but it cannot cross compile**. So, to
distribute executables for multiple types of OS, you’ll need a build machine for each supported OS.

### Linux & MacOS

After you have cloned this repository and installed requirements, run the following command in the root
directory of the project.

```bash
pyinstaller --onefile --name 'Bank Executable MacOS' main.py
```

After that, you will find an executable in the `dist` folder.

### Windows

To generate an executable for Windows, run:

```bash
pyinstaller --onefile --name 'Bank Executable Windows' main.py
```

After that, you will find an executable in the `dist` folder.
