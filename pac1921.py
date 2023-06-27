import smbus2
from smbus2 import i2c_msg
import time
import os
import csv


class Pac1921:
    ADDRESS_DEVICE = 0X4C
    ADDRESS_GAIN = 0X00
    ADDRESS_INTEGRATION = 0X01
    ADDRESS_CONTROL = 0X02
    ADDRESS_V_BUS = 0X10
    ADDRESS_V_SENSE = 0X12
    ADDRESS_OVERFLOW = 0X1C
    CONTROL_DELAY = 0.15

    def __init__(self, bus=None):
        if bus is None:
            bus = 0
        self.bus = smbus2.SMBus(int(bus))

        self.v_bus = 0          # value V
        self.v_sense = 0        # value V
        self.i_sense = 0        # value A
        self.v_power = 0        # value W
        self.overflow = 0       # save as binary

        self.v_bus_register = []    # value from register v_bus
        self.v_sense_register = []  # value from register v_sense
        self.v_power_register = []  # value from register v_power
        self.overflow_register = []  # value from register overflow

        self.fileName = "pac1921.csv"

        self.write_register(self.ADDRESS_GAIN, 0x01)
        time.sleep(self.CONTROL_DELAY)
        self.write_register(self.ADDRESS_CONTROL, 0x02)
        time.sleep(self.CONTROL_DELAY)

    def write_register(self, register_address, data):
        """
        Write value to register, for this usage device address is 0x4c
        :param register_address: register address to write
        :param data: data to write
        :return:
        """
        write = i2c_msg.write(self.ADDRESS_DEVICE, [register_address, data])
        self.bus.i2c_rdwr(write)

    def read_data(self, data):
        """
        function to convert two 8bit data to one 16-bit
        :param data: list of 8-bit data
        :return: combine of 8-bit data and crate 16 bit value
        """
        value = ((data[0] << 8) | data[1])
        return value

    def read_register(self, reg_addr, byte=None):
        """
        Function to read data from a register. If byte is not defined, read 2 bytes.
        :param reg_addr: Register address
        :param byte: Number of bytes to read
        :return: List of 8-bit values
        """
        if byte is None:
            byte = 2

        write = i2c_msg.write(self.ADDRESS_DEVICE, [reg_addr])
        self.bus.i2c_rdwr(write)

        read = i2c_msg.read(self.ADDRESS_DEVICE, byte)
        self.bus.i2c_rdwr(read)

        return list(read)

    def calculation(self, v_bus, v_sense, v_power):
        """
        function calculate value to Volt, V sense, Amps, Watt
        :param v_bus: decimal value from 16 bit register
        :param v_sense: decimal value from 16 bit register
        :param v_power: decimal value from 16 bit register
        :return: none
        """
        self.v_bus = v_bus * 16 / 65408            # save as Volts
        self.v_sense = (v_sense * 0.1 / 65408)     # save as Volts
        self.i_sense = self.v_sense / 0.02          # save as Amps
        self.v_power = v_power * 80 / 65408        # save as Watt

    def measurement(self):
        """
        Perform measurement by writing to the integration register and reading the values from the device.
        :return: none
        """
        self.write_register(self.ADDRESS_INTEGRATION, 0x3f)
        time.sleep(self.CONTROL_DELAY)
        self.write_register(self.ADDRESS_INTEGRATION, 0x3e)
        time.sleep(3)

        self.v_bus_register = self.read_register(0x10)
        time.sleep(self.CONTROL_DELAY)
        self.v_sense_register = self.read_register(0x12)
        time.sleep(self.CONTROL_DELAY)
        self.v_power_register = self.read_register(0x1D)
        time.sleep(self.CONTROL_DELAY)
        self.overflow_register = self.read_register(0x1C, 1)
        time.sleep(self.CONTROL_DELAY)
        self.overflow = bin(self.overflow_register[0])

        self.calculation(self.read_data(self.v_bus_register), self.read_data(self.v_sense_register),
                         self.read_data(self.v_power_register))

    def measurement_value(self):
        """
        Get the measured values.
        :return: Tuple containing the rounded v_bus, i_sense, and v_power values.
        """
        return round(self.v_bus, 2), round(self.i_sense, 2), round(self.v_power, 2)

    def print_data(self):
        """
        print data in terminal
        :return: none
        """
        print()
        print(f"V_bus:\t\t{round(self.v_bus, 3)}[V]\nV_sense:\t{round(self.v_sense, 3)}[V]\n"
              f"I_sense:\t{round(self.i_sense, 3)}[A]\nPower:\t\t{round(self.v_power, 3)}[W]")
        print()
        print(f"TYPE:"
              f"\t\tHEX\t\tHEX\t\tDEC\t\tDEC\t\tDEC\t\tHEX\t\tHEX\t\tDEC\t\tDEC"
              f"\t\tDEC\t\tHEX\t\tHEX\t\tDEC\t\tDEC\t\tDEC\t\tBIN")
        print(f"REGISTER:"
              f"\t0x10\t0x11\t0x10\t0x11\tV_bus\t0x12\t0x13\t0x12\t0x13\tV_sense\t"
              f"0x1D\t0x1E\t0x1D\t0x1E\tV_power\toverflow")
        print(f"VALUE:\t\t"
              f"0x{self.v_bus_register[0]:02X}\t0x{self.v_bus_register[1]:02X}\t{self.v_bus_register[0]}\t\t"
              f"{self.v_bus_register[1]}\t\t{self.read_data(self.v_bus_register)}\t"
              f"0x{self.v_sense_register[0]:02X}\t0x{self.v_sense_register[1]:02X}\t"
              f"{self.v_sense_register[0]}\t\t{self.v_sense_register[1]}\t\t{self.read_data(self.v_sense_register)}\t"
              f"0x{self.v_power_register[0]:02X}\t0x{self.v_power_register[1]:02X}\t"
              f"{self.v_power_register[0]:}\t\t{self.v_power_register[1]}\t\t{self.read_data(self.v_power_register)}"
              f"\t{self.overflow}")
        print()

    def close(self):
        """
        close i2c connection
        :return: none
        """
        self.bus.close()

    def savefile(self):
        """
        save data to file csv
        :return: none
        """
        file_exists = os.path.isfile(self.fileName)

        headers = ['VbusH[HEX]', 'VbusL[HEX]', 'VbusH[DEC]', 'VbusL[DEC]', 'Vbus[DEC]', 'Vbus[V]',
                   'VsenseH[HEX]', 'VsenseL[HEX]', 'VsenseH[DEC]', 'VsenseL[DEC]', 'Vsense[DEC]',
                   'VpowerH[HEX]', 'VpowerL[HEX]', 'VpowerH[DEC]', 'VpowerL[DEC]', 'Vpower[DEC]',
                   'overflow[BIN]', 'V_bus', 'V_sense', 'I_sense', 'V_power']

        with open(self.fileName, 'a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(headers)

            VbusH_HEX = f'{self.v_bus_register[1]:02X}'
            VbusL_HEX = f'{self.v_bus_register[0]:02X}'
            VbusH_DEC = self.v_bus_register[1]
            VbusL_DEC = self.v_bus_register[0]
            VbusDEC_DEC = self.read_data(self.v_bus_register)
            VbusV = self.v_bus

            VsenseH_HEX = f'{self.v_sense_register[1]:02X}'
            VsenseL_HEX = f'{self.v_sense_register[0]:02X}'
            VsenseH_DEC = self.v_sense_register[1]
            VsenseL_DEC = self.v_sense_register[0]
            Vsense_DEC = self.read_data(self.v_sense_register)

            VpowerH_HEX = f'{self.v_power_register[1]:02X}'
            VpowerL_HEX = f'{self.v_power_register[0]:02X}'
            VpowerH_DEC = self.v_power_register[1]
            VpowerL_DEC = self.v_power_register[0]
            Vpower_DEC = self.read_data(self.v_power_register)
            overflow = self.overflow
            V_bus = self.v_bus
            V_sense = self.v_sense
            I_sense = self.i_sense
            V_power = self.v_power

            row = [VbusH_HEX, VbusL_HEX, VbusH_DEC, VbusL_DEC, VbusDEC_DEC, VbusV, VsenseH_HEX, VsenseL_HEX,
                   VsenseH_DEC, VsenseL_DEC, Vsense_DEC, VpowerH_HEX, VpowerL_HEX,VpowerH_DEC, VpowerL_DEC, Vpower_DEC,
                   overflow, V_bus, V_sense, I_sense, V_power]
            writer.writerow(row)

            file.close()


if __name__ == "__main__":
    pac1921 = Pac1921(0)

    while True:
        choice = input("Next? [y/n]: ")
        if choice == 'y':
            pac1921.measurement()
            pac1921.print_data()
            pac1921.savefile()
        elif choice == 'n':
            pac1921.close()
            break
