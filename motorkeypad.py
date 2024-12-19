import RPi.GPIO as GPIO
import time

# Servo Motor Setup
SERVO_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM frequency
servo_pwm.start(0)  # Start with 0 duty cycle

# Keypad Setup
ROW = [3, 5, 7, 29]
COL = [31, 33, 35, 37]

# Keypad matrix
MATRIX = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Setup GPIO for Keypad
GPIO.setmode(GPIO.BOARD)
for pin in ROW:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in COL:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 1)

# Function to set servo angle
def set_servo_angle(angle):
    duty_cycle = (angle / 18) + 2  # Converts angle (0-180 degrees) to a PWM duty cycle (2-12%)
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)  # Small delay to allow the servo to rotate

# Function to test keypad and get input
def test_keypad_input():
    for j in range(4):
        GPIO.output(COL[j], 0)  # Set one column low
        for i in range(4):
            if GPIO.input(ROW[i]) == 0:
                print(f"Key detected at row {i+1}, column {j+1}: {MATRIX[i][j]}")
                if MATRIX[i][j] in '1234567890':
                    angle = int(MATRIX[i][j]) * 10  # Map key to servo angle
                    set_servo_angle(angle)
                    time.sleep(0.1)  # Debounce delay
        GPIO.output(COL[j], 1)  # Set column high again

# Main loop to read keypad and control servo
try:
    while True:
        test_keypad_input()
except KeyboardInterrupt:
    print("Exiting...")
    servo_pwm.stop()     # Stop PWM
    GPIO.cleanup()       # Clean up GPIO
