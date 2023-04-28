### We are developing a nice notification system for your cashflow!

#### TODO List
  - [x] internal notification
  - [x] external notification
    - [x] trigger logic
    - [x] build emails
    - [x] set msgs in json
    - [x] set variables in msgs
    - [x] select right tone
    - [x] ~~separate intimation contact~~ don't use intimation tone
    - [x] configure email msgs
    - [x] add payement link
    - [x] update external notif status 
    - [x] format amount with two decimals
    - [x] add installment in mails
  - [x] use unique key instead of invoice id
    - [x] consider installments
    - [x] consider recurrent pays
  - [x] configure fili mailbox as sender
  - [x] receive arguments to identify client
    - [x] looker configuration path
  - [x] format:
    - [x] format amount in html tables
    - [x] format date in html tables

#### Bugs
  - [x] smtp fails in cloud function if recipient doesn't exist
  - [x] smtp fails if mail address has no correct format
  - [x] BQ query updates are not check to have run ok
   
Diagram: 
![send_notif_diagram](https://user-images.githubusercontent.com/84101337/231532890-990dc944-647a-43c9-b28b-653986f9da40.png)
