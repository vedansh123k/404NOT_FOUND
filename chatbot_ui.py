import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from main_code import EntityAwareChatbot

class AdvancedChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Support Chatbot")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)

        # Apply modern theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TEntry", font=("Arial", 12))
        style.configure("TLabel", font=("Arial", 12))

        # Initialize chatbot
        self.chatbot = EntityAwareChatbot()

        # Header
        self.header = tk.Label(
            root, text="Customer Support Chatbot", font=("Arial", 18, "bold"),
            bg="#0078D7", fg="white", pady=10
        )
        self.header.pack(fill=tk.X)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, bg="#f9f9f9",
            font=("Arial", 12), relief=tk.FLAT
        )
        self.chat_display.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)

        # User input frame
        self.input_frame = ttk.Frame(root)
        self.input_frame.pack(pady=10, fill=tk.X)

        # User input field
        self.user_input = ttk.Entry(self.input_frame)
        self.user_input.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.user_input.bind("<Return>", self.send_message)

        # Send button
        self.send_button = ttk.Button(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.grid(row=0, column=1, padx=5)

        # Clear chat button
        self.clear_button = ttk.Button(
            self.input_frame, text="Clear Chat", command=self.clear_chat
        )
        self.clear_button.grid(row=0, column=2, padx=5)

        # Exit button
        self.exit_button = ttk.Button(
            root, text="Exit", command=self.exit_app
        )
        self.exit_button.pack(pady=10)

        # Configure grid layout
        self.input_frame.columnconfigure(0, weight=1)

        # Welcome message
        self.display_message("Bot", "Hello! How can I assist you today?")

    def display_message(self, sender, message):
        """Display a message in the chat display area."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def send_message(self, event=None):
        """Handle sending a message."""
        user_message = self.user_input.get().strip()
        if user_message:
            # Display user message
            self.display_message("You", user_message)

            # Get chatbot response
            bot_response = self.chatbot.get_response(user_message)
            self.display_message("Bot", bot_response)

            # Clear input field
            self.user_input.delete(0, tk.END)

    def clear_chat(self):
        """Clear the chat display area."""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat?"):
            self.chat_display.config(state='normal')
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state='disabled')
            self.display_message("Bot", "Chat cleared. How can I assist you?")

    def exit_app(self):
        """Exit the application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedChatbotUI(root)
    root.mainloop()