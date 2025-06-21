from common.config_loader import load_config
from hardware.motor_controller import MotorController
from hardware.sorting_module import SortingModule

def main():
    config = load_config()

    motor_cfg = config['serial']['motor']
    sorter_cfg = config['serial']['sorter']

    motor = MotorController(motor_cfg['port'], motor_cfg['baudrate'])
    motor.connect()
    motor.set_speed_3000()
    motor.run_forward()
    motor.stop()
    motor.close()

    sorter = SortingModule(sorter_cfg['port'], sorter_cfg['baudrate'])
    sorter.connect()
    sorter.turn_left()
    sorter.back_to_middle()
    sorter.turn_right()
    sorter.close()

if __name__ == "__main__":
    main()