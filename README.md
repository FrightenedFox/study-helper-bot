# PRz Data Analysis Bot

Telegram bot for student cooperation and communication. At least that was the original idea, but due to the lack of time, the final version of the bot can only:

- authenticate user with USOS API
- download all information about user lectures to the local database
- inform the user of his schedule for the next few days
- inform the user about the schedule for a specific subject

This project is a part of the curriculum in *"Databases"* of the Rzeszow University of Technology, Poland. A detailed description of the project can be found in the [`DocumentationPL.pdf`](https://github.com/FrightenedFox/study-helper-bot/blob/main/DocumentationPL.pdf) file.


## Installation steps

### Python

Clone the files of the project
```shell
git clone https://github.com/FrightenedFox/study-helper-bot study_helper_bot
cd study_helper_bot
```

Create and activate a new venv environment
```shell
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate
```

Install project dependencies and packages in editable mode
```shell
python3 -m pip install -e .
```

If you want to recreate an exact same environment of the developers, you also need to run the following command:
```shell
python3 -m pip install -r requirements_dev.txt
```

### Config

Create a copy of the config example, which you can find at `src/studyhelperbot/config/config_example.ini`, and put it to the same folder. You may want to change the `logging` and `rethinkdb` sections or `admin_password` value in the `rethinkdb-setup` section. At this point don't touch other settings, we'll get back to them later.

### PostgreSQL

Configure the PostgreSQL server. You need to create a database and a dedicated user for the bot. This [guide from ArchWiki](https://wiki.archlinux.org/title/PostgreSQL#Installation) may be useful.

Now you need to fulfill the `postgresql` section in the config file and run `StudyHelperBotDB.sql` script.

### RethinkDB

Install `rethinkdb` from the [official repositories](https://rethinkdb.com/docs/install/).

Create and set user rights for RethinkDB folder (**warning:** examples are given for Arch based GNU/Linux systems, some commands may very for different distributions):

```shell
rethinkdb create -d "/var/lib/rethinkdb/aiogramStorage/"
chown -R rethinkdb:rethinkdb /var/lib/rethinkdb/
```

Start RethinkDB service:

```shell
systemctl enable --now rethinkdb@aiogramStorage.service
```

Run `src/studyhelperbot/rethinkdb_setup.py` script, which will set up a password for the administrator as well as create database, table and user using values from the config file.

```shell
cd studyhelperbot/src/studyhelperbot
python3 rethinkdb_setup.py
```

### Telegram

Create a new Telegram bot using [Father Bot](https://telegram.me/BotFather) (`@BotFather`). Paste its API Token to
the `bot` section of the config file.

### USOS API

Create your OAth `consumer_key` and `consumer_secret` using [USOS Apps developer center](https://usosapps.prz.edu.pl/developers/). Paste them to the `usosapi` section of the configuration file. 

### Done

Assuming you installed everything correctly and your current working directory is the source directory of the project (`study_helper_bot/src/studyhelperbot`), you can run `bot.py` module and everything should be set up!

```shell
python3 bot.py
```
