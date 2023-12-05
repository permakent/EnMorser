import tkinter as tk
import array
import math
from time import sleep
from time import time
import pyaudio
import datetime

p = pyaudio.PyAudio()

volume = 0.1  # range [0.0, 1.0]
fs = 2000  # sampling rate, Hz, must be integer
duration = 0.08  # in seconds, may be float
f = 700.0  # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
num_samples = int(fs * duration)
samples = [volume * math.sin(2 * math.pi * k * f / fs)
            for k in range(0, num_samples)]

# per @yahweh comment explicitly convert to bytes sequence
output_bytes = array.array('f', samples).tobytes()
output_byte3 = output_bytes + output_bytes + output_bytes

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

# Morse code dictionary

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', '0': '-----', ',': '--..--', '.': '.-.-.-', '?': '..--..',
    '/': '-..-.', '@': '.--.-.', ':': '---...', '$': '...-..-', '*': '...-.-',
    '!': '-.-.--', '<': '........', '+': '.-.-.', '(': '-.--.', '=': '-...-'
}
REVERSE_MORSE_CODE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

WPM = 20
UNIT_DURATION = 1.2 / WPM  # In seconds
WORD_END_THRESHOLD = 0.8  # Threshold for the end of a word in Morse code
DOT_THRESHOLD = 0.15
DASH_THRESHOLD = 0.4
SPACE_THRESHOLD = 0.45

