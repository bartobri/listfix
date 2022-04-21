![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)

Listfix
=======

Listfix is an email list manager for the postfix email server. It is
designed with minimal features to be quick to set up, easy to integrate with
postfix, and simple to create and administer lists.

Listfix allows you to create and manage multiple email lists through a simple
command line interface (CLI). Integration with the postfix email server is
generally only a matter of a couple easy configuration changes (this assumes
you already have postfix installed and configured to send and receive email).

Once integrated, postfix will hand off emails to listfix if the recipient is
an email list address that is configured in listfix. Listfix will then
modify the headers (most importantly, the 'To' header), and
resubmit an new email back to postfix for each recipient in the email list.
Postfix will then deliver the new email to each recipient.

Listfix uses a json database which allows for simple viewing and direct
manipulation via your preferred text editor. This json format also allows for
easy plugin compatibility via custom written scripts or other software.

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
    * [Log and Database Permissions](#log-and-database-permissions)
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

Next add your email list(s) to the file (or resource) that is configured for
virtual_alias_maps. If it is configured similarly to the above example, open
this file and add a new line for each email list you want to manage via listfix.
Each new line should consist of two parts separated by a space. The first
part is the email address for the list. The domain name for this address should
be one that you have previously configured postfix to receive email for. The
second part is a unique id. You can make the unique id anything you want, but
each list must have its own unique id and it must conform to system userid
character requirements. It also can not match any userid on the system. See the
below example:

```
everyone@smith-family.com list-smith-family
```

After you save the changes you will need to rebuild your virtual alias database
and restart postfix:

```
$ sudo postmap /etc/postfix/virtual
$ sudo service postfix restart
```

#### Configure /etc/aliases

Next you need to add an entry to the /etc/aliases file for each unique id you
added to the postfix virtual_alias_maps file. Each entry should start with the
unique id, followed by a colon and space, and then a command that pipes data
to listfix. Be sure to use the listfix 'filter' command followed
by the email address of the list that corresponds to the unique id. See the
example below:

```
list-smith-family: "| /path/to/listfix.py filter everyone@smith-family.com"
```

After saving the changes you will need to rebuild the aliases database:

```
$ sudo newaliases
```

Now postfix will hand off emails to listfix when it receives an incoming 
email addressed to one of the email list addresses configured in postfix's
virtual alias maps.

#### Log and Database Permissions

When postfix hands off an email to listfix, it executes the listfix script in
the process. The userid that postfix uses when it executes listfix needs to
have read/write access to the listfix log and database files. Until you grant
this access, listfix will likely generate read/write errors and will not
function as expected.

Change to the directory that listfix.py resides in. This is the same directory
where listfix creates its database and log files. You should see one of both of
these files.

##### listfix.json

If you have created an email list per the instructions above, you should see the
file listfix.json, which is the database file. Change the permissions to 664 so
that it is both owner and group writable. Next change the group to 'nogroup'
which is the group for the postfix default user 'nobody' that it uses for
handoffs. This will allow the user 'nobody' to write to this file.

```
$ chmod 664 listfix.json
$ sudo chown :nogroup listfix.json
```

##### listfix.log

If you made any errors while creating the database, you will also see the file
listfix.log. If that file does not exist, create it and leave it empty. Next,
make the same permission changes to this file so that the user 'nobody' can
write to it.

```
$ chmod 664 listfix.log
$ sudo chown :nogroup listfix.log
```

Now you should be able to test listfix and confirm it is working as expected.

License
-------

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License. See [LICENSE](LICENSE) for
more details.

Tips
----

[Tips are always appreciated.](https://github.com/bartobri/tips)