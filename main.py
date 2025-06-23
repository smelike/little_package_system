from hardware.motor_controller import MotorController
from hardware.sorting_module import SortingModule
from time import sleep

def main():
    # Shared COM port with different baudrates
    COM_PORT = "COM3"

    # Instantiate and test MotorController (19200 baud)
    motor = MotorController(COM_PORT, 19200)
    motor.set_speed(1500)
    motor.run_forward()
    sleep(1)
    motor.stop()
    motor.reset()

    # Instantiate and test SortingModule (38400 baud)
    sorter = SortingModule(COM_PORT, 38400)
    sorter.turn_left()
    sleep(0.5)
    sorter.back_to_middle()
    sleep(0.5)
    sorter.turn_right()

    # Close shared port
    motor.close()

if __name__ == "__main__":
    main()