class MorseKeyboard(tk.Tk):
    
    def __init__(self):
        super().__init__()

        self.last_release_time = time()
        self.last_press_time = 0
        self.morse_sequence = ""
        self.decoded_message = ""
        self.decoded_char = ""

        self.title("EnMorser Terminal")
        self.geometry("480x320")
        self.config(bg="white")

        # Load the image file from disk.
        icon = tk.PhotoImage(file="em_icon.png")
        # Set it as the window icon.
        self.iconphoto(True, icon)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
        self.message_area = tk.StringVar()
        self.create_keyboard()
        self.send_area = tk.StringVar()
        self.create_display_area()
        

    def on_close(self):
        self.destroy()

    def create_keyboard(self):
        keyboard_frame = tk.Frame(self)
        keyboard_frame.grid(row=1, column=0, sticky="nsew")

        keys = [
            "1234567890$@",
            "QWERTYUIOP?!",
            "ASDFGHJKL:/",
            "ZXCVBNM.,",
        ]

        for idx, keyrow in enumerate(keys):
            for idy, key in enumerate(keyrow):
                button = tk.Button(keyboard_frame, text=key, command=lambda
                            k=key: self.press_key(k), width=2)
                button.grid(row=idx, column=idy, padx=5, pady=5)


        receive_button = tk.Button(keyboard_frame, text="RECEIVE", fg="#006600", 
                            width=9, relief="raised")
        receive_button.grid(row=3, column=10, columnspan=4, padx=5, pady=5)
        receive_button.bind("<ButtonPress>", lambda e: self.button_pressed())  # Bind the press event
        receive_button.bind("<ButtonRelease>", lambda e: self.button_released())  # Bind the release event

        clear_button = tk.Button(keyboard_frame, text="CLEAR",
                            command=self.clear_button, width=6)
        clear_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        bkspace_button = tk.Button(keyboard_frame, text="<-",
                            command=self.back_space, width=6)
        bkspace_button.grid(row=5, column=2, columnspan=2, padx=5, pady=5)

        space_button = tk.Button(keyboard_frame, text="SPACE",
                            command=self.press_space, width=10)
        space_button.grid(row=5, column=4, columnspan=3, padx=5, pady=5)

        send_button = tk.Button(keyboard_frame, text="SEND", fg="#660000",
                            command=self.send_message, width=6)
        send_button.grid(row=5, column=8, columnspan=2, padx=5, pady=5)

    def create_display_area(self):
        display_frame = tk.Frame(self)
        display_frame.grid(row=0, column=0, sticky="nsew")
        txt_callsign = tk.Label(display_frame, width=10, font=('arial', 10),
                    text = "WA6ZFY", fg='#660000')
        txt_callsign.grid(row=0, column=0, padx=2, pady=2, sticky="w")
        txt_title = tk.Label(display_frame, width=30, font=('arial', 12),
                    text = "EnMorser Terminal", fg='#000066')
        txt_title.grid(row=0, column=1, padx=2, pady=2, sticky="w")
        txt_recvcall = tk.Label(display_frame, width=10, font=('arial', 10),
                    text = "K7ABC", fg='#006600')
        txt_recvcall.grid(row=0, column=2, padx=2, pady=2, sticky="w")
        
        display_label = tk.Label(display_frame, text="Message Area:")
        display_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        display_entry = tk.Entry(display_frame,
                            textvariable=self.message_area, width=45)
        display_entry.grid(row=1, column=1, columnspan=9, padx=5, pady=5)

        send_label = tk.Label(display_frame, text="Sending:")
        send_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.send_display = tk.Text(display_frame, height=2, width=45)
        self.send_display.grid(row=2, column=1, columnspan=9, padx=5, pady=5)
        scrollbar = tk.Scrollbar(display_frame, command=self.send_display.yview)
        scrollbar.grid(row=2, column=10, sticky='nsew')
        self.send_display['yscrollcommand'] = scrollbar.set

        self.flash_area = tk.Label(self, width=1, height=1,
                            bg="white", relief="groove")
        self.flash_area.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

    def morse_to_text(self, morse_code):
        words = morse_code.split("  ")  # Split morse code into words
        decoded_message = ""
        decoded_char = ""

        for word in words:
            chars = word.split()  # Split words into characters
            for char in chars:
                if char in REVERSE_MORSE_CODE_DICT:
                    decoded_message += REVERSE_MORSE_CODE_DICT[char]

            decoded_message += " "  # Add space between words

        return decoded_message.strip()

    def button_pressed(self):
        self.last_press_time = time()  # Record the time when the button is pressed

        # Check the duration since the last button press to determine if a
        # space (end of a letter) or three spaces (end of a word) needs to be added
        time_since_last_press = self.last_press_time - self.last_release_time
        if time_since_last_press > WORD_END_THRESHOLD:
            self.morse_sequence += "   "  # Three spaces for the end of a word
        elif time_since_last_press > SPACE_THRESHOLD:
            self.morse_sequence += " "   # One space for the end of a letter
        self.morse_sequence = self.morse_sequence.lstrip()


    def button_released(self):
        current_time = time()

        # Duration of the button being pressed
        press_duration = current_time - self.last_press_time

        # Determine if the press was a dot or a dash based on its duration
        if press_duration < DOT_THRESHOLD:
            self.morse_sequence += "."
        elif DOT_THRESHOLD < press_duration < DASH_THRESHOLD:
            self.morse_sequence += "-"

        self.update_display()
        self.last_release_time = current_time

        # def update_display(self):
        #     # Decode Morse sequence to text
        #     self.decoded_message = self.morse_to_text(self.morse_sequence)
        #     self.message_area.set(self.decoded_message)

        #     # Display the Morse sequence
        #     self.send_display.delete(1.0, tk.END)
        #     self.send_display.insert(tk.END, self.morse_sequence)
        
    def update_display(self):
        # Decode Morse sequence to text
        self.decoded_message = self.morse_to_text(self.morse_sequence)
        
        # Extract the call sign from the decoded message
        call_sign = self.extract_call_sign(self.decoded_message)
        
        # Get the current UTC time
        utc_time = datetime.datetime.utcnow().strftime('%H:%M:%S UTC')
        
        # Update the message area with the call sign and UTC time
        display_text = f"{call_sign} {utc_time}" if call_sign else self.decoded_message
        self.message_area.set(display_text)

        # Display the Morse sequence
        self.send_display.delete(1.0, tk.END)
        self.send_display.insert(tk.END, self.morse_sequence)
 
    def extract_call_sign(self, message):
        # Look for the call sign pattern (usually after "DE" and before "KN")
        parts = message.split(' DE ')
        if len(parts) > 1:
            # Further split by space and take the elements before "KN"
            call_sign_parts = parts[1].split()
            call_sign = []
            for part in call_sign_parts:
                if part == "KN":
                    break
                call_sign.append(part)
            return ' '.join(call_sign).replace(" ", "")  # Join the parts of the call sign
        return "" 

    def press_key(self, key):
        current_text = self.message_area.get()
        self.message_area.set(current_text + key)

    def press_space(self):
        current_text = self.message_area.get()
        self.message_area.set(current_text + " ")

    def decode_morse(self):
        for char, morse in MORSE_CODE_DICT.items():
            if self.morse_sequence == morse:
                self.decoded_message += char
                self.morse_sequence = ''  # Reset the Morse sequence
                break

    def clear_button(self):
        current_text = ""
        self.message_area.set(current_text)
        self.send_display.delete(1.0, tk.END)
        self.decoded_message = ""
        self.morse_sequence = ""

    def back_space(self):
        current_text = self.message_area.get()
        self.message_area.set(current_text[:-1])

    def send_message(self):
        self.send_display.delete(1.0, tk.END)
        message = self.message_area.get().upper()
        morse_code = self.convert_to_morse_code(message)
        self.flash_morse_code(morse_code)

    def convert_to_morse_code(self, message):
        morse_code = ""
        for char in message:
            if char == " ":
                morse_code += "  "
            elif char in MORSE_CODE_DICT:
                morse_code += MORSE_CODE_DICT[char] + " "
        return morse_code.strip()

    def flash_morse_code(self, morse_code):
        self.flash_area.config(bg="white")
        for symbol in morse_code:
            self.send_display.insert(tk.END, symbol)
            self.send_display.see(tk.END)

            if symbol == ".":
                self.flash_area.config(bg="green")
                self.update()
                stream.write(output_bytes)
                sleep(UNIT_DURATION)
                self.flash_area.config(bg="white")
                self.update()
                sleep(UNIT_DURATION)
            elif symbol == "-":
                self.flash_area.config(bg="red")
                self.update()
                stream.write(output_byte3)
                sleep(UNIT_DURATION * 3)
                self.flash_area.config(bg="white")
                self.update()
                sleep(UNIT_DURATION)
            elif symbol == " ":
                sleep(UNIT_DURATION * 4)

if __name__ == "__main__":
    app = MorseKeyboard()
    app.mainloop()
