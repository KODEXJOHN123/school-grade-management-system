import tkinter as tk
from tkinter import messagebox, filedialog
HAS_REPORTLAB = True
HAS_PIL = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except Exception:
    HAS_REPORTLAB = False

try:
    from PIL import Image, ImageTk
except Exception:
    HAS_PIL = False

import json
import os
import datetime

APP_NAME = "ScoreGuard"

GREEN = "#1db954"
GOLD = "#d4af37"
DARK_GREEN = "#0b3d2e"
WHITE = "#ffffff"

DATA_DIR = "data"
RESULT_DIR = "results"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w") as f:
        json.dump([], f)

class ScoreGuardApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1100x700")
        self.resizable(False, False)

        self.current_user = None
        self.profile_data = {}
        self.course_data = []
        self.cgpa = 0
        self.cgpa_scale = 5
        self.background_image = None

        self.container = tk.Frame(self, bg=DARK_GREEN)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        pages = (
            LoginPage,
            RegisterPage,
            HomePage,
            ProfilePage,
            ScoreVaultPage,
            PreviewPage,
            ResultVaultPage,
            ScoreboardPage,
            SettingsPage
        )

        for page in pages:
            frame = page(self.container, self)
            self.frames[page.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("LoginPage")

    def show_frame(self, name):
        frame = self.frames[name]
        # Call refresh method if frame has one (for dynamic content)
        if hasattr(frame, 'on_show'):
            frame.on_show()
        frame.tkraise()

    def logout(self):
        """Clear user data and return to login"""
        self.current_user = None
        self.profile_data = {}
        self.course_data = []
        self.cgpa = 0
        self.cgpa_scale = 5
        self.background_image = None
        self.show_frame("LoginPage")

class LoginPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Label(
            self,
            text="🦉 ScoreGuard",
            font=("Arial", 32, "bold"),
            fg=GOLD,
            bg=DARK_GREEN
        ).pack(pady=40)

        self.username = tk.Entry(self, font=("Arial", 14), width=30)
        self.username.pack(pady=10)

        self.password = tk.Entry(self, font=("Arial", 14), show="*", width=30)
        self.password.pack(pady=10)

        tk.Button(
            self,
            text="Login",
            bg=GREEN,
            fg="black",
            width=20,
            command=self.login
        ).pack(pady=10)

        tk.Button(
            self,
            text="Register",
            bg=GOLD,
            fg="black",
            width=20,
            command=lambda: app.show_frame("RegisterPage")
        ).pack()

    def login(self):
        with open(USERS_FILE) as f:
            users = json.load(f)

        u = self.username.get()
        p = self.password.get()

        if u in users and users[u]["password"] == p:
            self.app.current_user = u
            self.app.show_frame("HomePage")
        else:
            messagebox.showerror("Error", "Invalid username or password")

class RegisterPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("LoginPage")
        ).pack(anchor="nw")

        tk.Label(
            self,
            text="Create Account",
            font=("Arial", 26),
            fg=GOLD,
            bg=DARK_GREEN
        ).pack(pady=40)

        self.username = tk.Entry(self, font=("Arial", 14), width=30)
        self.username.pack(pady=10)

        self.password = tk.Entry(self, font=("Arial", 14), show="*", width=30)
        self.password.pack(pady=10)

        tk.Button(
            self,
            text="Create Account",
            bg=GREEN,
            width=20,
            command=self.create_account
        ).pack(pady=10)

    def create_account(self):
        with open(USERS_FILE) as f:
            users = json.load(f)

        u = self.username.get()

        if u in users:
            messagebox.showerror("Error", "User already exists")
            return

        users[u] = {
            "password": self.password.get(),
            "university": ""
        }

        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

        messagebox.showinfo("Success", "Account created")
        self.app.show_frame("LoginPage")

