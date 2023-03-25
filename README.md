# VAULT MANAGER

#### Video Demo:  <https://youtu.be/oFV0jUqqrug>

#### Description

The vault manager is a web application that can help foreign exchange companies manage their cash flows from the bank to the supervisors,
from the supervisors to the tellers and from the tellers to the customers.
It can help the management to be able to know the current running balance of their respective zones and branches.
They will be able to ascertain the current balance of their branches and closing balances so as to know the amount to be withdrawn from the bank
to be used as an opening balance for the next business day.

## How It Works

In the morning the vault manager will send a withdraw request to the management with the amount through the software. The finance department will
look at yesterdays closing balances and make judgement as to what amount should be withdrawn. When his or her withdrawal request is accepted,
the money will be withdrawn from the bank and credit the main vault account in the software. The vault manager will used this amount to credit
supervisors accounts as opening balances. The supervisors in turn will use this amount to credit the account of the tellers.

Inputs to the system would be done from the vault management level, where the opening and additional amounts would be entered by the
supervisors. All cash distributions would be debited from the Vault of the respective zone and credited to the respective branches.
The system would not be limited to the supervisors only but would be extended to the cashiers as well.
During the cash distribution, the cashiers would request the cash from their supervisors, the supervisors will now credit their accounts
for their opening balances which will in turn debit the supervisor’s account.

In the mid of the day, the vault manager will assess the accounts of the supervisors and see who needs an additional cash for operation.
If theirs any, that agents account will be credited as an additional cash. These credits will deduct or debit the main vault account in the software.

The supervisors at the interior part of the country can also send a withdrawal request and use it for their operations.

At the end of the day, the tellers will return their closing balances to their supervisors and reset their account balance to 0.0.
The supervisors will also return their account balance to the vault and credit the main vault account. They will send this report with the 
cash given to them as both opening and closing balance along with the currencies they traded to for that day and their closing balances.

The dashboard will display the main vault account balance and the respective zones opening, additional and closing balances.

## Components

### Accounts

The accounts package contains a forms.py file that contains the Creation and an update of a vault account.
The routes.py file contains routes to return the available accounts and their properties. It also has routes to create and update accounts.

### Branches

Same as the accounts package, the branches package also contains a forms.py routes to return the available branches and create and edit branches.

### Deposits

The deposits package contains forms and routes to return both the deposits of cashiers and supervisors. It also implements routes to
approve and disapprove deposits and a refund route to help correct mistaken deposits.

### Errors

The errors package contains custom error handling routes which renders templates to the most common types of error
which helps in handling errors that the software may encounter in a more user-friendly manner.
It handles a 403 forbidden error, 404 not found error and 500 server error in a more visual and readable approach.

### Instance

This contains the site.dB file which is a SQLite database using ORM to store the data of the app.

### Main

The main module contains routes to render information on the dashboard, set a time limit to the session of the current user,
run a d.create_all() to create the tables, a home to route to determine where the current user should be redirected to,
a movement route to keep track of all the activities of then agents. It also provides a route to display all the current registered users.
It also provides a utils.py file to help fetch information to be rendered on the dashboard and also helps format the currency.

### Reports

The reports package contains form to send reports and modify these reports. The routes file contains routes to send, approve and delete reports.
It also provides all the daily reports reported by the supervisors and cashiers in a different route. It also provides generations routes
to help generate reports in csv file for download. Be it the daily cashier reports or supervisor reports or the withdrawals reports etc.

### Users

The user’s module contains forms and routes for users’ registration and management.
It also provides routes where users can view their profile information and also make changes to them and give the admin full access to
change a user’s branch, zone, authorization level and password or even delete a user.
The utils.py implements functions to save the user's profile picture and also a function to generate a random agent code for the user.
It has routes via which users can view their reports that they have submitted.

### Vault

This is the heart of the program it contains the static directory for the static files, the templates directory for the templates
and also, the config file to store the configuration of the application. It also provides a models.py file to help in Object Relational Mapping
It stores all the models of the program.

### Withdrawals

This provides functions to withdraw cash, view the withdrawal transactions, approve and reject these withdrawals.
When an agent sent a withdrawal request, an email will be sent to the admin that so and so is requesting for such an amount of money
and a link to approve or reject the request will be sent to the him. When the request is approved or rejected, the agent will receive an email
about the status of his / her request.

### Zones

The zones package like the branches, also provides the functionality of creating and updating zones and also assigning them to their managers.
It also provides all information about the zone, their opening, additional and closing balances.

### Requirements.txt

This contains all the packages and modules used in building the project.

### Run.py

The engine which let you run the program from a development environment.
