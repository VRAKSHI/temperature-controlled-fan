# Temperature-Controlled Fan

A Raspberry Pi temperature-controlled fan using an LM35 analog temperature
sensor, an MCP3008 SPI ADC, and PWM fan control with hysteresis.

## Features

- Reads the LM35 through MCP3008 channel 0.
- Averages several ADC samples to reduce noise.
- Turns the fan on at the start threshold and off at a lower stop threshold.
- Gradually increases PWM duty while the fan is on.
- Includes hardware-independent tests for temperature and hysteresis behavior.

## Hardware

- Raspberry Pi with SPI enabled
- LM35 temperature sensor
- MCP3008 ADC
- DC fan and a suitable logic-level MOSFET or transistor driver
- Separate fan power supply, as required by the fan

### Wiring

| MCP3008 | Raspberry Pi |
| --- | --- |
| VDD, VREF | 3.3 V |
| AGND, DGND | GND |
| CLK | GPIO11 / SCLK |
| DOUT | GPIO9 / MISO |
| DIN | GPIO10 / MOSI |
| CS/SHDN | GPIO8 / CE0 |

| Signal | Connection |
| --- | --- |
| LM35 output | MCP3008 CH0 |
| LM35 supply and ground | Suitable supply and common ground; verify the sensor's datasheet and pinout |
| Fan driver control | GPIO18 |
| Fan power | Separate supply through the driver |

**Electrical safety:** Do not connect a fan directly to a Raspberry Pi GPIO.
Use a properly rated driver and fan supply, and connect the Pi and fan-supply
grounds together. Fit a flyback diode when required by the fan/driver (for
example, with a brushed DC motor). The MCP3008 inputs must stay between ground
and VREF (3.3 V in this wiring); check the LM35 output over the full expected
temperature range and add appropriate signal conditioning if it could exceed
that limit. This example PWM-switches a DC fan's power through a driver; it is
not a 4-wire PC fan PWM-input circuit.

Enable SPI with `sudo raspi-config` (Interface Options > SPI), then reboot if
prompted.

## Install

On the Raspberry Pi:

```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip install -r requirements.txt
```

`gpiozero` uses the available GPIO pin factory. If the default backend is not
available on your Raspberry Pi OS installation, install and configure a
supported backend such as `pigpio` or `lgpio`.

## Run

```bash
python src/fan_controller.py
```

Defaults in `src/fan_controller.py`:

- ADC channel: `0`
- Fan control pin: BCM `18`
- Start fan at: `30 °C`
- Stop fan at: `28 °C`
- Reach full duty at: `45 °C`
- Sensor reference voltage: `3.3 V`

Adjust thresholds and wiring constants in the script for your build. The LM35
conversion assumes its nominal 10 mV/°C output and the MCP3008's 10-bit range.
Confirm the reference voltage and sensor calibration for your hardware.

## Test

The unit tests do not require Raspberry Pi hardware:

```bash
python -m unittest discover -s tests -v
```

## Troubleshooting

- **SPI device error:** Enable SPI and verify the MCP3008 wiring, especially
  CE0, MOSI, MISO, and SCLK.
- **Unexpected temperature:** Check LM35 pinout, shared ground, VREF, and the
  sensor's datasheet. Keep the ADC input within its allowed range.
- **Fan does not start:** Verify the driver circuit and fan supply. Some fans
  need a minimum starting duty cycle; adjust `MIN_DUTY` if appropriate.
- **GPIO backend error:** Install/configure a GPIO Zero-compatible pin factory.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
