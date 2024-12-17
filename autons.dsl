initial_cpp_code
    // Initial setup code
    void setup() {
        // Setup code here
    }
end

// API Definitions
api
chassis.setPose(x:float, y:float, theta:float) -> pose(x, y, theta)
set_drive(distance:float, ms:int=3000, minSpeed:int=0, maxSpeed:int=127) -> drive(distance, ?ms, ?turn, ?speed)
mogoClamp.toggle() -> clamp()
chassis.turnToPoint(x:float, y:float, ms:int=3000, %{%.forwards:bool=true, .minSpeed:int=0, .maxSpeed:int=127%}%) -> turnTo(x, y, ms, ?.forwards, ?.minSpeed, ?.maxSpeed)
LBExtend(position:int) -> LBExtend(position)
pros::delay(ms:float) -> sleep(ms)
setIntake(speed:int) -> intake(speed)
chassis.waitUntilDone() -> wait()
end

// Autonomous Routines
// Picks up mobile goal and scores rings
routine mogoAdvayAutonBlue
    // Set initial position
    pose 48 60 -90
    drive -24.5
    wait
    // Turn to Mogo #1
    turnTo 9.5 -55 3000 false
    wait
    drive -14.87 
    // -1*sqrt((23.5-9.5)^2+(60-55)^2)
    wait
    // Clamp to Mogo #1
    clamp
    sleep 100
    intake 127
    sleep 500
    // Turn to Mogo #2
    turnTo 17 19 3000 false
    clamp
    wait
    drive 36.77 
    // -1*sqrt((9.5-17)^2+(55-19)^2)
    wait
    // Clamp to Mogo #2
    clamp
    sleep 700
    setIntake 127
    // Turn to Ring Stake
    turnTo 25 -54
    wait
    drive 12
    wait
    // Turn to Ladder
    turnTo 48 0
    wait
    drive 40
end

routine mogoAdvayAutonRed
    // Set initial position
    pose -48 60 90
    drive -24.5
    wait
    // Turn to Mogo #1
    turnTo -9.5 -55 3000 false
    wait
    drive -14.87 
    // -1*sqrt((23.5-9.5)^2+(60-55)^2)
    wait
    // Clamp to Mogo #1
    clamp
    sleep 100
    intake 127
    sleep 500
    // Turn to Mogo #2
    turnTo -17 19 3000 false
    clamp
    wait
    drive 36.77 
    // -1*sqrt((9.5-17)^2+(55-19)^2)
    wait
    // Clamp to Mogo #2
    clamp
    sleep 700
    setIntake 127
    // Turn to Ring Stake
    turnTo -25 -54
    wait
    drive 12
    wait
    // Turn to Ladder
    turnTo -48 0
    wait
    drive 40
end