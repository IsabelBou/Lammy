from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Thread, main_thread

import numpy as np
import pandas as pd

from NightmareScrapper.config import (ATTRIBUTE_TO_COLOR_MAPPING,
                                      NM_JP_JSON_URL, NM_JSON_URL,
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

    def nm_by_resource_id(self, resource_id: str) -> pd.DataFrame:
        data = self.nm_data
        return data[data.resource_name.astype(str).str.contains(resource_id, regex=False, case=False)]

    def nm_lookup(self, search_string: str) -> pd.DataFrame:
        data = self.nm_data
        return data[
            np.logical_or.reduce([
                data[prop].str.contains(search_string, regex=False, case=False)
                for prop in ('name', 'skill_description', 'skill_name')
            ])
        ]

    @staticmethod
    def _get_nm_dataframe():
        def get_jp_nm_data():
            nm_jp_data = pd.read_json(NM_JP_JSON_URL)
            nm_jp_data = nm_jp_data[(nm_jp_data["cardType"] == 3) & (nm_jp_data["evolutionLevel"] > 0)]
            return nm_jp_data

        def get_nm_data():
            nm_data = pd.read_json(NM_JSON_URL)
            nm_data = nm_data[(nm_data["cardType"] == 3) & (nm_data["evolutionLevel"] > 0)]
            return nm_data

        def get_nm_skills_data():
            return pd.read_json(NM_SKILLS_JSON_URL)

        with ThreadPoolExecutor(3) as workers:
            nm_data_future = workers.submit(get_nm_data)
            nm_jp_data_future = workers.submit(get_jp_nm_data)
            nm_skill_future = workers.submit(get_nm_skills_data)
            nm_data = nm_data_future.result()
            nm_skill_data = nm_skill_future.result()
            nm_jp_data = nm_jp_data_future.result()
            nm_data = pd.merge(nm_data, nm_jp_data, on="cardMstId", suffixes=("", "_jp"))
            merged_data = pd.merge(nm_data, nm_skill_data, on="artMstId")
            merged_story_data = pd.merge(nm_data, nm_skill_data, left_on="questArtMstId", right_on="artMstId")
            merged_data = merged_data[["sp", "duration", "name_x", "name_y", "description_x",
                                       "description_y", "cardMstId", "leadTime", "attribute", "shortName", "resourceName_jp"]]
            merged_data["story_skill_name"] = merged_story_data["name_y"]
            merged_data["story_skill_sp"] = merged_story_data["sp"]
            merged_data["story_skill_duration"] = merged_story_data["duration"]
            merged_data["story_skill_lead_time"] = merged_story_data["leadTime"]
            merged_data["story_skill_description"] = merged_story_data["description_y"]
            merged_data["color"] = merged_data["attribute"].map(ATTRIBUTE_TO_COLOR_MAPPING)
            del merged_data["attribute"]
            return merged_data.rename(columns=dict(name_x="name", description_y="skill_description", description_x="description", cardMstId="card_id", resourceName_jp="resource_name", name_y="skill_name", leadTime="lead_time", shortName="_short_name"))
