import unittest
from unittest.mock import MagicMock
from hardware.motor_controller import MotorController

class TestMotorController(unittest.TestCase):
    def setUp(self):
        self.device = MotorController("COM1", 19200)
        self.device.send = MagicMock()

    def test_run_forward(self):
        self.device.run_forward()
        self.device.send.assert_called_once()