class HomePage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        self.bg_label = tk.Label(self)
        self.bg_label.place(relwidth=1, relheight=1)

        self.refresh_background()

        grid = tk.Frame(self, bg=DARK_GREEN)
        grid.place(relx=0.5, rely=0.5, anchor="center")

        buttons = [
            ("Profile", "ProfilePage"),
            ("Score Vault", "ScoreVaultPage"),
            ("Preview", "PreviewPage"),
            ("Result Vault", "ResultVaultPage"),
            ("Scoreboard", "ScoreboardPage")
        ]

        r = 0
        c = 0

        for text, page in buttons:
            tk.Button(
                grid,
                text=text,
                width=25,
                height=3,
                bg=GREEN,
                fg="black",
                command=lambda p=page: app.show_frame(p)
            ).grid(row=r, column=c, padx=25, pady=25)

            c += 1
            if c == 2:
                c = 0
                r += 1

        tk.Button(
            self,
            text="⚙",
            bg=GOLD,
            width=3,
            command=lambda: app.show_frame("SettingsPage")
        ).place(relx=0.96, rely=0.94)

        tk.Button(
            self,
            text="Logout",
            bg="#e74c3c",
            fg="black",
            width=8,
            command=app.logout
        ).place(relx=0.96, rely=0.02, anchor="ne")

    def refresh_background(self):
        if self.app.background_image and HAS_PIL:
            try:
                img = Image.open(self.app.background_image)
                img = img.resize((1100, 700))
                self.bg = ImageTk.PhotoImage(img)
                self.bg_label.config(image=self.bg)
            except Exception:
                self.bg_label.config(bg="#0a2f24")
        else:
            self.bg_label.config(bg="#0a2f24")

