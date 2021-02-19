from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Thread, main_thread

import numpy as np
import pandas as pd

from NightmareScrapper.config import (ATTRIBUTE_TO_COLOR_MAPPING, NM_JSON_URL,
                                      NM_SKILLS_JSON_URL)


class NightmareScrapper:
    def __init__(self, cache_ttl: timedelta = timedelta(hours=12), do_initial_load=False) -> None:
        super().__init__()
        self.cache_ttl = cache_ttl
        self._last_time_got_data = datetime.fromtimestamp(0)
        self._is_currently_fetching_data = False
        self._nm_dataframe = None
        if do_initial_load:
            self.reload_nm_data()

    def reload_nm_data(self):
        if not self._is_currently_fetching_data:
            self._is_currently_fetching_data = True
            self._nm_dataframe = NightmareScrapper._get_nm_dataframe()
            self._last_time_got_data = datetime.now()
            self._is_currently_fetching_data = False

    @property
    def nm_data(self) -> pd.DataFrame:
        if datetime.now() - self._last_time_got_data > self.cache_ttl:
            if self._nm_dataframe is None or self._nm_dataframe.empty:
                self.reload_nm_data()
            else:
                Thread(target=self.reload_nm_data).start()

        return self._nm_dataframe

    def find_nm(self, search_string: str) -> pd.DataFrame:
        data = self.nm_data
        return data[data.name.str.contains(search_string, regex=False, case=False)]

    def nm_lookup(self, search_string: str) -> pd.DataFrame:
        data = self.nm_data
        return data[
            np.logical_or.reduce([
                data[prop].str.contains(search_string, regex=False, case=False)
                for prop in ('name', 'description', 'skill_name')
            ])
        ]

    @staticmethod
    def _get_nm_dataframe():
        def get_nm_data():
            nm_data = pd.read_json(NM_JSON_URL)
            nm_data = nm_data[(nm_data["cardType"] == 3) & (nm_data["evolutionLevel"] > 0)]
            return nm_data

        def get_nm_skills_data():
            return pd.read_json(NM_SKILLS_JSON_URL)

        with ThreadPoolExecutor(2) as workers:
            nm_data_future = workers.submit(get_nm_data)
            nm_skill_future = workers.submit(get_nm_skills_data)
            nm_Data = nm_data_future.result()
            nm_skill_data = nm_skill_future.result()
            merged_data = pd.merge(nm_Data, nm_skill_data, on="artMstId")
            merged_data = merged_data[["sp", "duration", "name_x", "name_y", "description_y", "cardMstId", "leadTime", "attribute", "shortName"]]
            merged_data["color"] = merged_data["attribute"].map(ATTRIBUTE_TO_COLOR_MAPPING)
            del merged_data["attribute"]
            return merged_data.rename(columns=dict(name_x="name", description_y="description", cardMstId="card_id", name_y="skill_name", duration="lead_time", leadTime="duration", shortName="short_name"))
