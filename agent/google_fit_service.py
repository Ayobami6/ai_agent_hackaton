from typing import List, Tuple
import requests
from .exceptions import ServiceException


class GoogleFitService:
    def __init__(self, headers: dict) -> None:
        self.headers = headers

    _height_weight: List[str] = [
        "raw:com.google.height:com.google.android.apps.fitness:user_input",
        "raw:com.google.weight:com.google.android.apps.fitness:user_input",
    ]
    _blood_pressure_resource: List[str] = [
        "raw:com.google.blood_pressure:com.google.android.apps.fitness:user_input"
    ]
    _cumulative_steps_count_resource: List[str] = [
        "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    ]
    _sleep_resource: List[str] = [
        "derived:com.google.sleep.segment:com.google.android.gms:merged"
    ]
    _body_fat: List[str] = [
        "derived:com.google.body.fat.percentage:com.google.android.gms:merged"
    ]

    _all: List[str] = (
        _height_weight
        + _blood_pressure_resource
        + _body_fat
    )

    BASE_URL = "https://fitness.googleapis.com/fitness/v1/users/me/dataSources/{}/dataPointChanges"

    def get_weight_height_val(self) -> dict:
        weight_height_map = {}
        for url in self._height_weight:
            resource_url = self.BASE_URL.format(url)
            response = requests.get(resource_url, headers=self.headers)
            data = response.json()
            if data["insertedDataPoint"] == []:
                raise ServiceException(
                    "No data found for weight and height",
                    status_code=404,
                )
            val = data["insertedDataPoint"][-1]["value"][0]["fpVal"]
            weight_height_map[data["insertedDataPoint"]
                              [0]["dataTypeName"][11:]] = val
        return weight_height_map

    def get_body_fat_val(self) -> float:
        resource_url = self.BASE_URL.format(self._body_fat[0])
        response = requests.get(resource_url, headers=self.headers)
        data = response.json()
        if data["insertedDataPoint"] == []:
            raise ServiceException(
                "No data found for body fat",
                status_code=404,
            )
        val = data["insertedDataPoint"][-1]["value"][0]["fpVal"]
        return val

    def get_bp_data(self) -> Tuple[str]:
        resource_url = self.BASE_URL.format(self._blood_pressure_resource[0])
        response = requests.get(resource_url, headers=self.headers)
        data = response.json()
        if data["insertedDataPoint"] == []:
            raise ServiceException(
                "No data found for blood pressure",
                status_code=404,
            )
        numerator = data["insertedDataPoint"][0]["value"][0]["fpVal"]
        denom = data["insertedDataPoint"][-1]["value"][1]["fpVal"]
        bp = f"{numerator}/{denom}"
        return bp, numerator, denom

    def get_data(self) -> str:
        fit_data = {}
        for resource in self._all:
            resource_url = self.BASE_URL.format(resource)
            response = requests.get(resource_url, headers=self.headers)
            data = response.json()
            if data["insertedDataPoint"] == []:
                raise ServiceException(
                    f"No data found for {resource}",
                    status_code=404,
                )
            val = data["insertedDataPoint"][-1]["value"][0]["fpVal"]
            if data["insertedDataPoint"][0]["dataTypeName"][11:] == "blood_pressure":
                fit_data["blood_pressure"] = f"{
                    val}/{data["insertedDataPoint"][-1]["value"][1]["fpVal"]}"
            else:
                fit_data[data["insertedDataPoint"]
                         [0]["dataTypeName"][11:]] = val