class ProfilePage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("HomePage")
        ).pack(anchor="nw")

        self.entries = {}

        fields = [
            "Name",
            "Phone",
            "Level",
            "Parent Phone",
            "Parent Email",
            "University"
        ]

        for field in fields:
            tk.Label(self, text=field, fg=WHITE, bg=DARK_GREEN).pack(pady=3)
            entry = tk.Entry(self, width=40)
            entry.pack()
            self.entries[field] = entry

        self.display = tk.Label(self, fg=GOLD, bg=DARK_GREEN)
        self.display.pack(pady=10)

        tk.Button(
            self,
            text="Save",
            bg=GREEN,
            width=20,
            command=self.save_profile
        ).pack(pady=5)

        tk.Button(
            self,
            text="Edit",
            bg=GOLD,
            width=20,
            command=self.edit_profile
        ).pack(pady=5)

    def on_show(self):
        """Called when this page is shown - load saved profile data"""
        self.load_profile()

    def get_profile_file(self):
        """Get the profile file path for current user"""
        return os.path.join(DATA_DIR, f"{self.app.current_user}_profile.json")

    def load_profile(self):
        """Load profile data from file for current user"""
        profile_file = self.get_profile_file()
        if os.path.exists(profile_file):
            try:
                with open(profile_file) as f:
                    profile_data = json.load(f)
                # Load data into app
                self.app.profile_data = profile_data
                # Display the data
                text = ""
                for k, v in profile_data.items():
                    text += f"{k}: {v}\n"
                self.display.config(text=text)
                # Populate entry fields
                for field, value in profile_data.items():
                    if field in self.entries:
                        self.entries[field].delete(0, tk.END)
                        self.entries[field].insert(0, value)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load profile: {str(e)}")

    def save_profile(self):
        self.app.profile_data = {}
        for k, v in self.entries.items():
            self.app.profile_data[k] = v.get()

        # Save to user-specific profile file
        profile_file = self.get_profile_file()
        try:
            with open(profile_file, "w") as f:
                json.dump(self.app.profile_data, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save profile: {str(e)}")
            return

        text = ""
        for k, v in self.app.profile_data.items():
            text += f"{k}: {v}\n"

        self.display.config(text=text)
        messagebox.showinfo("Saved", "Profile saved successfully!")

    def edit_profile(self):
        for k, v in self.entries.items():
            v.delete(0, tk.END)

class ScoreVaultPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("HomePage")
        ).pack(anchor="nw")

        header = tk.Frame(self, bg=DARK_GREEN)
        header.pack(pady=10)

        tk.Label(header, text="", fg=GOLD, width=3, bg=DARK_GREEN).pack(side="left")
        tk.Label(header, text="Course", fg=GOLD, width=20, bg=DARK_GREEN).pack(side="left")
        tk.Label(header, text="Unit", fg=GOLD, width=10, bg=DARK_GREEN).pack(side="left")
        tk.Label(header, text="Score", fg=GOLD, width=10, bg=DARK_GREEN).pack(side="left")

        self.rows = []
        self.body = tk.Frame(self, bg=DARK_GREEN)
        self.body.pack()

        self.add_row()

        self.scale = tk.IntVar(value=5)

        control = tk.Frame(self, bg=DARK_GREEN)
        control.pack(pady=10)

        tk.Radiobutton(control, text="Over 4", variable=self.scale, value=4).pack(side="left")
        tk.Radiobutton(control, text="Over 5", variable=self.scale, value=5).pack(side="left")

        tk.Button(control, text="Add Course", command=self.add_row).pack(side="left", padx=5)
        tk.Button(control, text="Calculate CGPA", bg=GREEN, command=self.calculate).pack(side="left", padx=5)

    def add_row(self):
        if len(self.rows) >= 11:
            return

        # Create a frame for this row
        row_frame = tk.Frame(self.body, bg=DARK_GREEN)
        row_frame.pack(anchor="w", pady=2)
        
        # Delete button
        row_index = len(self.rows)
        delete_btn = tk.Button(
            row_frame,
            text="X",
            bg="#e74c3c",
            fg="white",
            width=2,
            command=lambda idx=row_index: self.delete_row(idx)
        )
        delete_btn.pack(side="left", padx=2)
        
        row = []
        for _ in range(3):
            e = tk.Entry(row_frame, width=20)
            e.pack(side="left", padx=2)
            row.append(e)

        self.rows.append({"frame": row_frame, "entries": row})

    def delete_row(self, index):
        """Delete an entire row"""
        if 0 <= index < len(self.rows):
            # Destroy the frame
            self.rows[index]["frame"].destroy()
            # Remove from list
            self.rows.pop(index)

    def calculate(self):
        total_points = 0
        total_units = 0
        results = []

        for r in self.rows:
            try:
                course = r["entries"][0].get()
                unit = int(r["entries"][1].get())
                score = int(r["entries"][2].get())
            except:
                continue

            if unit < 0 or unit > 6 or score < 0 or score > 100:
                messagebox.showerror("Error", "Invalid unit or score")
                return

            grade, point = self.get_grade(score)

            total_points += unit * point
            total_units += unit
            results.append((course, unit, score, grade))

        if total_units == 0:
            return

        self.app.cgpa = round(total_points / total_units, 2)
        self.app.cgpa_scale = self.scale.get()
        self.app.course_data = results

        messagebox.showinfo("CGPA", f"Your CGPA is {self.app.cgpa}")

    def get_grade(self, score):
        if score <= 44:
            return "F", 0
        if score <= 49:
            return "D", 1
        if score <= 59:
            return "C", 2
        if score <= 69:
            return "B", 3
        return "A", 4 if self.scale.get() == 4 else 5

class PreviewPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("HomePage")
        ).pack(anchor="nw")

        tk.Label(
            self,
            text="Preview (PDF)",
            font=("Arial", 20),
            fg=GOLD,
            bg=DARK_GREEN
        ).pack(pady=10)

        # Text preview widget
        self.preview_text = tk.Text(self, width=90, height=25, bg="white", fg="black", font=("Courier", 10))
        self.preview_text.pack(pady=10, padx=10)
        self.preview_text.config(state="disabled")

        # Button frame
        button_frame = tk.Frame(self, bg=DARK_GREEN)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Preview",
            bg=GREEN,
            fg="black",
            width=15,
            command=self.refresh_preview
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Save",
            bg=GREEN,
            fg="black",
            width=15,
            command=self.save_to_vault
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Download PDF",
            bg=GOLD,
            fg="black",
            width=15,
            command=self.download_pdf
        ).pack(side="left", padx=5)

    def on_show(self):
        """Called when this page is shown - refresh the preview"""
        self.refresh_preview()

    def save_to_vault(self):
        """Save PDF directly to result vault"""
        if not HAS_REPORTLAB:
            messagebox.showerror(
                "Missing dependency",
                "ReportLab is not installed. Install the 'reportlab' package to enable PDF export."
            )
            return

        # Check if there's data to save
        if not self.app.profile_data and not self.app.course_data:
            messagebox.showwarning(
                "No Data",
                "Please enter profile information and calculate CGPA before saving PDF."
            )
            return

        # Generate filename
        filename = f"{self.app.current_user}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path = os.path.join(RESULT_DIR, filename)

        # Generate PDF
        try:
            c = canvas.Canvas(path, pagesize=A4)
            y = 800

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "STUDENT ACADEMIC REPORT")
            y -= 30

            c.setFont("Helvetica", 11)
            c.drawString(50, y, "PROFILE INFORMATION")
            y -= 15
            c.line(50, y, 540, y)
            y -= 15

            # Profile data
            for k, v in self.app.profile_data.items():
                c.drawString(50, y, f"{k}: {v}")
                y -= 15

            y -= 10

            # Course header
            c.drawString(50, y, "COURSE INFORMATION")
            y -= 15
            c.line(50, y, 540, y)
            y -= 15

            # Course table header
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Course")
            c.drawString(280, y, "Units")
            c.drawString(380, y, "Score")
            c.drawString(470, y, "Grade")
            y -= 12
            c.line(50, y, 540, y)
            y -= 12

            # Course data
            c.setFont("Helvetica", 10)
            for course, unit, score, grade in self.app.course_data:
                c.drawString(50, y, str(course)[:40])
                c.drawString(280, y, str(unit))
                c.drawString(380, y, str(score))
                c.drawString(470, y, str(grade))
                y -= 12

            y -= 10
            c.line(50, y, 540, y)
            y -= 15

            # CGPA summary
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"CUMULATIVE GPA (CGPA): {self.app.cgpa}")
            y -= 15
            c.drawString(50, y, f"GPA Scale: {self.app.cgpa_scale}")

            c.save()

            # Save to results file for history
            with open(RESULTS_FILE) as f:
                data = json.load(f)

            data.append({
                "user": self.app.current_user,
                "file": path,
                "cgpa": self.app.cgpa,
                "date": str(datetime.datetime.now()),
                "profile_data": self.app.profile_data,
                "course_data": self.app.course_data,
                "cgpa_scale": self.app.cgpa_scale
            })

            with open(RESULTS_FILE, "w") as f:
                json.dump(data, f)

            messagebox.showinfo("Saved", f"PDF saved to Result Vault:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")

    def refresh_preview(self):
        """Update the preview text with current profile and course data"""
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)

        # Check if data exists
        if not self.app.profile_data and not self.app.course_data:
            preview = "No data to preview yet.\n\n"
            preview += "Steps to create a PDF:\n"
            preview += "1. Go to Profile page and fill in your information, then click Save\n"
            preview += "2. Go to Score Vault and enter your courses and scores, then click Calculate CGPA\n"
            preview += "3. Return to Preview to see your PDF preview\n"
            self.preview_text.insert("1.0", preview)
            self.preview_text.config(state="disabled")
            return

        # Build preview content
        preview = "=" * 90 + "\n"
        preview += " " * 35 + "PDF PREVIEW\n"
        preview += "=" * 90 + "\n\n"

        # Profile data
        preview += "STUDENT PROFILE INFORMATION\n"
        preview += "-" * 90 + "\n"
        if self.app.profile_data:
            for k, v in self.app.profile_data.items():
                preview += f"{k:<25}: {v}\n"
        else:
            preview += "No profile information entered\n"

        preview += "\n"

        # Course data
        preview += "COURSE INFORMATION\n"
        preview += "-" * 90 + "\n"
        if self.app.course_data:
            preview += f"{'Course':<40} {'Units':<10} {'Score':<10} {'Grade':<10}\n"
            preview += "-" * 90 + "\n"
            for course, unit, score, grade in self.app.course_data:
                preview += f"{course:<40} {unit:<10} {score:<10} {grade:<10}\n"
        else:
            preview += "No course information entered\n"

        preview += "\n"
        preview += "=" * 90 + "\n"
        preview += f"CUMULATIVE GPA (CGPA): {self.app.cgpa}\n"
        preview += f"GPA Scale: {self.app.cgpa_scale}\n"
        preview += "=" * 90 + "\n"

        self.preview_text.insert("1.0", preview)
        self.preview_text.config(state="disabled")

    def download_pdf(self):
        """Save PDF to user-selected location"""
        if not HAS_REPORTLAB:
            messagebox.showerror(
                "Missing dependency",
                "ReportLab is not installed. Install the 'reportlab' package to enable PDF export."
            )
            return

        # Check if there's data to save
        if not self.app.profile_data and not self.app.course_data:
            messagebox.showwarning(
                "No Data",
                "Please enter profile information and calculate CGPA before downloading PDF."
            )
            return

        # Open save dialog
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{self.app.current_user}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        if not path:
            return

        # Generate PDF at selected location
        try:
            c = canvas.Canvas(path, pagesize=A4)
            y = 800

            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, y, "STUDENT ACADEMIC REPORT")
            y -= 30

            c.setFont("Helvetica", 11)
            c.drawString(50, y, "PROFILE INFORMATION")
            y -= 15
            c.line(50, y, 540, y)
            y -= 15

            # Profile data
            for k, v in self.app.profile_data.items():
                c.drawString(50, y, f"{k}: {v}")
                y -= 15

            y -= 10

            # Course header
            c.drawString(50, y, "COURSE INFORMATION")
            y -= 15
            c.line(50, y, 540, y)
            y -= 15

            # Course table header
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Course")
            c.drawString(280, y, "Units")
            c.drawString(380, y, "Score")
            c.drawString(470, y, "Grade")
            y -= 12
            c.line(50, y, 540, y)
            y -= 12

            # Course data
            c.setFont("Helvetica", 10)
            for course, unit, score, grade in self.app.course_data:
                c.drawString(50, y, str(course)[:40])
                c.drawString(280, y, str(unit))
                c.drawString(380, y, str(score))
                c.drawString(470, y, str(grade))
                y -= 12

            y -= 10
            c.line(50, y, 540, y)
            y -= 15

            # CGPA summary
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"CUMULATIVE GPA (CGPA): {self.app.cgpa}")
            y -= 15
            c.drawString(50, y, f"GPA Scale: {self.app.cgpa_scale}")

            c.save()

            # Save to results file for history
            with open(RESULTS_FILE) as f:
                data = json.load(f)

            data.append({
                "user": self.app.current_user,
                "file": path,
                "cgpa": self.app.cgpa,
                "date": str(datetime.datetime.now()),
                "profile_data": self.app.profile_data,
                "course_data": self.app.course_data,
                "cgpa_scale": self.app.cgpa_scale
            })

            with open(RESULTS_FILE, "w") as f:
                json.dump(data, f)

            messagebox.showinfo("Success", f"PDF saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")

class ResultVaultPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("HomePage")
        ).pack(anchor="nw")

        tk.Label(
            self,
            text="Saved Results",
            font=("Arial", 18),
            fg=GOLD,
            bg=DARK_GREEN
        ).pack(pady=10)

        # Results display as text widget (table format)
        self.results_text = tk.Text(self, width=110, height=20, bg="white", fg="black", font=("Courier", 9))
        self.results_text.pack(pady=10, padx=10)
        self.results_text.config(state="disabled")

        # Button frame
        button_frame = tk.Frame(self, bg=DARK_GREEN)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Refresh",
            bg=GREEN,
            fg="black",
            command=self.refresh
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Open File",
            bg=GOLD,
            fg="black",
            command=self.open_file
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Download",
            bg=GREEN,
            fg="black",
            command=self.download_file
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Delete",
            bg="#e74c3c",
            fg="black",
            command=self.delete_result
        ).pack(side="left", padx=5)

        self.results = []
        self.refresh()

    def on_show(self):
        """Called when this page is shown - refresh the results list"""
        self.refresh()

    def refresh(self):
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", tk.END)

        # Table header
        header = f"{'#':<4} {'Filename':<45} {'CGPA':<10} {'Date':<25}\n"
        self.results_text.insert(tk.END, header)
        self.results_text.insert(tk.END, "=" * 90 + "\n")

        with open(RESULTS_FILE) as f:
            data = json.load(f)

        self.results = []
        count = 1
        for r in data:
            if r["user"] == self.app.current_user:
                self.results.append(r)
                filename = os.path.basename(r["file"])
                date_str = r["date"][:19]  # Format datetime
                row = f"{count:<4} {filename:<45} {r['cgpa']:<10} {date_str:<25}\n"
                self.results_text.insert(tk.END, row)
                count += 1

        if count == 1:
            self.results_text.insert(tk.END, "No saved results yet.\n")

        self.results_text.config(state="disabled")

    def open_file(self):
        if not self.results:
            messagebox.showwarning("No Results", "No results to open.")
            return

        # Show selection dialog
        result_strs = [f"{os.path.basename(r['file'])} - CGPA: {r['cgpa']}" for r in self.results]
        selected_idx = self._select_from_list(result_strs, "Select result to open")

        if selected_idx is not None and 0 <= selected_idx < len(self.results):
            file_path = self.results[selected_idx]["file"]
            if os.path.exists(file_path):
                try:
                    os.startfile(file_path)  # Windows
                    messagebox.showinfo("Opening", f"Opening {os.path.basename(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")
            else:
                messagebox.showerror("Error", "File not found.")

    def download_file(self):
        if not self.results:
            messagebox.showwarning("No Results", "No results to download.")
            return

        # Show selection dialog
        result_strs = [f"{os.path.basename(r['file'])} - CGPA: {r['cgpa']}" for r in self.results]
        selected_idx = self._select_from_list(result_strs, "Select result to download")

        if selected_idx is not None and 0 <= selected_idx < len(self.results):
            result = self.results[selected_idx]
            try:
                # Open save dialog
                filename = os.path.basename(result['file'])
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=filename
                )

                if save_path:
                    # Generate formatted PDF at save location
                    self._generate_pdf_from_result(result, save_path)
                    messagebox.showinfo("Downloaded", f"PDF saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not download file: {str(e)}")

    def _generate_pdf_from_result(self, result, save_path):
        """Generate a formatted PDF from result data"""
        if not HAS_REPORTLAB:
            raise Exception("ReportLab not installed")

        c = canvas.Canvas(save_path, pagesize=A4)
        y = 800

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "STUDENT ACADEMIC REPORT")
        y -= 30

        c.setFont("Helvetica", 11)
        c.drawString(50, y, "PROFILE INFORMATION")
        y -= 15
        c.line(50, y, 540, y)
        y -= 15

        # Profile data
        profile_data = result.get("profile_data", {})
        for k, v in profile_data.items():
            c.drawString(50, y, f"{k}: {v}")
            y -= 15

        y -= 10

        # Course header
        c.drawString(50, y, "COURSE INFORMATION")
        y -= 15
        c.line(50, y, 540, y)
        y -= 15

        # Course table header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Course")
        c.drawString(280, y, "Units")
        c.drawString(380, y, "Score")
        c.drawString(470, y, "Grade")
        y -= 12
        c.line(50, y, 540, y)
        y -= 12

        # Course data
        c.setFont("Helvetica", 10)
        course_data = result.get("course_data", [])
        for course, unit, score, grade in course_data:
            c.drawString(50, y, str(course)[:40])
            c.drawString(280, y, str(unit))
            c.drawString(380, y, str(score))
            c.drawString(470, y, str(grade))
            y -= 12

        y -= 10
        c.line(50, y, 540, y)
        y -= 15

        # CGPA summary
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"CUMULATIVE GPA (CGPA): {result['cgpa']}")
        y -= 15
        cgpa_scale = result.get("cgpa_scale", 5)
        c.drawString(50, y, f"GPA Scale: {cgpa_scale}")

        c.save()

    def delete_result(self):
        if not self.results:
            messagebox.showwarning("No Results", "No results to delete.")
            return

        result_strs = [f"{os.path.basename(r['file'])} - CGPA: {r['cgpa']}" for r in self.results]
        selected_idx = self._select_from_list(result_strs, "Select result to delete")

        if selected_idx is not None and 0 <= selected_idx < len(self.results):
            result = self.results[selected_idx]
            if messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(result['file'])}?"):
                try:
                    if os.path.exists(result["file"]):
                        os.remove(result["file"])

                    # Remove from RESULTS_FILE
                    with open(RESULTS_FILE) as f:
                        data = json.load(f)

                    data = [r for r in data if r["file"] != result["file"]]

                    with open(RESULTS_FILE, "w") as f:
                        json.dump(data, f)

                    messagebox.showinfo("Deleted", "Result deleted successfully.")
                    self.refresh()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete: {str(e)}")

    def _select_from_list(self, items, title):
        """Helper to create a simple selection dialog"""
        if not items:
            return None

        selection_window = tk.Toplevel(self)
        selection_window.title(title)
        selection_window.geometry("400x300")
        selection_window.resizable(False, False)

        listbox = tk.Listbox(selection_window, height=12)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for item in items:
            listbox.insert(tk.END, item)

        selected_idx = [None]

        def on_select():
            if listbox.curselection():
                selected_idx[0] = listbox.curselection()[0]
            selection_window.destroy()

        tk.Button(
            selection_window,
            text="Select",
            command=on_select
        ).pack(pady=5)

        selection_window.wait_window()
        return selected_idx[0]

class ScoreboardPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("HomePage")
        ).pack(anchor="nw")

        # Refresh button
        button_frame = tk.Frame(self, bg=DARK_GREEN)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Refresh Rankings",
            bg=GREEN,
            fg="black",
            command=self.load_board
        ).pack(side="left", padx=5)

        self.text = tk.Text(self, width=100, height=28, bg="white", fg="black", font=("Courier", 10))
        self.text.pack(pady=10, padx=10)
        self.text.config(state="disabled")

        self.load_board()

    def on_show(self):
        """Called when this page is shown - refresh the rankings"""
        self.load_board()

    def load_board(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)

        # Table header
        header = f"{'Rank':<6} {'Username':<20} {'University':<25} {'Average CGPA':<15}\n"
        self.text.insert(tk.END, header)
        self.text.insert(tk.END, "=" * 70 + "\n")

        with open(RESULTS_FILE) as f:
            data = json.load(f)

        scores = {}
        for r in data:
            scores.setdefault(r["user"], []).append(r["cgpa"])

        ranking = sorted(
            [(u, sum(v) / len(v)) for u, v in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )

        for i, (u, g) in enumerate(ranking[:10], 1):
            row = f"{i:<6} {u:<20} {'---':<25} {round(g, 2):<15}\n"
            self.text.insert(tk.END, row)

        self.text.config(state="disabled")

class SettingsPage(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=DARK_GREEN)
        self.app = app

        tk.Button(
            self,
            text="←",
            command=lambda: app.show_frame("HomePage")
        ).pack(anchor="nw")

        tk.Label(
            self,
            text="Settings",
            font=("Arial", 22),
            fg=GOLD,
            bg=DARK_GREEN
        ).pack(pady=20)

        tk.Button(
            self,
            text="Change Background",
            bg=GREEN,
            command=self.change_background
        ).pack(pady=10)

    def change_background(self):
        path = filedialog.askopenfilename()
        if path:
            if not HAS_PIL:
                messagebox.showwarning(
                    "Missing dependency",
                    "Pillow (PIL) is not installed. Install the 'Pillow' package to use background images."
                )
                return
            self.app.background_image = path
            self.app.frames["HomePage"].refresh_background()

if __name__ == "__main__":
    ScoreGuardApp().mainloop()
