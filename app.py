import tkinter as tk
from tkinter import messagebox, font
import smtplib
import random
import time

# --- CREDENTIALS ---
EMAIL_ADDRESS = "lakshya.pcvn@gmail.com"
EMAIL_PASSWORD = "jrct radn tiuf sbhq" # Your provided app password

def send_anniversary_email():
    """Sends the confirmation email when she clicks YES."""
    subject = "❤️ THE BOYFRIEND POST HAS BEEN REINSTATED! ❤️"
    body = (
        "Alert! Alert!\n\n"
        "Madam Sweetheart/Rashbhari has officially clicked YES.\n"
        "The 7-month affirmation anniversary is a success.\n"
        "The 'Boyfriend Post' has been successfully recovered and given back to Lakshya.\n"
        "Status: Infinitely Loved."
    )
    
    msg = f"Subject: {subject}\n\n{body}"
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

class AnniversaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("7 Months of Us | Official Affirmation")
        self.root.geometry("600x600")
        self.root.configure(bg="#fff5f5")
        
        self.questions = [
            ("Who is the prettiest girl in the entire universe?", "Rashbhari / My Wifey"),
            ("What are we celebrating today?", "7 Months of Affirmation"),
            ("Does Lakshya deserve his boyfriend post back?", "YES (Obviously)")
        ]
        self.q_index = 0
        self.show_welcome()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_screen()
        tk.Label(self.root, text="Happy 7 Months, My Laddu!", font=("Arial", 20, "bold"), bg="#fff5f5", fg="#d63384").pack(pady=50)
        tk.Button(self.root, text="Enter Our Memory Lane", command=self.show_question, bg="#ff85a2", fg="white", font=("Arial", 12, "bold")).pack()

    def show_question(self):
        self.clear_screen()
        if self.q_index < len(self.questions):
            tk.Label(self.root, text=f"Question {self.q_index + 1}", font=("Arial", 12), bg="#fff5f5").pack(pady=10)
            tk.Label(self.root, text=self.questions[self.q_index][0], font=("Arial", 14, "bold"), bg="#fff5f5", wraplength=500).pack(pady=20)
            
            ans_entry = tk.Entry(self.root, font=("Arial", 12))
            ans_entry.pack(pady=10)
            
            tk.Button(self.root, text="Next", command=lambda: self.next_q(), bg="#ff85a2", fg="white").pack(pady=20)
            self.q_index += 1
        else:
            self.show_marksheet()

    def next_q(self):
        self.show_question()

    def show_marksheet(self):
        self.clear_screen()
        tk.Label(self.root, text="✨ OFFICIAL ANNIVERSARY MARKSHEET ✨", font=("Arial", 16, "bold"), bg="#fff5f5").pack(pady=20)
        
        report = (
            "Subject: Love & Chemistry\n"
            "Score: 100/100 (Out of this World)\n"
            "Grade: SSS (Soulmate Level)\n"
            "Remarks: Too cute to be handled! Forever is the goal."
        )
        tk.Label(self.root, text=report, font=("Courier", 12), bg="white", relief="ridge", padx=20, pady=20).pack(pady=10)
        
        # The Proposal Message
        proposal = (
            "\nMy Dearest Madam Sweetheart,\n\n"
            "I know I made a huge mistake that led to you taking away my 'Boyfriend Post'.\n"
            "These 7 months have been the most beautiful affirmation of my life,\n"
            "and being without my title feels like a part of me is missing.\n"
            "I am asking you, with all the love my heart can hold: please forgive me.\n"
            "I want my post back. I want to be yours officially, now and forever.\n\n"
            "Do you love me now?"
        )
        tk.Label(self.root, text=proposal, font=("Arial", 11, "italic"), bg="#fff5f5", wraplength=500, fg="#333").pack(pady=10)

        # The Buttons
        self.yes_btn = tk.Button(self.root, text="YES", font=("Arial", 14, "bold"), bg="#28a745", fg="white", width=10, command=self.final_celebration)
        self.yes_btn.place(x=150, y=500)

        self.no_btn = tk.Button(self.root, text="NO", font=("Arial", 14, "bold"), bg="#dc3545", fg="white", width=10)
        self.no_btn.place(x=350, y=500)
        self.no_btn.bind("<Enter>", self.move_no_button)

    def move_no_button(self, event):
        new_x = random.randint(50, 450)
        new_y = random.randint(50, 550)
        self.no_btn.place(x=new_x, y=new_y)

    def final_celebration(self):
        self.clear_screen()
        # Visual interface for YES
        tk.Label(self.root, text="💖 YAYYYYY! 💖", font=("Arial", 30, "bold"), bg="#fff5f5", fg="#d63384").pack(pady=50)
        tk.Label(self.root, text="The Boyfriend Post has been REINSTATED!\nCheck your email for the confirmation!", 
                 font=("Arial", 14), bg="#fff5f5", justify="center").pack(pady=20)
        
        # Send the email
        if send_anniversary_email():
            tk.Label(self.root, text="📧 Email sent to Lakshya!", font=("Arial", 10), bg="#fff5f5", fg="green").pack()
        else:
            tk.Label(self.root, text="❌ Email failed but Love is still here!", font=("Arial", 10), bg="#fff5f5", fg="red").pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnniversaryApp(root)
    root.mainloop()
