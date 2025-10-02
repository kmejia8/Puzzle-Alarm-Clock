''' ECE 350 Project
Puzzle Alarm Clock
Modified by Karla Mejia and Sawera Ashfaq
References the following lessons from the Adeept Manual:
- Lesson 14: Passive Buzzer
- Lesson 11: Matrix Keyboard
- Lesson 18: LCD 1602
- LCD 1602 Data Sheet (for different commands)
'''

import RPi.GPIO as GPIO
import smbus # allows for access to I2C, mainly for LCD screen
import random # for generating random numbers
from time import sleep

# ---------------------------------------------------------------------------------------
'''
This following block of code was referenced from the Adeept Manual (Lesson 18) to
get the LCD to properly power on and display.
'''
# ---------------------------------------------------------------------------------------
# converts time to , mainly for delay
def delay(time):
    sleep(time / 1000.0)

# converts time to microseconds, mainly for delay
def delayMicroseconds(time):
    sleep(time / 1000000.0)

# entire class includes methods for LCD, including displaying text, sending data, etc
class Screen():
    enable_mask = 1 << 2
    rw_mask = 1 << 1
    rs_mask = 1 << 0
    backlight_mask = 1 << 3
    data_mask = 0x00

    # initializing LCD
    def __init__(self, cols=16, rows=2, addr=0x27, bus=1):
        self.cols = cols
        self.rows = rows        
        self.bus = smbus.SMBus(bus)
        self.addr = addr
        self.enable_backlight() # ensures backlight is always on
        self.display_init()

    # enables backlight
    def enable_backlight(self):
        self.data_mask = self.data_mask|self.backlight_mask
        
    # disables backlight
    def disable_backlight(self):
        self.data_mask = self.data_mask& ~self.backlight_mask

    # clears screen, then displays characters/strings
    def display_data(self, *args):
        self.clear()
        for line, arg in enumerate(args):
            self.cursorTo(line, 0)
            self.println(arg[:self.cols].ljust(self.cols))

    # moves cursor
    def cursorTo(self, row, col):
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(0x80 | (offsets[row] + col))

    # clears any text from screen
    def clear(self):
        self.command(0x01) # clears the entire screen
        delay(2) # ensures LCD has enough time to clear

    # traverses through string to print each character
    def println(self, line):
        for char in line:
            self.print_char(char)

    # prints a given character
    def print_char(self, char):
        char_code = ord(char)
        self.send(char_code, self.rs_mask)

    # initializes entire LCD screen
    def display_init(self):
        delay(1.0)
        self.write4bits(0x30)
        delay(4.5)
        self.write4bits(0x30)
        delay(4.5)
        self.write4bits(0x30)
        delay(0.15)
        self.write4bits(0x20)
        # following commands referenced from datasheet
        self.command(0x28) # sets into 4 bit mode, 2 line display, and 5x8 character font
        self.command(0x0C) # turns on display, hides cursor, and disables blinking for clean look
        self.command(0x06) # cursor moves to the right when characters are printed
        self.clear()
        delay(2)

    # sends actual commands to the screen
    def command(self, value, delay=50.0):
        self.send(value, 0)
        delayMicroseconds(delay)

    # sends data as bits
    def send(self, data, mode):
        self.write4bits((data & 0xF0) | mode)
        self.write4bits(((data << 4) & 0xF0) | mode)

    # writes bits for screen
    def write4bits(self, value):
        value &= ~self.enable_mask
        self.expanderWrite(value)
        self.expanderWrite(value | self.enable_mask)
        self.expanderWrite(value)

    # communicates via I2C
    def expanderWrite(self, data):
        self.bus.write_byte_data(self.addr, 0, data | self.data_mask)

    # adding a cleanup command for if KeyboardInterrupt occurs
    def cleanup(self):
        self.clear() # clears display
        self.disable_backlight() # disables backlight
        self.expanderWrite(0x00) # disables any output
# ---------------------------------------------------------------------------------------
'''
This following block of code was referenced from the Adeept Manual (Lesson 11) to
get the 4x4 matrix keyboard to work properly
'''
# ---------------------------------------------------------------------------------------
class keypad():
    # maps true values from keypad to respective row/column
    KEYPAD = [
        [1, 2, 3, "A"],
        [4, 5, 6, "B"],
        [7, 8, 9, "C"],
        ["*", 0, "#", "D"]
    ]
    ROW = [11, 12, 13, 15] # GPIO pins used for rows
    COLUMN = [16, 18, 22, 7] # GPIO pins used for columns

    # initializes keypad and sets all buttons as input
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

    # handles when actual button is pressed
    def getKey(self):
        # sets all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)

        # settings rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # scanning rows for when button pushed, which will change rowVal
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i
        
        # checks for when button is pressed, if not, exits
        if rowVal < 0 or rowVal > 3:
            self.exit()
            return 

        # converts the columns into input
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # if row detects input, prepares to scan for column within that row
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)

        # scans columns for button thats pressed
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # checks if button pressed, if not, exits
        if colVal < 0 or colVal > 3:
            self.exit()
            return
 
        # return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
    
    # Reinitialize all rows and columns as input at exit
    def exit(self):
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
# ---------------------------------------------------------------------------------------

