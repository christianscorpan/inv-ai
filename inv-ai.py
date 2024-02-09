import threading
from pynput.keyboard import GlobalHotKeys
import pyperclip
from openai import OpenAI
import os


#make current directory the same as the file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load the OpenAI API key from a file
with open("secret.key", "r") as apikeyFile:
    client = OpenAI(api_key=apikeyFile.read())

# Configuration: Define the hotkey for sending clipboard content
    
send_key = "<alt>+i"  # Adjust the hotkey as needed

# Function to send the clipboard content to the OpenAI API
def send_clipboard_text():
    clipboard_text = pyperclip.paste()  # Get text from clipboard
    if clipboard_text:
        print("Sending clipboard text to OpenAI API:", clipboard_text)
        try:
            # Send the text to the OpenAI API and get the response
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "user", "content": clipboard_text}]
            )
            # Copy the API response back to the clipboard
            pyperclip.copy(response.choices[0].message.content.strip())
            print("Response copied to clipboard.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Clipboard is empty. No text was sent.")

# Main function to initialize the hotkey listener
def main():
    # Setup the hotkey listener
    with GlobalHotKeys({
            send_key: send_clipboard_text  # Bind the send_clipboard_text function to the hotkey
        }) as listener:
        # Wait for hotkey activation
        listener.join()

if __name__ == "__main__":
    main()

