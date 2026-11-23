import unittest

from src.fan_controller import adc_to_temperature, fan_state_and_duty


class AdcConversionTests(unittest.TestCase):
    def test_converts_lm35_reading(self):
        self.assertAlmostEqual(adc_to_temperature(31, 3.3), 10.0, delta=0.1)

    def test_rejects_out_of_range_adc_value(self):
        with self.assertRaises(ValueError):
            adc_to_temperature(1024)


class FanControlTests(unittest.TestCase):
    def test_hysteresis_keeps_fan_state_between_thresholds(self):
        self.assertEqual(fan_state_and_duty(29.0, False), (False, 0.0))
        on, duty = fan_state_and_duty(29.0, True)
        self.assertTrue(on)
        self.assertGreater(duty, 0.0)

    def test_thresholds_turn_fan_on_and_off(self):
        self.assertEqual(fan_state_and_duty(30.0, False)[0], True)
        self.assertEqual(fan_state_and_duty(28.0, True), (False, 0.0))

    def test_duty_increases_and_is_capped(self):
        _, low_duty = fan_state_and_duty(32.0, True)
        _, high_duty = fan_state_and_duty(40.0, True)
        _, max_duty = fan_state_and_duty(50.0, True)
        self.assertLess(low_duty, high_duty)
        self.assertEqual(max_duty, 1.0)


if __name__ == "__main__":
    unittest.main()