LED_PINS = [32, 36, 38] # pins chosen for LEDs
BUZZER_PIN = 37 # pin for buzzer
buzzer_pwm = None # prepares to modify the buzzer PWM

# function for initializing buzzer and LED pins
def setup_leds_and_buzzer():
    global buzzer_pwm # referencing variable for buzzer PWM since we're going to modify it

    # setting all LEDs as output and off initially
    for pin in LED_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    
    # sets up buzzer pin as output
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    # setting frequency of buzzer to 1kHz at a duty cycle of 0% (only for initializiation)
    buzzer_pwm = GPIO.PWM(BUZZER_PIN, 1000)
    buzzer_pwm.start(0)

# function to make LEDs flash, allowing for modifications to flash rate, delay, and buzzer volume
# default is to flash normally with delay of 0.2s and buzzer volume starting at duty cycle of 10 if not given
def change_led_and_buzzer(times=1, delay_time=0.2, buzzer_volume=10):
    # since buzzer volume is changing, we must cap the duty cycle to 100
    buzzer_pwm.ChangeDutyCycle(min(100, buzzer_volume))

    # makes LEDs flash depending on delay and number of times chosen
    for num in range(times):
        for pin in LED_PINS:
            GPIO.output(pin, GPIO.HIGH)
        sleep(delay_time)
        for pin in LED_PINS:
            GPIO.output(pin, GPIO.LOW)
        sleep(delay_time)
    buzzer_pwm.ChangeDutyCycle(0)

# increases the volume based on the number of wrong attempts
def buzz_on_wrong(attempts):
    # increases volume by 10%, capping it at 100%
    volume = min(100, 10 + attempts * 10)
    buzzer_pwm.ChangeDutyCycle(volume)
    sleep(0.2)
    buzzer_pwm.ChangeDutyCycle(0)

# determines what equation user will have to solve
def generate_equation():
    # possible operations
    op = random.choice(['+', '-'])

    # for addition
    if op == '+':
        # chooses number between 0-9, adds them to find the answer
        num1 = random.randint(0, 9)
        num2 = random.randint(0, 9)
        answer = num1 + num2
    # for subtraction
    elif op == '-':
        # chooses first number from 0-9
        num1 = random.randint(0, 9)
        # second number must be <= to first number to avoid negative answers
        num2 = random.randint(0, num1)
        # determines answer by subtracting both randoms
        answer = num1 - num2

    # determines what equation should be shown on screen
    equation = f"{num1} {op} {num2} = ???"
    return equation, answer

# clean up function to turn off pins, turn buzzer off, and clear screen
def cleanup():
    for pin in LED_PINS:
        GPIO.output(pin, GPIO.LOW)
        GPIO.setup(pin, GPIO.IN)
    buzzer_pwm.ChangeDutyCycle(0)
    buzzer_pwm.stop()
    GPIO.cleanup()
    screen.cleanup()

# main function, where actual logic for puzzle is implemented
if __name__ == "__main__":
    screen = Screen() # initializing LCD
    kp = keypad() # initializing 4x4 keypad
    GPIO.setwarnings(False)
    setup_leds_and_buzzer() # setting up LEDs and buzzer

    try:
        equation, correct_answer = generate_equation() # generates random equation and answer
        screen.display_data("Solve:", equation) # displays prompt and random equation on screen

        input_buffer = "" # stores user's input
        wrong_attempts = 0 # keeps track of number of wrong attempts

        # will continue to run until the correct answer is inputted (where the only 'break' is)
        while True:
            # consistently flashes LEDs, increasing volume by 10% for wrong attempts
            change_led_and_buzzer(1, buzzer_volume=10 + wrong_attempts * 10)

            # waits for input from keypad
            key = kp.getKey()
            
            # once a key is pressed
            if key is not None:
                # for resetting input
                if key == '*':
                    input_buffer = ""
                    screen.display_data("Solve:", equation)

                # checks if key is an integer, making it a valid input (no letters!)
                elif type(key) == int:
                    # while input is less than 3 digits
                    if len(input_buffer) < 3:
                        # adds input to buffer and displays any newly entered digits
                        input_buffer += str(key)
                        screen.display_data("Answer:", input_buffer)

                        # checks for if input is correct answer
                        if int(input_buffer) == correct_answer:
                            # displays equation with correct answer that was just input
                            screen.display_data("Correct!", f"{equation[:-3]} {correct_answer}") # slicing off '???'
                            wrong_attempts = 0 # resetting number of wrong attempts
                            sleep(1)
                            screen.display_data("Have a great", "day! :)")
                            break
                        # if numbers entered exceed the length of the correct answer, we know its wrong
                        elif len(input_buffer) >= len(str(correct_answer)):
                            wrong_attempts += 1 # increments wrong attempt counter
                            screen.display_data("Wrong!", equation) # displays that wrong answer input
                            buzz_on_wrong(wrong_attempts) # buzzer buzzes louder depending on number of wrong attempts
                            input_buffer = "" # resets input to blank
                            sleep(1)
                            screen.display_data("Solve:", equation) # shows original equation, preparing for another attempt

        # quickly flashes LEDs, indicating correct answer has been input!
        change_led_and_buzzer(3)
        sleep(2)

    except KeyboardInterrupt:
        print("Code interrupted")
        cleanup()
