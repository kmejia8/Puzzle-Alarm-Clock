# Puzzle Alarm Clock

A Raspberry Pi project that functions as a puzzle-based alarm clock.  
To silence the alarm, the user must solve a randomly generated math equation displayed on a 16x2 I²C LCD.  
Input is entered through a 4x4 matrix keypad, while LEDs and a buzzer act as the alarm system.  
Incorrect attempts increase the buzzer’s intensity until the correct answer is provided.

---

## Features
- Displays random addition and subtraction problems on a 16x2 I²C LCD  
- Requires solving the equation correctly to stop the alarm  
- Uses a 4x4 matrix keypad for user input  
- LEDs and buzzer simulate the alarm system  
- Buzzer intensity increases with each wrong attempt  
- Resets after solving, displaying a “Have a great day” message  

---

## Hardware Used
- Raspberry Pi (tested with Pi 3/4)  
- 16x2 I²C LCD (PCF8574 backpack)  
- 4x4 Matrix keypad  
- 3x LEDs + resistors  
- Passive buzzer  
- Breadboard + jumper wires  

---

## Dependencies
- `RPi.GPIO` (for GPIO control)  
- `smbus` (for I²C LCD communication)  
- `time`, `random` (Python standard libraries)  
