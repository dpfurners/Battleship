# Battleship
  Software Engineering project using the SCRUM-Development

## Task 

Screen:
 - Enemy
 - Own Ships (under enemy)
 - Statistics (All) + Ship Graphic (Next to Enemy and Own Ships)

Functions:
 - Network Client (Lobby System)
    - Join When match (not random)
 - Scoreboard
    - Who won most games (unsure how i want it)
 - Field in Background
    - 2D Array

Size:
 - Field 12x12 (can be custom)
 - Screen max. 1024x768

Ships (Which):
 - 1x 2x4 (With two edges missing -> Aircraft Carrier)
 - 2x 3x1 (Frigate)
 - 3x 2x1 (Cruiser)
 
Questions:
 - Sounds?
 - Random Placement?
 - Sprints in the README.md or in another Folder

## Sprint 1

Result: Working Login/Registration with DB Integration

 - Setup Database (Dominik)
  - What data should be stored?
  - Normalization
  - API?
 - Login/Registration? Screen (Emanuel)
  - Login GUI/Registration GUI
  - Output to get the Username/Password
 - Basic Client-Server Setup (Aleks)
  - Client is able to connect to the server
  - Server receives Login and Calls Database Login
  - Server Returns Client Model to the Client (dataclass)
