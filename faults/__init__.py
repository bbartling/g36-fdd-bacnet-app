class Cache:
    def __init__(self):
        self._items = []

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def add(self, item: float) -> None:
        self._items.append(item)

    def mean(self) -> float:
        if self._items:
            mean_value = sum(self._items) / len(self._items)
            self._items = []
        else:
            mean_value = 0.0
        return mean_value

    def clear(self) -> None:
        self._items.clear()


class FaultEquationOne:
    def __init__(self):
        # tuning params
        self.supply_air_static_pressure_err_thres_pv = None
        self.fan_vfd_max_speed_err_thres_pv = None
        self.fan_vfd_err_thres_pv = None

        # fan status
        self.fan_status = False

        # caches
        self.supply_air_static_pressure_cache = Cache()
        self.supply_air_static_pressure_setpoint_cache = Cache()
        self.fan_vfd_cache = Cache()

    # also assigns supply fan status
    def hi_fan_speed_check(self) -> bool:
        motor_speed_mean = self.fan_vfd_cache.mean()
        self.fan_status = True if motor_speed_mean > 0 else False
        return motor_speed_mean >= (
            self.fan_vfd_max_speed_err_thres_pv - self.fan_vfd_err_thres_pv
        )

    def low_duct_pressure_check(self) -> bool:
        pressure_mean = self.supply_air_static_pressure_cache.mean()
        setpoint_mean = self.supply_air_static_pressure_setpoint_cache.mean()
        return pressure_mean < (
            setpoint_mean - self.supply_air_static_pressure_err_thres_pv
        )

    def run_fault_check(self) -> bool:
        return self.low_duct_pressure_check() and self.hi_fan_speed_check()

    def add_supply_air_static_pressure_data(self, data) -> None:
        self.supply_air_static_pressure_cache.add(data)

    def add_supply_air_static_pressure_setpoint_data(self, data) -> None:
        self.supply_air_static_pressure_setpoint_cache.add(data)

    def add_fan_vfd_data(self, data) -> None:
        self.fan_vfd_cache.add(data)

    def clear_caches(self) -> None:
        self.supply_air_static_pressure_cache.clear()
        self.supply_air_static_pressure_setpoint_cache.clear()
        self.fan_vfd_cache.clear()


class FaultEquationTwo:
    def __init__(self):
        # tuning params
        self.mix_air_temp_sensor_err_thres_pv = None
        self.outside_air_temp_sensor_err_thres_pv = None
        self.return_air_temp_sensor_err_thres_pv = None

        # caches
        self.mix_air_temp_sensor_cache = Cache()
        self.outside_air_temp_sensor_cache = Cache()
        self.return_air_temp_sensor_cache = Cache()

    def run_fault_check(self) -> bool:
        mix_temp_mean = self.mix_air_temp_sensor_cache.mean()
        out_temp_mean = self.outside_air_temp_sensor_cache.mean()
        return_temp_mean = self.return_air_temp_sensor_cache.mean()

        mix_calc = mix_temp_mean + self.mix_air_temp_sensor_err_thres_pv
        return_calc = return_temp_mean - self.return_air_temp_sensor_err_thres_pv
        out_calc = out_temp_mean - self.outside_air_temp_sensor_err_thres_pv
        min_return_out = min(return_calc, out_calc)

        return mix_calc < min_return_out

    def add_mix_air_temp_data(self, data) -> None:
        self.mix_air_temp_sensor_cache.add(data)

    def add_outside_air_temp_data(self, data) -> None:
        self.outside_air_temp_sensor_cache.add(data)

    def add_return_air_temp_data(self, data) -> None:
        self.return_air_temp_sensor_cache.add(data)

    def clear_caches(self) -> None:
        self.mix_air_temp_sensor_cache.clear()
        self.outside_air_temp_sensor_cache.clear()
        self.return_air_temp_sensor_cache.clear()
