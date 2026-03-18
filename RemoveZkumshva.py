import winreg
import os
import shutil

def uninstall_and_remove():
    # 1. რეესტრიდან ჩანაწერების წაშლა
    try:
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\ZPAQ_App\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\ZPAQ_App")
        
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\ZPAQ_App\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\ZPAQ_App")
        print("რეესტრიდან მენიუ წაიშალა.")
    except FileNotFoundError:
        print("რეესტრში ჩანაწერი არ მოიძებნა.")
    except PermissionError:
        print("შეცდომა: გაუშვით სკრიპტი ადმინისტრატორის უფლებებით!")
        return

    # 2. C: დისკიდან ფაილების წაშლა
    target_dir = r"C:\Program Files\ZPAQ_App"
    try:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
            print(f"საქაღალდე და ფაილები წაიშალა: {target_dir}")
        else:
            print("სამუშაო საქაღალდე უკვე წაშლილია.")
    except Exception as e:
        print(f"ფაილების წაშლის შეცდომა: {e}")

if __name__ == "__main__":
    uninstall_and_remove()
    input("დააჭირეთ Enter-ს გამოსასვლელად...")