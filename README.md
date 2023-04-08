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
  - [ ] use unique_key instead of invoice_id
    - [ ] consider installments
    - [ ] consider recurrent pays
  - [ ] configure fili mailbox as sender
  - [x] receive arguments to identify client
    - [x] looker configuration path

#### Bugs
  - [ ] smtp fails in cloud function if recipient doesn't exist