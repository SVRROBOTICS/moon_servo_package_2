import time
import math
from .connection import ModbusConnection


# Function to convert desired linear speed (m/s) to motor units
def mps_to_motor_units(speed_mps, wheel_diameter=0.125, scale=240, gearbox_ratio=20):
    circumference = 3.14159 * wheel_diameter  # Wheel circumference in meters
    rps = speed_mps / circumference  # Convert m/s to rps
    motor_rps = rps * gearbox_ratio  # Account for gearbox ratio
    motor_units = int(motor_rps * scale)  # Convert rps to motor units
    return motor_units

class MoonServoMotor:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, base_address: int = 0):
        connection: ModbusConnection = ModbusConnection(port=port, baudrate=baudrate, timeout=5, parity='N', stopbits=1, bytesize=8)
        self.client = connection.get_client()
        self.base_address = base_address

    def connect(self):
        if self.client.connect():
            print("Modbus Connection Successful")
            return True
        else:
            raise ConnectionError("Modbus Connection Failed")

    def disconnect(self):
        self.client.close()
        print("Modbus Connection Closed")

    def enable_driver1(self):
        command_register = self.base_address + 124
        opcode = 0x009F
        self._write_register1(command_register, opcode, "Enable driver")

    def enable_driver2(self):
        command_register = self.base_address + 1124
        opcode = 0x009F
        self._write_register2(command_register, opcode, "Enable driver")


    def disable_driver1(self):
        command_register = self.base_address + 124
        opcode = 0x009E
        self._write_register1(command_register, opcode, "Disable driver")

    def disable_driver2(self):
        command_register = self.base_address + 1124
        opcode = 0x009E
        self._write_register2(command_register, opcode, "Disable driver")    

    def start_jogging1(self):
        command_register = self.base_address + 124
        opcode = 0x0096
        self._write_register1(command_register, opcode, "Start jogging")

    def start_jogging2(self):
        command_register = self.base_address + 1124
        opcode = 0x0096
        self._write_register2(command_register, opcode, "Start jogging")    

    def stop_jogging1(self):
        command_register = self.base_address + 124
        opcode = 0x00D8
        self._write_register1(command_register, opcode, "Stop jogging")

    def stop_jogging2(self):
        command_register = self.base_address + 1124
        opcode = 0x00D8
        self._write_register2(command_register, opcode, "Stop jogging")


    
    def set_speed1(self, speed_mps, run_time=5):
        speed_value = mps_to_motor_units(speed_mps)
        speed_register = self.base_address + 342
        self._write_32bit_register1(speed_register, speed_value, "Set speed")
        time.sleep(run_time)
        self._write_32bit_register1(speed_register, 0, "Stop motor after timeout")

    def set_speed2(self, speed_mps, run_time=5):
        speed_value = mps_to_motor_units(speed_mps)
        speed_register = self.base_address + 1342
        self._write_32bit_register2(speed_register, speed_value, "Set speed")
        time.sleep(run_time)
        self._write_32bit_register2(speed_register, 0, "Stop motor after timeout")    
    
    def set_acceleration1(self, accel_value):
        accel_register = self.base_address + 338
        self._write_32bit_register1(accel_register, accel_value, "Set acceleration")

    def set_acceleration2(self, accel_value):
        accel_register = self.base_address + 1338
        self._write_32bit_register2(accel_register, accel_value, "Set acceleration")    

    def set_deceleration1(self, decel_value):
        decel_register = self.base_address + 340
        self._write_32bit_register1(decel_register, decel_value, "Set deceleration")

    def set_deceleration2(self, decel_value):
        decel_register = self.base_address + 1340
        self._write_32bit_register2(decel_register, decel_value, "Set deceleration")

    def _write_register1(self, register, value, action):
        try:
            self.client.write_register(register, value)
            print(f"{action} successful.")
        except Exception as e:
            print(f"Error during {action}: {e}")
            raise

    def _write_register2(self, register, value, action):
        try:
            self.client.write_register(register, value)
            print(f"{action} successful.")
        except Exception as e:
            print(f"Error during {action}: {e}")
            raise
    

    def _write_32bit_register1(self, register, value, action):
        try:
            high_word = (value >> 16) & 0xFFFF
            low_word = value & 0xFFFF
            self.client.write_registers(register, [high_word, low_word])
            print(f"{action} successful.")
        except Exception as e:
            print(f"Error during {action}: {e}")
            raise
        
    def _write_32bit_register2(self, register, value, action):
        try:
            high_word = (value >> 16) & 0xFFFF
            low_word = value & 0xFFFF
            self.client.write_registers(register, [high_word, low_word])
            print(f"{action} successful.")
        except Exception as e:
            print(f"Error during {action}: {e}")
            raise    

    def read_register_32bit1(self,register_address, endian='big'):
        """
        Reads a 32-bit value from a Modbus register.
        
        :param register_address: The starting address of the register (Modbus address).
        :param endian: The byte order, 'big' or 'little'. Defaults to 'big'.
        :return: The 32-bit integer value, or None if an error occurs.
        """
        zero_based_address = register_address - 40001  # Convert to zero-based address
        
        try:
            # Read two 16-bit registers
            result = self.client.read_holding_registers(zero_based_address, 2)
            
            if result.isError():
                print(f"Error reading register {register_address}, error: {result}")
                return None
            
            # Combine the two 16-bit registers into a 32-bit integer
            high, low = result.registers
            if endian == 'big':
                value = (high << 16) | low  # Big-endian: High word first
            elif endian == 'little':
                value = (low << 16) | high  # Little-endian: Low word first
            else:
                raise ValueError("Invalid endian type. Use 'big' or 'little'.")
            
            print(f"Value at register {register_address}: {value}")
            return value
        
        except Exception as e:
            print(f"Error reading register {register_address}: {e}")
            return None

    def read_register_32bit2(self,register_address, endian='big'):
        """
        Reads a 32-bit value from a Modbus register.
        
        :param register_address: The starting address of the register (Modbus address).
        :param endian: The byte order, 'big' or 'little'. Defaults to 'big'.
        :return: The 32-bit integer value, or None if an error occurs.
        """
        zero_based_address = register_address - 40001  # Convert to zero-based address
        
        try:
            # Read two 16-bit registers
            result = self.client.read_holding_registers(zero_based_address, 2)
            
            if result.isError():
                print(f"Error reading register {register_address}, error: {result}")
                return None
            
            # Combine the two 16-bit registers into a 32-bit integer
            high, low = result.registers
            if endian == 'big':
                value = (high << 16) | low  # Big-endian: High word first
            elif endian == 'little':
                value = (low << 16) | high  # Little-endian: Low word first
            else:
                raise ValueError("Invalid endian type. Use 'big' or 'little'.")
            
            print(f"Value at register {register_address}: {value}")
            return value
        
        except Exception as e:
            print(f"Error reading register {register_address}: {e}")
            return None  
