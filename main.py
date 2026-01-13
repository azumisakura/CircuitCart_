# main.py
from app_controller import CircuitLendController
from gui import CircuitLendGUI

def main():
    controller = CircuitLendController()
    gui = CircuitLendGUI(controller)
    gui.run()

if __name__ == "__main__":
    main()
