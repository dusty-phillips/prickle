Prickle is a simple time tracking app inspired by Freckle. It is intended to
be run in a local one-user setup (there's no auth or user management). It is
pretty intuitive and answers important questions like "how much money did I
make today", and "how many hours did I bill for this project" quickly and
easily. It also handles basic invoicing.

Preparation
============
Make sure these apps are available on your system:
  python
  virtualenv
  mongodb

On Arch Linux, do:
  sudo pacman -S python python-virtualenv mongodb 

All other deps should be pulled into the virtualenv in the install process.

Ensure mongodb is running:
  sudo /etc/rc.d/mongodb start

Installation and Setup
======================
1. Clone the git repo:
    git clone git://github.com/buchuki/prickle.git

2. change into the new repository:
    cd prickle

3. If you don't like living on the edge, select the release tag:
    git checkout v0.3

4. create a virtualenv:
    virtualenv --no-site-packages --distribute env

5. activate the virtualenv:
    source env/bin/activate

6. install the dependencies:
    pip install -r requirements.txt

7. set up the egg links:
    python setup.py develop

8. Optionally edit production.ini to suit your needs. There is one custom
setting in here, database_name that is used in naming mongodb databases.

9. Run the server:
    paster serve --reload production.ini

Usage
=====
Visit http://localhost:5000/ in your web browser. You should probably use a
Webkit browser; I developed Prickle on Chromium, and it kind of expects that
the webkit html5 widgets are available. Try it in Firefox 4 or Opera 11 if you
prefer!

Prickle's primary purpose is time tracking. Select a date, enter a time, enter
a project name and optional type, enter a description, and log it. It's that
simple.

Actually, it's simpler. The time entry field has some extra validation. It
expects data in the form HH:MM to represent the number of hours and minutes you
spent on a given project. However, if it doesn't get a HH:MM format it will
typically do The Right Thing. Decimals such as 1.75 convert to hours and
minutes such as 1:45. Low integers such as 1 or 2 convert to hours such as 1:00
or 2:00. High integers such as 15 or 30 convert to minutes such as 00:15 or
00:30.

The project field features autocomplete and remembers every project you've used
before. Just type a few letters, notice when your project is selected, and
press tab to the next field.

The type field features autocomplete per project. Different types can be billed
at different rates on the invoice. Some common types might be sysadmin,
communication, development, documentation, and research. You could also use
type to distinguish between different aspects of a project on a single invoice,
for example, user interface, backend, and modelling.

The description is freeform. Say whatever you want. You don't have to click the log it button. Just press enter.

To log half an hour these are the keypresses required:
 * time is autofocused on page load.
 * type 30<tab>
 * type pro<tab> to autocomplete a project named project (if you had one ;)
 * press <tab> to leave the type field blank (or enter one)
 * type a description<enter> 
 * Done

The calendar on the right allows you to navigate through dates to see what
items you logged on previous days. The log it form is displayed on each of
these pages, with the correct date selected, so it's easy to log forgotten
hours for previous days. Some browsers will know how to add a date selector to
the widget as well.

The dashborad page includes a summary of all the time you have logged that has
not yet been invoiced. It provides a summary of the number of hours and
your rate for that project. It provides links to see summaries of specific days
or specific projects.

Click on the link for your newly created project. Then click the "edit" link to
set a project rate. This is the amount of money you bill per hour for that
project. Go back to the dashboard and notice how your unbilled time now has a
rate and total applied. If you have multiple lines it will also tell you the
total a top and bottom of the table. You can also set rates for different types
for different projects.

There is a month view (click "This Month" in the menu) to see your time entries
for a given month. You can see at a glance how much you billed for each month.
There is also a per-project view that summarizes the uninvoiced hours.
Navigating between these pages is normally trivial because there are links to
them in the tables. But you can also use the menus.

The last feature is invoicing.  Go to the project page for a given project and
click create invoice.

This creates a simple invoice for you. Select the invoice date, enter an
invoice number (this must be a unique integer. Prickle will try to guess the
next available number and enter it for you, but double check it). Optionally
enter a tax rate. Enter a billing address in the bill to box. Click create.

This will take you to an invoice page summary page that summarizes the lineitems.
You can click the print button to view a printable invoice and pop up a print
dialog. Please edit the templates/invoic.html to make this more suitable to
your use. I'd rather you don't invoice under my name. ;-) It's an html page,
but uses inches for sizing so it is suitable for print based pages.

More importantly, when you create an invoice, uninvoiced hours for that project
are converted to billed hours, and your dashboard and project views will be
reset. Further, there are links to the invoice on the project pages so you can
review old invoices and the timesheets associated with them. The invoices menu
on the top page also gives a good summary.

It is possible to mark hours as billed without creating an invoice; do this
from the project page. This is useful for tracking projects that are not
invoiced (eg: open source development on prickle), or for tracking time on
projects that are invoiced through other means.

Dusty Phillips
dusty@archlinux.ca
