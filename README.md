# Assignement 2

## Table of Contents

- [Assignement 2](#assignement-2)
  - [Table of Contents](#table-of-contents)
  - [Usage :](#usage-)
    - [Install](#install)
    - [Run](#run)
  - [Features](#features)
  - [Design considerations](#design-considerations)
    - [Database](#database)
    - [Security](#security)
    - [Code](#code)
      - [Structure](#structure)
      - [Handling messages](#handling-messages)
  - [Possible improvements](#possible-improvements)
  - [The Question](#the-question)
    - [Threat model – who might attack the application? What can an attacker do? What damage could be done (in terms of confidentiality, integrity, availability)? Are there limits to what an attacker can do? Are there limits to what we can sensibly protect against?](#threat-model--who-might-attack-the-application-what-can-an-attacker-do-what-damage-could-be-done-in-terms-of-confidentiality-integrity-availability-are-there-limits-to-what-an-attacker-can-do-are-there-limits-to-what-we-can-sensibly-protect-against)
      - [Threat agents](#threat-agents)
      - [Impact](#impact)
      - [Likelyhood](#likelyhood)
      - [Controls, Preventions & Mitigations](#controls-preventions--mitigations)
    - [What are the main attack vectors for the application?](#what-are-the-main-attack-vectors-for-the-application)
      - [XSS](#xss)
      - [CSRF](#csrf)
      - [SQL injection](#sql-injection)
      - [Insecure design](#insecure-design)
        - [Authentication](#authentication)
        - [Authorization](#authorization)
        - [Plaintext secret](#plaintext-secret)
        - [One-filer](#one-filer)
        - [Login's Next](#logins-next)
        - [Spam vulnerability](#spam-vulnerability)
        - [Logging private data](#logging-private-data)
    - [What should we do (or what have you done) to protect against attacks?](#what-should-we-do-or-what-have-you-done-to-protect-against-attacks)
      - [XSS](#xss-1)
      - [CSRF](#csrf-1)
      - [SQL injection](#sql-injection-1)
      - [Insecure design](#insecure-design-1)
        - [Authentication](#authentication-1)
        - [Authorization](#authorization-1)
        - [Plaintext secret](#plaintext-secret-1)
        - [One-filer](#one-filer-1)
        - [Login's Next](#logins-next-1)
        - [Spam vulnerability](#spam-vulnerability-1)
        - [Logging private data](#logging-private-data-1)
    - [What is the access control model?](#what-is-the-access-control-model)
    - [How can you know that you security is good enough? (traceability)](#how-can-you-know-that-you-security-is-good-enough-traceability)

## Usage :

### Install

- (Optional) Setup your python environemen  
```shell
conda create INF226-serve
conda activate INF226-serve
```
- Install dependencies
```shell
pip install -r requirement.txt
```
- (Strongly Recomended) setup the variable in the `.env`
```shell
cp .env.example .env
nano .env
```

### Run

- Run the server
```shell
flask run
```
- go to [http://localhost:5000/](http://localhost:5000/) to see the result

## Features

This is a very basic message board. 

- [x] Create a user
- [x] Login
- [x] Create a message with multiple recipients
- [x] Get all my messages
- [x] Get all the messages I sent
- [x] Delete a message
  - [x] Sender deleting the message for all
  - [x] Recipient discarding the message
- [x] Markdown support
- [x] NO coffee support

## Design considerations

### Database

To keep the app simple we use a sqlite database. This is not a good choice for a production app but it is good enough for this assignment.

### Security

For security we tended to rely on the work of the framework and other reputable python modules. It is not a good idea to reinvent the wheel. 

We use the `flask-login` extension to handle the login and the session. This is a good extension that is well maintained which reduce the chance of introducing the bug. The `@require_login` decorator is usefull to make sure that authorisation is correctly implemented.

We use `bcrypt` to hash and check the password.

We use `flask-wtf` to handle the form. It handles the CSRF token and the validation of the form. Which is a good way to avoid the most common security issues(CSRF, nad input...).

We made sure to use the right method for each route. It help to avoid XSS security issues.

We used the predefined sql statements to avoid SQL injection.

We made sure to escape the user input before displaying it using `DOMSanify`.

### Code

*Note : Not much to say it's a server*

#### Structure

The code is split between files associated with the different routes. 

- `app.py` is the main file. It contains the app creation and the connection to the database.
- `src/` contains the different routes. 
  - `coffees.py` contains the routes for the coffee requests.
  - `messages.py` contains the routes related to messages (creation, deletion, list...).
  - `static.py` contains the routes for the static files.
  - `users.py` contains the routes related to users (creation, login, logout...), the `User` class and the authentication logic.
  - `forms/` contains the different forms used in the app.
- `templates/` contains the html templates.
- `static/` contains the static files (css, js, images...).

#### Handling messages

We made sure to check the authorisation of the user for each route : 
- a user can create a message only if he is logged in and if he hasnt reached the limit of messages.
- a user can delete a message only if he is the sender or the recipient.
  - if he is the sender he can delete the message for all the recipients.
  - if he is the recipient or the sender he can discard the message.
- a user can get a message only if he is the sender or the recipient.
- a user can get a list of his inbox and sent messages only if he is logged in.

## Possible improvements

- [ ] Move the database to it's own file
- [ ] Integrate reCaptcha to avoid spam / Use email confirmation
- [ ] Add a way to delete a user account

## The Question

### Threat model – who might attack the application? What can an attacker do? What damage could be done (in terms of confidentiality, integrity, availability)? Are there limits to what an attacker can do? Are there limits to what we can sensibly protect against?

#### Threat agents 

- malicious users
- spam bots
- spies

#### Impact

- confidentiality : 
  - the attacker can read the messages of other users
- integrity : 
  - the attacker can modify the messages of other users
  - the attacker can masquerade as another user
  - the attacker can fake an announcement
- availability : 
  - the attacker can delete the messages of other users
  - the attacker can create a lot of messages to make the server unavailable
  - the attacker could use the database to store mallicious data

#### Likelyhood

If the application is used. An attack is certain

#### Controls, Preventions & Mitigations

Nothing nada zilch. The only limit is the imagination of the attacker.

The main limitation is the clearly insecure apearance of the application which makes users less likely to use it. 

### What are the main attack vectors for the application?

#### XSS

The application is vulnerable to XSS. The user input is not sanitized before being displayed or being stored. If you escape the input correctly you can inject javascript code in the page.

e.g.
```
<img src=\"x\" onerror=\"alert()\"></img>
```

#### CSRF

The application use GET request to send messages which mean you can trick the user into sending a message(a bit overkill considering the other porblems).

#### SQL injection

As the application doesnt sanitize the user input before sending it and doesnt use prepared statements it is vulnerable to SQL injection. 

e.g.
```
1' OR 1=1; CREATE TABLE Coffees(name TEXT) ; INSERT INTO coffees VALUES ('arabica'); --
```

#### Insecure design

##### Authentication

The authentication didnt check the password. It only checked if the user exist. This mean that an attacker can masquerade as another user. The users are also stored in plain text in the source code. This mean that an attacker can get the list of users and their password.

##### Authorization

The authorization is lax, it only check that a user is logged in before displaying the chat page. If an attacker as access to the application he can see all messages and send message as an other person.

##### Plaintext secret

The secret key is stored in plain text in the source code. This mean that an attacker can get the secret key and decrypt the session cookie.

##### One-filer

While craming in a single file is not a security issue in itself, it makes the code harder to read and maintain. which make it more likely to introduce security issues.

##### Login's Next

The login page doesnt check the next parameter. This mean that an attacker can redirect the user to a malicious page after login. It would be less of a problem used the correct method for each route. But as the application use GET request for everything it is a problem. 

##### Spam vulnerability

Since the `send` route is totaly unprotected the site is vulnerable to bot. This mean that an attacker can create a lot of messages to make the server unavailable. 

##### Logging private data

The application log the user password in plain text. Even the admin shouldnt have access to the password of user.

### What should we do (or what have you done) to protect against attacks?

#### XSS

We used `DOMSanify` to sanitize the user input before displaying it. This way we can be sure that the user input is safe to display. We also try to get most of our data from the server and not from the user. This way we can be sure that the data is safe to display.

#### CSRF

We make sure to use the correct method for each route. This way we can be sure that the user input is safe to use. We also use `flask-wtf` to handle the form. It handles the CSRF token and the validation of the form. 

#### SQL injection

We always use the predefined sql statements to avoid SQL injection. 
```python
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

#### Insecure design

##### Authentication

We made sure to hash the password before storing it in the database. We also made sure to check the password when the user login. They was a bearer token authentication but it was removed because it was not used. We made sure that we were using flask-login correctly.

##### Authorization

We properly defined the access rights to the resources and applied them to each routes for each user.

##### Plaintext secret

We moved the secret key to an environment variable. This way it is not stored in the source code.

##### One-filer

We split the code in multiple files. This way it is easier to read and maintain.

##### Login's Next

We made sure to check the next parameter. This way we can be sure that the user is redirected to a safe page.

##### Spam vulnerability

We added a limit to the number of messages a user can send. This way we can be sure that the user cant spam the server with message.

**Note** *The application is still vulnerable to spam. The limit only applies to messages. An attacker could easily spam the database with new users. This would make the server unavailable. The only way to prevent this is to use a captcha or to send an email confirmation.*


##### Logging private data

Just don't.

### What is the access control model?

The access control model is simple the application only requires a monolitique user and the user can only access the message resource.

A user can : 
- create a message if he hasnt reached the limit of messages.
- delete a message if he is the sender or the recipient.
  - if he is the sender he can delete the message for all the recipients.
  - if he is the recipient or the sender he can discard the message.
- access a message if he is the sender or the recipient.

### How can you know that you security is good enough? (traceability)

We can use the log of the server to detect unusual activity. 

We expect the server to be used by humans. If we see a lot of activity we can suspect that something is wrong. 

A standard user should not be raising certain exceptions. If we see a lot of exceptions it's likely due to an attacker.

We can also track failed login attempts. Failing to connect 20 times in a row should definitely raise a red flag.

We should also make a way to contact the maintainer of the application. Because logging is not sufficient to detect all the attacks. So it is import for the users to have a way to raise the alarm.