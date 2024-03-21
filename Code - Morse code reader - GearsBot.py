import time
from ev3dev2.motor import LargeMotor, MoveTank
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.sound import Sound

# Morse code definitions
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
    '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
    '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
    '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z',
    '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5',
    '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0'
}

# Adjusted parameters
base_speed = 20
speed_increment = 10
colour_change_threshold = 1

def read_and_convert_morse():
    # Initialise sensors and actuators
    colour_sensor = ColorSensor('in1')  # Initialize color sensor connected to input port 1
    ultrasonic_sensor = UltrasonicSensor('in2')  # Initialize ultrasonic sensor connected to input port 2
    speaker = Sound()  # Initialize speaker for audio output
    x_motor = LargeMotor('outA')  # Initialize large motor connected to output port A (left motor)
    y_motor = LargeMotor('outB')  # Initialize large motor connected to output port B (right motor)
 
    # Initialise variables
    morse_message = ""  # Store the Morse code message
    finished_colour = False  # Store the last detected colour
    time_zero = time.time()  # Reference time for measuring colour duration
    dot_duration = None  # Duration of a dot in Morse code
    colour_changed = False
    # Main loop
    while True:
        # Read colour sensor and check for obstacle
        reading_colour = colour_sensor.color
        object_detected = ultrasonic_sensor.distance_centimeters < 10
        end_of_message = morse_message.endswith(' ' * 10)
        
         # Process colour change
        if reading_colour != finished_colour:
            colour_changed = True
            # Calculation dot_duration
            if finished_colour == 6:
                if dot_duration is None:
                    dot_duration = time.time() - time_zero
      
             #Conditions to read colours and add signs to list morse_message
            if colour_changed is True:
                reading_colour_time = time.time() - time_zero
                if finished_colour is not None:
                    # Determine if dot or dash based on colour red duration
                    if finished_colour == 5:# Red colour (dot or dash)
                        if reading_colour_time <  dot_duration * colour_change_threshold:
                            morse_message += '.'  # Dot
                            print("dot")
                            speaker.beep()
                        else:
                            morse_message += '-'  # Dash
                            print("dash")
                            for _ in range(2):  # Repeat beep twice for a longer sound
                                speaker.beep()
                    # Creation spacing
                    if finished_colour == 6:# White colour (word spacing)
                        # Add appropriate number of spaces based on colour white duration
                        morse_message += ' ' * round(reading_colour_time / dot_duration)
                        
                # Updating finished colour and reference time
                finished_colour = reading_colour  
                time_zero = time.time()
                
        # Check for obstacle or end of message
        if object_detected or end_of_message:
            if object_detected:
                x_motor.off(brake=True)
                y_motor.off(brake=True)
                print('Obstacle detected and vehicle stopped')
            break
        
        # Update motor speeds based on side line colours detection
        left_speed = base_speed 
        right_speed = base_speed 
        x_motor.on(left_speed, brake=False)
        y_motor.on(right_speed, brake=False)
    
    # Decode Morse code message
    print(f"Signals to decode: {morse_message}")
    
    letters_message = ""  # Variable to store the translated message from Morse code to letters

# Loop through individual words in the Morse code message, separated by three spaces
#(equivalent to one space between words in the original text)
for word in morse_message.split('   '):
    # Loop through individual letters in each word
    for letter in word.split():  # Skip empty elements (spaces)
        # Convert the Morse code symbol to its corresponding letter;
        #if the symbol doesn't exist in the MORSE_CODE dictionary, replace it with a question mark
        letters_message += MORSE_CODE.get(letter, '?')
    letters_message += " "  # Add space between translated words


        
    # Print and speak decoded message
    print(f"Received message: {letters_message.strip()}")
    speaker.speak(f"I read: {letters_message.strip()}")

# Call the main function
read_and_convert_morse()
