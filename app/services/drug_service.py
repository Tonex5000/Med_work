import asyncio
import logging
from collections.abc import Sequence

import httpx

from app.core.config import Settings
from app.core.exceptions import RxNavServiceException

logger = logging.getLogger(__name__)


class DrugClassifierService:
    def __init__(self, client: httpx.AsyncClient, settings: Settings):
        self.client = client
        self.settings = settings
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_rxnav_calls)

    async def classify_drugs(self, drugs: Sequence[str]) -> list[str]:
        tasks = [self._classify_single_drug(drug) for drug in drugs]
        return await asyncio.gather(*tasks)

    async def _classify_single_drug(self, drug_name: str) -> str:
        if not drug_name or not str(drug_name).strip():
            return "Unknown/Unclassified"

        async with self.semaphore:
            normalized_name = str(drug_name).strip()
            try:
                rxcui = await self._get_rxcui(normalized_name)
                if not rxcui:
                    return "Unknown/Unclassified"

                therapeutic_class = await self._get_therapeutic_class(rxcui)
                return therapeutic_class or "Unknown/Unclassified"
            except (httpx.HTTPError, RxNavServiceException) as exc:
                logger.warning(
                    "drug_classification_failed",
                    extra={"drug": normalized_name, "error": str(exc)},
                )
                return "Unknown/Unclassified"

    async def _get_rxcui(self, drug_name: str) -> str | None:
        url = f"{self.settings.rxnav_base_url}/rxcui.json"
        response = await self.client.get(url, params={"name": drug_name})
        response.raise_for_status()
        data = response.json()

        id_group = data.get("idGroup") or {}
        rxnorm_ids = id_group.get("rxnormId") or []
        if not rxnorm_ids:
            return None

        return rxnorm_ids[0]

    async def _get_therapeutic_class(self, rxcui: str) -> str | None:
        url = f"{self.settings.rxnav_base_url}/rxclass/class/byRxcui.json"
        response = await self.client.get(url, params={"rxcui": rxcui, "relaSource": "MEDRT"})
        response.raise_for_status()
        data = response.json()

        rxclass_drug_info_list = data.get("rxclassDrugInfoList") or {}
        rxclass_drug_info = rxclass_drug_info_list.get("rxclassDrugInfo") or []

        if not rxclass_drug_info:
            return None

        min_concept_item = rxclass_drug_info[0].get("rxclassMinConceptItem") or {}
        class_name = min_concept_item.get("className")

        return str(class_name).strip() if class_name else None
