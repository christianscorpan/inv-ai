import threading
import time
from pynput import keyboard
import pyperclip
from openai import OpenAI
from pynput.keyboard import Key, KeyCode, GlobalHotKeys, Listener

client = OpenAI(api_key='ur-api-key-here')

# conf
collect_key = "<cmd>+t"
cancel_key = "<cmd>+y"
send_key = "<cmd>+o"
collection_active = False
text_buffer = []

# Global set to track pressed keys
currently_pressed_keys = set()

# Listener actions on key press
def on_activate_collect():
    global collection_active, text_buffer
    collection_active = True
    text_buffer = []
    print("Text collection started.")

def on_activate_cancel():
    global collection_active
    collection_active = False
    print("Text collection canceled.")

def on_activate_send():
    global collection_active, text_buffer
    if text_buffer:
        query_text = ''.join(text_buffer)
        print("Sending text to OpenAI API:", query_text)
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": "user", "content": query_text}]
            )
            pyperclip.copy(response.choices[0].message.content.strip())
            print("Response copied to clipboard.")
        except Exception as e:
            print(f"Error: {e}")
        
    else:
        print("Nothing to send.")
    collection_active = False
    text_buffer = []

def on_press(key):
    global collection_active, text_buffer, currently_pressed_keys

    currently_pressed_keys.add(key)

    # Check if current keys match any hotkey combination
    if {Key.cmd, KeyCode.from_char('t')} <= currently_pressed_keys \
       or {Key.cmd, KeyCode.from_char('o')} <= currently_pressed_keys:
        return  # Ignore keys part of hotkey combinations

    try:
        if collection_active:
            if hasattr(key, 'char') and key.char:
                text_buffer.append(key.char)
            elif key == keyboard.Key.space:  # Handle space separately
                text_buffer.append(' ')
    except AttributeError:
        pass  # Do nothing for other special keys

def on_release(key):
    global currently_pressed_keys
    try:
        currently_pressed_keys.remove(key)
    except KeyError:
        pass  # Key was not in set

def main():
    # Listener to bind keys and actions for hotkeys
    with GlobalHotKeys({
            collect_key: on_activate_collect,
            cancel_key: on_activate_cancel,
            send_key: on_activate_send
        }) as h:

        # Set up and start the listener for on_press and on_release events
        with Listener(on_press=on_press, on_release=on_release) as listener:
            # Thread to run the GlobalHotKeys listener in the background
            listener_thread = threading.Thread(target=h.join)
            listener_thread.start()

            # Main loop to prevent the script from exiting
            try:
                while True:
                    time.sleep(0.01)  # Sleep to prevent high CPU usage
            except KeyboardInterrupt:
                listener.stop()
                print("Script interrupted by user.")

if __name__ == "__main__":
    main()
