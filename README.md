# Battleship
  Software Engineering project using the SCRUM-Development

## Current State (Sprint 2)
    - Matchmaking is done
    - Game-Window is done
    - Ships can be placed (The colissions detection is not right already)
      So the ships that want to be changed will be placed ontop of each other

    overall: everything is done except the game logic when someone is shooting/win condition 

## How to test it:
    1. Start the Server
    2. Start at least two Client (it needs two clients to be able to start a game)
    3. Log in with your credentials
    4. Click on a player you want to match with
    5. The game starts and the ships can be placed
       - the ships are placed randomly at the beginning
       - select a ship you want to move on the statistics screen
       - click on the field you want to place the ship
       - press [r] to rotate the ship

## Task 

#### Screen:
    - Enemy
    - Own Ships (under enemy)
    - Statistics (All) + Ship Graphic (Next to Enemy and Own Ships)

#### Functions:
    - Network Client (Lobby System)
      - Join When match (not random)
    - Scoreboard
      - Who won most games (unsure how i want it)
    - Field in Background
      - 2D Array

#### Size:
    - Field 12x12 (can be custom)
    - Screen max. 1024x768

#### Ships (Which):
    - 1x 2x4 (With two edges missing -> Aircraft Carrier)
    - 2x 3x1 (Frigate)
    - 3x 2x1 (Cruiser)
