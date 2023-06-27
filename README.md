# Pac1921 Sensor Data Reader

This Python code allows you to read data from the Pac1921 sensor using the I2C communication protocol. The Pac1921 sensor is a power monitoring IC that provides accurate measurements of voltage, current, and power.

## Features

- Read voltage, current, and power data from the Pac1921 sensor.
- Perform measurements by writing to the integration register and reading the sensor values.
- Calculate the actual values from the raw register data.
- Save the sensor data to a CSV file for further analysis.

## Prerequisites

- Python 3.x
- smbus2 library (Install using `pip install smbus2`)

## Usage

1. Connect the Pac1921 sensor to your I2C bus.
2. Run the code using Python 3.x.
3. Follow the on-screen prompts to perform measurements and save the data.
4. The measured data will be displayed on the console and saved to a CSV file (`pac1921.csv`).

## Code Explanation

The code is organized into the following classes and methods:

### `Pac1921` class

Represents the Pac1921 sensor and provides methods for measurement, calculation, and data storage.

- `__init__()`: Initializes the Pac1921 object and sets up the I2C bus communication.
- `write_register()`: Writes data to the specified register address of the Pac1921 sensor.
- `read_data()`: Reads data from the sensor and combines the bytes into an integer value.
- `read_register()`: Reads the specified number of bytes from the given register address.
- `calculation()`: Calculates the actual values of voltage, current, and power based on the raw register data.
- `measurement()`: Performs the measurement by writing to the integration register and reading the sensor values.
- `measurement_value()`: Gets the measured values of voltage, current, and power.
- `print_data()`: Displays the measured sensor data on the console.
- `close()`: Closes the I2C bus connection.
- `savefile()`: Saves the measured data to a CSV file.

## License

This project is licensed under the [MIT License](LICENSE).
