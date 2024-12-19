import RPi.GPIO as GPIO
import time
import socket
import os

# --- Setup GPIO ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# --- Servo Motor Setup ---
SERVO_PIN = 11
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz frequency
servo.start(0)

# --- Keypad Setup ---
MATRIX = [[1, 2, 3, 'A'],
          [4, 5, 6, 'B'],
          [7, 8, 9, 'C'],
          ['*', 0, '#', 'D']]
ROW = [3, 5, 7, 29]
COL = [31, 33, 35, 37]
for j in range(4):
    GPIO.setup(COL[j], GPIO.OUT)
    GPIO.output(COL[j], 1)
for i in range(4):
    GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- LCD Setup ---
LCD_RS = 15
LCD_E = 16
LCD_D4 = 18
LCD_D5 = 22
LCD_D6 = 24
LCD_D7 = 26
LCD_WIDTH = 16  # Characters per line
LCD_CHR = True  # Send data
LCD_CMD = False  # Send command
LCD_LINE_1 = 0x80  # Address for line 1
LCD_LINE_2 = 0xC0  # Address for line 2

# --- LCD Functions ---
def lcd_init():
    """Initialize the LCD."""
    lcd_send_byte(0x33, LCD_CMD)  # Initialize
    lcd_send_byte(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_send_byte(0x28, LCD_CMD)  # 2 line, 5x7 matrix
    lcd_send_byte(0x0C, LCD_CMD)  # Turn cursor off
    lcd_send_byte(0x06, LCD_CMD)  # Shift cursor right
    lcd_send_byte(0x01, LCD_CMD)  # Clear display
    time.sleep(0.005)

def lcd_send_byte(bits, mode):
    """Send byte to data pins."""
    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, bool(bits & 0x10))
    GPIO.output(LCD_D5, bool(bits & 0x20))
    GPIO.output(LCD_D6, bool(bits & 0x40))
    GPIO.output(LCD_D7, bool(bits & 0x80))
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, bool(bits & 0x01))
    GPIO.output(LCD_D5, bool(bits & 0x02))
    GPIO.output(LCD_D6, bool(bits & 0x04))
    GPIO.output(LCD_D7, bool(bits & 0x08))
    lcd_toggle_enable()

def lcd_toggle_enable():
    """Toggle enable pin."""
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

def lcd_display(message, line):
    """Display message on LCD."""
    lcd_send_byte(line, LCD_CMD)
    message = message.ljust(LCD_WIDTH, " ")  # Pad message to fit screen
    for char in message[:LCD_WIDTH]:
        lcd_send_byte(ord(char), LCD_CHR)

# --- Socket Setup (File Sharing) ---
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 12345

# --- Functions ---
def keypad_input():
    """Read input from the keypad."""
    for j in range(4):
        GPIO.output(COL[j], 0)
        for i in range(4):
            if GPIO.input(ROW[i]) == 0:
                time.sleep(0.2)  # Debounce
                while GPIO.input(ROW[i]) == 0:
                    pass
                GPIO.output(COL[j], 1)
                return MATRIX[i][j]
        GPIO.output(COL[j], 1)
    return None

def servo_rotate(angle):
    """Rotate the servo motor to the specified angle."""
    duty_cycle = 2 + (angle / 18)  # Convert angle to duty cycle
    servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)  # Stop sending signal to prevent jitter

def handle_file_transfer(conn):
    """Handle file sharing (send/receive) between Raspberry Pi and PC."""
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        elif data.startswith("SEND"):
            filename = data.split()[1]
            with open(filename, "wb") as f:
                while True:
                    chunk = conn.recv(1024)
                    if chunk == b"EOF":
                        break
                    f.write(chunk)
            lcd_display(f"File {filename} received", LCD_LINE_1)
        elif data.startswith("RECEIVE"):
            filename = data.split()[1]
            if os.path.exists(filename):
                conn.send(f"OK {os.path.getsize(filename)}".encode())
                with open(filename, "rb") as f:
                    while chunk := f.read(1024):
                        conn.send(chunk)
                conn.send(b"EOF")
                lcd_display(f"File {filename} sent", LCD_LINE_1)
            else:
                conn.send("ERROR File not found".encode())
        elif data.lower() == "exit":
            break

# --- Main Program ---
def main():
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_D4, GPIO.OUT)
    GPIO.setup(LCD_D5, GPIO.OUT)
    GPIO.setup(LCD_D6, GPIO.OUT)
    GPIO.setup(LCD_D7, GPIO.OUT)
    lcd_init()

    # Start socket server for file sharing
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server started on {HOST}:{PORT}. Waiting for connections...")
    lcd_display("Server started", LCD_LINE_1)
    conn, addr = server_socket.accept()
    print(f"Connected by {addr}")
    lcd_display(f"Connected to {addr[0]}", LCD_LINE_2)

    try:
        while True:
            # Display menu on LCD
            lcd_display("1: Servo 2: File", LCD_LINE_1)
            key = keypad_input()

            if key == 1:  # Servo Operation
                lcd_display("Enter angle (0-180):", LCD_LINE_1)
                angle = ""
                while True:
                    digit = keypad_input()
                    if digit == '#':  # Confirm input
                        break
                    elif digit == '*':  # Clear input
                        angle = ""
                        lcd_display("Enter angle:", LCD_LINE_1)
                    elif isinstance(digit, int):  # Add digit to angle
                        angle += str(digit)
                        lcd_display(f"Angle: {angle}", LCD_LINE_2)
                angle = int(angle)
                if 0 <= angle <= 180:
                    servo_rotate(angle)
                    lcd_display(f"Servo set to {angle}", LCD_LINE_1)
                else:
                    lcd_display("Invalid angle", LCD_LINE_1)

            elif key == 2:  # File Sharing
                lcd_display("File Sharing...", LCD_LINE_1)
                handle_file_transfer(conn)

            elif key == 'C':  # Exit program
                break

    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        conn.close()
        server_socket.close()
        servo.stop()
        GPIO.cleanup()
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
