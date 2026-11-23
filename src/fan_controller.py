"""Temperature-controlled DC fan using an LM35 and MCP3008."""

import time

ADC_CHANNEL = 0
FAN_PIN = 18
VREF = 3.3
ADC_MAX = 1023
SAMPLE_COUNT = 5
SAMPLE_INTERVAL = 0.1
LOOP_INTERVAL = 1.0
START_TEMP_C = 30.0
STOP_TEMP_C = 28.0
FULL_SPEED_TEMP_C = 45.0
MIN_DUTY = 0.35


def read_adc(spi, channel):
    """Read one 10-bit MCP3008 channel."""
    if not 0 <= channel <= 7:
        raise ValueError("MCP3008 channel must be between 0 and 7")
    response = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((response[1] & 3) << 8) | response[2]


def adc_to_temperature(adc_value, vref=VREF):
    """Convert the LM35's nominal 10 mV/°C output to Celsius."""
    if not 0 <= adc_value <= ADC_MAX:
        raise ValueError("ADC reading must be between 0 and 1023")
    if vref <= 0:
        raise ValueError("ADC reference voltage must be positive")
    voltage = adc_value * vref / ADC_MAX
    return voltage * 100.0


def fan_state_and_duty(
    temperature_c,
    fan_on,
    start_temp=START_TEMP_C,
    stop_temp=STOP_TEMP_C,
    full_speed_temp=FULL_SPEED_TEMP_C,
    min_duty=MIN_DUTY,
):
    """Apply hysteresis and return the updated fan state and PWM duty."""
    if stop_temp >= start_temp:
        raise ValueError("stop_temp must be lower than start_temp")
    if full_speed_temp <= start_temp:
        raise ValueError("full_speed_temp must be higher than start_temp")
    if not 0.0 < min_duty <= 1.0:
        raise ValueError("min_duty must be greater than 0 and at most 1")

    if fan_on:
        fan_on = temperature_c > stop_temp
    else:
        fan_on = temperature_c >= start_temp

    if not fan_on:
        return False, 0.0

    fraction = (temperature_c - start_temp) / (full_speed_temp - start_temp)
    duty = min(1.0, max(min_duty, fraction))
    return True, duty


def read_temperature(spi):
    """Average ADC samples and convert the result to Celsius."""
    readings = []
    for _ in range(SAMPLE_COUNT):
        readings.append(read_adc(spi, ADC_CHANNEL))
        time.sleep(SAMPLE_INTERVAL)
    return adc_to_temperature(sum(readings) / len(readings))


def main():
    import spidev
    from gpiozero import PWMOutputDevice

    spi = spidev.SpiDev()
    fan = PWMOutputDevice(FAN_PIN, initial_value=0)
    fan_on = False

    try:
        spi.open(0, 0)
        spi.max_speed_hz = 1_350_000
        print("Fan controller running; press Ctrl+C to stop.")

        while True:
            temperature_c = read_temperature(spi)
            fan_on, duty = fan_state_and_duty(temperature_c, fan_on)
            fan.value = duty
            print(
                "Temperature: {:.1f} °C | Fan: {} | PWM: {:.0f}%".format(
                    temperature_c,
                    "ON" if fan_on else "OFF",
                    duty * 100,
                )
            )
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping fan controller.")
    finally:
        fan.off()
        fan.close()
        spi.close()


if __name__ == "__main__":
    main()
