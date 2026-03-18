import customtkinter as ctk
import psutil
import subprocess
import threading
import os
import sys

# სისტემური მონაცემები
max_cores = psutil.cpu_count(logical=True)
total_ram_gb = psutil.virtual_memory().total / (1024**3)
zpaq_exe = os.path.abspath("zpaq.exe")
ZPAQ_MEM_REQ = {1: 0.1, 2: 0.25, 3: 1.0, 4: 4.0, 5: 16.0}

# მარჯვენა ღილაკიდან გადმოწოდებული მისამართის წაკითხვა
selected_path = sys.argv[1] if len(sys.argv) > 1 else ""
is_archive = selected_path.lower().endswith('.zpaq')

def check_resources():
    cores = int(cpu_slider.get())
    level = int(level_slider.get())
    allocated_ram_gb = total_ram_gb * (int(ram_slider.get()) / 100)
    required_ram = ZPAQ_MEM_REQ[level] * cores
    
    if required_ram > allocated_ram_gb:
        level_label.configure(text_color="red", text=f"კომპრესიის დონე: {level} (არასაკმარისი RAM!)")
    else:
        level_label.configure(text_color="green", text=f"კომპრესიის დონე: {level} (რესურსი საკმარისია)")

def update_cpu(value):
    cpu_label.configure(text=f"ბირთვები (1 - {max_cores}): {int(value)}")
    check_resources()

def update_ram(value):
    percent = int(value)
    ram_label.configure(text=f"RAM-ის ლიმიტი: {percent}% (დაახლ. {(total_ram_gb * percent / 100):.1f} GB)")
    check_resources()

def update_level(value):
    check_resources()

def run_process():
    if not selected_path:
        log_box.insert(ctk.END, "შეცდომა: მისამართი არ მოიძებნა!\n")
        return

    action_btn.configure(state="disabled", fg_color="gray")
    progress_bar.start()
    
    working_dir = os.path.dirname(selected_path)
    target_name = os.path.basename(selected_path)

    if is_archive:
        # ამოღების ლოგიკა
        extract_folder = target_name.replace('.zpaq', '_extracted')
        command = [zpaq_exe, "x", target_name, "-to", extract_folder]
        log_box.insert(ctk.END, f"ვიწყებთ ამოღებას საქაღალდეში: {extract_folder}...\n")
    else:
        # შეკუმშვის ლოგიკა
        cores = int(cpu_slider.get())
        level = int(level_slider.get())
        archive_name = f"{target_name}.zpaq"
        command = [zpaq_exe, "add", archive_name, target_name, f"-t{cores}", f"-m{level}"]
        log_box.insert(ctk.END, f"ვიწყებთ შეკუმშვას არქივში: {archive_name}...\n")

    def process_thread():
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW, cwd=working_dir)
            for line in process.stdout:
                app.after(0, log_box.insert, ctk.END, line)
                app.after(0, log_box.see, ctk.END)
            process.wait()
            app.after(0, log_box.insert, ctk.END, "\nპროცესი დასრულდა!\n")
        except Exception as e:
            app.after(0, log_box.insert, ctk.END, f"\nშეცდომა: {str(e)}\n")
        finally:
            app.after(0, progress_bar.stop)
            app.after(0, action_btn.configure, state="normal", fg_color="green" if not is_archive else "#1f538d")

    threading.Thread(target=process_thread, daemon=True).start()

# --- GUI ინიციალიზაცია ---
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("ZPAQ არქივატორი")

if not selected_path:
    app.geometry("400x200")
    ctk.CTkLabel(app, text="გთხოვთ გაუშვათ პროგრამა\nფაილზე მარჯვენა ღილაკის დაჭერით.", font=("Arial", 16), text_color="red").pack(pady=50)
else:
    target_basename = os.path.basename(selected_path)
    
    if is_archive:
        app.geometry("450x350")
        ctk.CTkLabel(app, text="რეჟიმი: დეკომპრესაცია (ამოღება)", font=("Arial", 16, "bold"), text_color="cyan").pack(pady=(15, 5))
        ctk.CTkLabel(app, text=f"ფაილი: {target_basename}", font=("Arial", 14)).pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(app, mode="indeterminate")
        progress_bar.pack(pady=20, fill="x", padx=40)
        
        action_btn = ctk.CTkButton(app, text="ამოღება", command=run_process, font=("Arial", 14))
        action_btn.pack(pady=10)
        
    else:
        app.geometry("500x600")
        ctk.CTkLabel(app, text="რეჟიმი: კომპრესაცია (შეკუმშვა)", font=("Arial", 16, "bold"), text_color="orange").pack(pady=(15, 5))
        ctk.CTkLabel(app, text=f"სამიზნე: {target_basename}", font=("Arial", 14)).pack(pady=5)
        
        # შეკუმშვის პარამეტრები
        cpu_label = ctk.CTkLabel(app, text=f"ბირთვები (1 - {max_cores}): {max_cores}", font=("Arial", 14))
        cpu_label.pack(pady=(15, 0))
        cpu_slider = ctk.CTkSlider(app, from_=1, to=max_cores, number_of_steps=max_cores-1, command=update_cpu)
        cpu_slider.set(max_cores)
        cpu_slider.pack(pady=5)

        ram_label = ctk.CTkLabel(app, text=f"RAM-ის ლიმიტი: 50% (დაახლ. {total_ram_gb * 0.5:.1f} GB)", font=("Arial", 14))
        ram_label.pack(pady=(15, 0))
        ram_slider = ctk.CTkSlider(app, from_=10, to=100, number_of_steps=90, command=update_ram)
        ram_slider.set(50)
        ram_slider.pack(pady=5)

        level_label = ctk.CTkLabel(app, text="კომპრესიის დონე: 3", font=("Arial", 14, "bold"))
        level_label.pack(pady=(15, 0))
        level_slider = ctk.CTkSlider(app, from_=1, to=5, number_of_steps=4, command=update_level)
        level_slider.set(3)
        level_slider.pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(app, mode="indeterminate")
        progress_bar.pack(pady=20, fill="x", padx=40)

        action_btn = ctk.CTkButton(app, text="შეკუმშვა", command=run_process, font=("Arial", 14), fg_color="green")
        action_btn.pack(pady=10)
        
        check_resources()

    # ლოგების ველი ორივე რეჟიმისთვის
    log_box = ctk.CTkTextbox(app, width=400, height=120, font=("Consolas", 12))
    log_box.pack(pady=10)

app.mainloop()