LudumDare game

# TODO

## Done

* Timer - spawn new wave at the end
    * Button to start next round
* Ammo
* Roll buttons
* Game state forcing you to:
    * Move enemy on rolling enemy
    * Spawn enemies on use "unstuck"
* Player death
  * Enemy and player hearts to show HP left
* Shoot angle over time
* Shotgun pickup
* Player loss when enemies get to the "goal" protected by the player - TODO: test
* Enemy move direction - "dijsktra floodfill"
* Tutorial: Defend this, dont lose life, kill them, roll here, press here to use dice, have a break between waves, start new wave here, go for high score
  * Use arrows and circles around objects pointed to
* Show score on loss (waves, enemies killed)

* Slight shot variation (random)

## In progress

* Add sounds
* Move enemies on enemies
  * Show arrow and immediately switch to forcing next enemy move - started but its broken
  
* Looks like some really nasty bug with clicks being ignored, is it because its done in draw()? TODO: YUP convfirmed we might skip draw if frame is too slow, should fix this

* States - spawn bugs
  * Spawn enemies wave
  
## Essential

* Restart with space on death
* Rewrite logic so it's in update instead of draw
* Setup first 6 waves, then constant large ammount

## Juice

* Cam shake
* Stop frames
* Graphics
* Graphics animation
* Blink on hit
* Screen flash on new wave spawn
* Smooth anim for movement
* SFX
* Music
* Show arrows for path on hover
* Smooth move enemies and player (slerp?)
