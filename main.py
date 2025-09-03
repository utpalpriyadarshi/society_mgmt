import sys
from PyQt5.QtWidgets import QApplication, QDialog
from gui.login_diaglog import LoginDialog
from gui.main_window import MainWindow
from utils.security import authenticate_user


class MainController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.current_username = None
        self.current_role = None
        
    def show_login(self):
        login = LoginDialog()
        if login.exec_() == QDialog.Accepted:
            username = login.username_input.text()
            password = login.password_input.text()
            
            # Authenticate user
            user_role = authenticate_user(username, password)
            if user_role:
                print("Login successful!")
                self.current_username = username
                self.current_role = user_role
                self.show_main_window()
                return True
            else:
                print("Authentication failed")
                return False
        else:
            print("Login cancelled")
            return False
            
    def show_main_window(self):
        if self.main_window:
            self.main_window.close()
        self.main_window = MainWindow(self.current_role, self.current_username, self)
        self.main_window.show()
        
    def logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.show_login()
        
    def run(self):
        if self.show_login():
            sys.exit(self.app.exec_())


def main():
    controller = MainController()
    controller.run()

if __name__ == "__main__":
    main()
    