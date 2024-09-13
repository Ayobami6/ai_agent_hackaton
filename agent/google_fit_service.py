from dataclasses import dataclass
from typing import List
import requests


@dataclass
class GoogleFitService:
    headers: dict
    _height_weight: List[str] = [
        "raw:com.google.height:com.google.android.apps.fitness:user_input",
        "raw:com.google.weight:com.google.android.apps.fitness:user_input",
    ]
    _blood_pressure_resource: List[str] = [
        "raw:com.google.blood_pressure:com.google.android.apps.fitness:user_input"
    ]
    _cumulative_steps_count_resource: List[str] = [
        "derived:com.google.step_count.cumulative:com.google.android.gms:HXY:A9 Pro:9cc6da4c:soft_step_counter"
    ]
    _sleep_resource: List[str] = [
        "derived:com.google.sleep.segment:com.google.android.gms:merged"
    ]
    _body_fat: List[str] = [
        "derived:com.google.body.fat.percentage:com.google.android.gms:merged"
    ]
    _instance = None

    BASE_URL = "https://fitness.googleapis.com/fitness/v1/users/me/dataSources/{}/dataPointChanges"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_weight_height_val(self) -> dict:
        weight_height_map = {}
        for url in self._height_weight:
            resource_url = self.BASE_URL.format(url)
            response = requests.get(resource_url, headers=self.headers)
            data = response.json()
            print(data)
            val = data["insertedDataPoint"][-1]["value"][0]["fpVal"]
            weight_height_map[data["insertedDataPoint"][0]["dataTypeName"][11:]] = val
        return weight_height_map
