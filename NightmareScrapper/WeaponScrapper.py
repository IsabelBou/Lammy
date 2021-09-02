from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Thread, main_thread

import numpy as np
import pandas as pd

from WeaponScrapper.config import (ATTRIBUTE_TO_COLOR_MAPPING,
                                      JP_JSON_URL, JSON_URL,
                                      SKILLS_JSON_URL,
									  WP_SKILLS_JSON_URL)


class WeaponScrapper:
    def __init__(self, cache_ttl: timedelta = timedelta(hours=12), do_initial_load=False) -> None:
        super().__init__()
        self.cache_ttl = cache_ttl
        self._last_time_got_data = datetime.fromtimestamp(0)
        self._is_currently_fetching_data = False
        self._wp_dataframe = None
        if do_initial_load:
            self.reload_wp_data()

    def reload_wp_data(self):
        if not self._is_currently_fetching_data:
            self._is_currently_fetching_data = True
            self._wp_dataframe = WeaponScrapper._get_wp_dataframe()
            self._last_time_got_data = datetime.now()
            self._is_currently_fetching_data = False

    @property
    def wp_data(self) -> pd.DataFrame:
        if datetime.now() - self._last_time_got_data > self.cache_ttl:
            if self._wp_dataframe is None or self._wp_dataframe.empty:
                self.reload_wp_data()
            else:
                Thread(target=self.reload_wp_data).start()
        return self._wp_dataframe

    def find_wp(self, search_string: str) -> pd.DataFrame:
        data = self.wp_data
        return data[data.name.str.contains(search_string, regex=False, case=False)]

    def wp_by_resource_id(self, resource_id: str) -> pd.DataFrame:
        data = self.wp_data
        return data[data.resource_name.astype(str).str.contains(resource_id, regex=False, case=False)]

    def wp_lookup(self, search_string: str) -> pd.DataFrame:
        data = self.wp_data
        return data[
            np.logical_or.reduce([
                data[prop].str.contains(search_string, regex=False, case=False)
                for prop in ('name', 'skill_description', 'skill_name')
            ])
        ]

    @staticmethod
    def _get_wp_dataframe():
        def get_jp_wp_data():
            wp_jp_data = pd.read_json(JP_JSON_URL)
            wp_jp_data = wp_jp_data[wp_jp_data["cardType"] == 1]
            wp_jp_data = wp_jp_data[wp_jp_data.groupby('cardUniqueId').evolutionLevel.transform(max) == wp_jp_data.evolutionLevel]
            return wp_jp_data

        def get_wp_data():
            wp_data = pd.read_json(JSON_URL)
            wp_data = wp_data[wp_data["cardType"] == 1]
            wp_data = wp_data[wp_data.groupby('cardUniqueId').evolutionLevel.transform(max) == wp_data.evolutionLevel]
            return wp_data
			
        def get_wp_skills_data():
            return pd.read_json(WP_SKILLS_JSON_URL)		

        with ThreadPoolExecutor(3) as workers:
            wp_data_future = workers.submit(get_wp_data)
            wp_jp_data_future = workers.submit(get_jp_wp_data)
            wp_skill_future = workers.submit(get_wp_skills_data)
            wp_data = wp_data_future.result()
            wp_skill_data = wp_skill_future.result()
            wp_jp_data = wp_jp_data_future.result()
            wp_data = pd.merge(wp_data, wp_jp_data, on="cardMstId", suffixes=("", "_jp"))
            merged_data = pd.merge(wp_data, wp_skill_data, on="skillMstId")
            merged_story_data = pd.merge(wp_data, wp_skill_data, left_on="questArtMstId", right_on="artMstId")
            merged_data = merged_data[["name_x", "name_y", "description_x", "description_y", "cardMstId", "attribute", "cardDetailType", "typeLabel" "shortName", "resourceName_jp"]]
            merged_data["story_skill_name"] = merged_story_data["name_y"]
            merged_data["story_skill_description"] = merged_story_data["description_y"]
            merged_data["color"] = merged_data["attribute"].map(ATTRIBUTE_TO_COLOR_MAPPING)
            merged_data["type"] = merged_data["attribute"].map(ATTRIBUTE_TO_TYPE_MAPPING)
            merged_data["weapon_type"] = merged_data["detailtype"].map(DETAILTYPE_TO_WEAPONTYPE_MAPPING)
            del merged_data["attribute"]
            del merged_data["detailtype"]
            return merged_data.rename(columns=dict(name_x="name", cardMstId="card_id", "" cardDetailType="Weapon_type", resourceName_jp="resource_name", name_y="skill_name", shortName="_short_name"))
