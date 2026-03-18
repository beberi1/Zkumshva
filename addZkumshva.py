import winreg
import os
import sys
import shutil

def install_and_add_to_registry():
    # მიმდინარე საქაღალდის დადგენა (სადაც add_menu.exe გაეშვა)
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # სად გვინდა გადატანა
    target_dir = r"C:\Program Files\ZPAQ_App"
    
    source_app = os.path.join(current_dir, "Zkumshva.exe")
    source_zpaq = os.path.join(current_dir, "zpaq.exe")
    target_app = os.path.join(target_dir, "Zkumshva.exe")
    
    try:
        # 1. ფაილების კოპირება C: დისკზე
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        if os.path.exists(source_app) and os.path.exists(source_zpaq):
            shutil.copy2(source_app, target_dir)
            shutil.copy2(source_zpaq, target_dir)
            print(f"ფაილები გადაკოპირდა აქ: {target_dir}")
        else:
            print("შეცდომა: Zkumshva.exe ან zpaq.exe ვერ მოიძებნა ამ საქაღალდეში!")
            return

        # 2. რეესტრის ჩანაწერის შექმნა ახალი მისამართით
        command = f'"{target_app}" "%1"'
        
        # ფაილებისთვის
        key_file = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\ZPAQ_App")
        winreg.SetValue(key_file, "", winreg.REG_SZ, "ZPAQ-ით შეკუმშვა/ამოღება")
        key_file_cmd = winreg.CreateKey(key_file, r"command")
        winreg.SetValue(key_file_cmd, "", winreg.REG_SZ, command)

        # საქაღალდეებისთვის
        key_dir = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\ZPAQ_App")
        winreg.SetValue(key_dir, "", winreg.REG_SZ, "ZPAQ-ით შეკუმშვა")
        key_dir_cmd = winreg.CreateKey(key_dir, r"command")
        winreg.SetValue(key_dir_cmd, "", winreg.REG_SZ, command)
        
        print("წარმატება: ინსტალაცია და რეესტრში ჩამატება დასრულდა!")
        
    except PermissionError:
        print("შეცდომა: სკრიპტი აუცილებლად უნდა გაუშვათ ადმინისტრატორის უფლებებით!")
    except Exception as e:
        print(f"შეცდომა: {e}")

if __name__ == "__main__":
    install_and_add_to_registry()
    input("დააჭირეთ Enter-ს გამოსასვლელად...")