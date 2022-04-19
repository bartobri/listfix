![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)

Listfix
=======

Listfix is a simple email list manager built with python for the postfix email
server. It is intended to be simple to set up and administer. Listfix simply 
receives email from postfix that is addressesed to a configured email list and
replicates that email to all list recipients in it's database.

Most of the origninal email headers are stripped and replaced such that the
replicated email is properly addressed as having been generated and sent by your
email server, with the "From" field having the same user@domain as the email
list itself. This is necessary to avoid the email being flagged as spam.

Listfix allows you to create multiple email lists, add and remove recipients,
and review the contents of lists through a simple command line interface (CLI).
As an alternative to the CLI, the Listfix database is stored in json format
allowing for simple viewing and manipulating of the list data via your preferred
text editor. This json format also allows for easy plugin capaibility via
custom written scripts or other software.

Table of Contents
-----------------

1. [Download](#download)
2. [Usage](#usage)
    * [Create a new email list](#create-a-new-email-list)
    * [List all email lists](#list-all-email-lists)
    * [Add a recipient to an email list](#add-a-recipient-to-an-email-list)
    * [List all recipients in an email list](#list-all-recipients-in-an-email-list)
    * [Remove a recipient in an email list](#remove-a-recipient-in-an-email-list)
    * [Destroy an email list](#destroy-an-email-list)
3. [Postfix Integration](#postfix-integration)
    * [Configure virtual_alias_maps](#configure-virtual_alias_maps)
    * [Configure /etc/aliases](#configure-etcaliases)
4. [License](#license)
5. [Tips](#tips)

Download
--------

#### Requirements:

This project was built using python version 3.7. It has not been tested with
lower versions. I suggest using at least python 3.7 to avoid any potential
issues.

#### Download from git:
```
$ git clone git@github.com:bartobri/listfix.git
```

Usage
-----

Basic Usage: `listfix.py <command> [<arg_1>,<arg_2>,...]`

After downloading the listfix git repo, cd to the listfix directory. Next use
the following commands to create and manage your email list database.

We'll be using the example everyone@smith-family.com for our email list address.

#### Create a new email list

Usage: `listfix.py create <email_list_address> <email_list_name>`

```
$ ./listfix.py create everyone@smith-family.com "Smith Family"
New list (everyone@smith-family.com) added.
$
```

#### List all email lists

Usage: `listfix.py lists`

```
$ ./listfix.py lists
everyone@smith-family.com (Smith Family)
$
```

#### Add a recipient to an email list

Usage: `listfix.py add <email_list_address> <recipient_address> <recipient_name>`

```
$ ./listfix.py add everyone@smith-family.com mom@example.com "Sue Smith"
New recipient (mom@example.com) added to list (everyone@smith-family.com)
$ ./listfix.py add everyone@smith-family.com dad@example.com "Bob Smith"
New recipient (dad@example.com) added to list (everyone@smith-family.com)
$ ./listfix.py add everyone@smith-family.com me@example.com "Joe Smith"
New recipient (me@example.com) added to list (everyone@smith-family.com)
```

#### List all recipients in an email list

Usage: `listfix.py dump <email_list_address>`

```
$ ./listfix.py dump everyone@smith-family.com
mom@example.com (Sue Smith)
dad@example.com (Bob Smith)
me@example.com (Joe Smith)
$
```

#### Remove a recipient in an email list

Usage: `listfix.py remove <email_list_address> <recipient_address>`

```
$ ./listfix.py remove everyone@smith-family.com mom@example.com
Recipient (mom@example.com) removed from list (everyone@smith-family.com)
$
```

#### Destroy an email list

Usage: `listfix.py destroy <email_list_address>`

```
$ ./listfix.py destroy everyone@smith-family.com
Email list (everyone@smith-family.com) destroyed
$
```

Postfix Integration
-------------------

These instructions assume you have the postfix email server set up on a unix or
linux system and you have virtual domain settings enabled. Setting up and
the postfix email server is not within scope for these instructions.

#### Configure virtual_alias_maps

Confirm that the virtual_alias_maps configuration setting exists in the postfix
main.cf config file. If it does not exist, you will have to add it. A common
setting looks something like this:

```
virtual_alias_maps = hash:/etc/postfix/virtual
```

Next add your email list(s) to the file (or resource) that if configured for
virtual_alias_maps. Open this file and add a new line for each email list you
want to manage via listfix. Each new line should consist of two parts. The first
part is the email address for the list. The second part is a unique id. You can
make the unique id anything you want, but each list must have its own unique id
and it must conform to system userid character standards. It also can not match
any userid on the system. See the below example:

```
everyone@smith-family.com list-smith-family
```

After you save the changes you will need to rebuild your virtual alias database
and restart postfix:

```
sudo postmap /etc/postfix/virtual
sudo service postfix restart
```

#### Configure /etc/aliases

Next you need to add an entry to the /etc/aliases file for each unique id you
added to the postfix virtual_alias_maps file. Each entry should start with the
unique id, followed by a colon and space, and the a command that pipes data
to listfix. You should be sure to use the 'filter' command for listfix followed
by the email address of the list that corresponds to the unique id. See the
example below:

```
list-smith-family: "| /path/to/listfix.py filter everyone@smith-family.com"
```

After saving the changes you will need to rebuild the aliases database:

```
sudo newaliases
```

Now postfix will pipe emails through listfix when it receives an incoming 
email addressed to one of the addresses configured in postfix's virtual
alias maps. Postfix will then replicate the contents of the email to all the
recipients for the email list.

License
-------

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License. See [LICENSE](LICENSE) for
more details.

Tips
----

[Tips are always appreciated.](https://github.com/bartobri/tips)