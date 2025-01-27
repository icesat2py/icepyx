from concurrent.futures import as_completed
import datetime as dt
import json
from pathlib import Path
import pprint
import time
from typing import Any, TypedDict, Union

import harmony
import requests

from icepyx.core.auth import EarthdataAuthMixin

# Sometimes harmony has problems (e.g., 500 bad gateway) and we need to retry.
# 5 seconds seems like enough, but not always.
REQUEST_RETRY_INTERVAL_SECONDS: int = 5


class HarmonyTemporal(TypedDict):
    # TODO: these are optional. Harmony can take a start without a stop or a
    # stop without a start.
    start: dt.datetime
    stop: dt.datetime


class HarmonyApi(EarthdataAuthMixin):
    def __init__(self):
        # initialize authentication properties
        EarthdataAuthMixin.__init__(self)
        self.harmony_client = harmony.Client(
            auth=(
                self.auth.username,
                self.auth.password,
            ),
        )

        # List of job IDs that have been placed with the HarmonyApi
        self.job_ids = []

    def get_capabilities(self, concept_id: str) -> dict[str, Any]:
        capabilities_request = harmony.CapabilitiesRequest(collection_id=concept_id)
        response = self.harmony_client.submit(capabilities_request)

        return response

    def _place_order(
        self,
        concept_id: str,
        # These are optional subset parameters
        spatial: Union[harmony.BBox, None] = None,
        temporal: Union[HarmonyTemporal, None] = None,
        shape: Union[str, None] = None,
    ) -> str:
        """Places a Harmony order with the given parameters.

        Return a string representing a job ID.
        """
        collection = harmony.Collection(id=concept_id)
        request = harmony.Request(
            collection=collection,
            # TODO: these two kwargs are type-ignored because `harmony-py` is
            # typed to not allow `None`. However, `harmony-py` initializes
            # values with `None`, so it should be allowed to pass that along.
            spatial=spatial,  # type: ignore[arg-type]
            temporal=temporal,  # type: ignore[arg-type]
            shape=shape,  # type: ignore[arg-type]
        )

        if not request.is_valid():
            raise RuntimeError(
                "Failed to create valid harmony request:" f" {request.error_messages()}"
            )

        job_id = self.harmony_client.submit(request)

        return job_id

    def check_order_status(self, job_id: str) -> dict[str, Any]:
        retries = 3

        for retry_num in range(1, retries + 1):
            try:
                status = self.harmony_client.status(job_id)
                return status
            except requests.HTTPError as e:
                if retry_num >= retries:
                    raise e

                print(
                    f"Encountered HTTPError {e} while requesting job status"
                    f" for {job_id}. Retrying...{retry_num}/{retries}"
                )
                time.sleep(REQUEST_RETRY_INTERVAL_SECONDS)

        raise RuntimeError(f"Failed to get harmony order status for {job_id}")

    def place_order(
        self,
        concept_id: str,
        # These are optional subset parameters
        spatial: Union[harmony.BBox, None] = None,
        temporal: Union[HarmonyTemporal, None] = None,
        shape: Union[str, None] = None,
    ) -> str:
        """Places a Harmony order with the given parameters and waits for it to complete.

        Return a string representing a job ID once the order is complete.
        """
        job_id = self._place_order(
            concept_id=concept_id,
            spatial=spatial,
            temporal=temporal,
            shape=shape,
        )

        # Append this job to the list of job ids.
        self.job_ids.append(job_id)

        order_fn = ".order_restart"
        with open(order_fn, "w") as fid:
            # Note: icepyx v1 used "orderIds". Harmony uses the term "job" to describe
            # an order, so that gets used here.
            json.dump({"jobIds": self.job_ids}, fid)

        print("Harmony job ID: ", job_id)
        status = self.check_order_status(job_id)
        print(f"Initial status of your harmony order request: {status['status']}")
        # The list of possible statues are here:
        # https://github.com/nasa/harmony/blob/8b2eb47feab5283d237f3679ac8e09f50e85038f/db/db.sql#L8
        while status["status"].startswith("running") or status["status"] == "accepted":
            print(
                (
                    "Your harmony job status is still "
                    f"{status['status']}. Please continue waiting... this may take a few moments."
                )
            )
            # Requesting the status too often can result in a 500 error.
            time.sleep(REQUEST_RETRY_INTERVAL_SECONDS)
            status = self.check_order_status(job_id)

        print("Your harmony order is: ", status["status"])
        print("Harmony returned this message:")
        pprint.pprint(status["message"])
        if status["status"] == "complete_with_errors" or status["status"] == "failed":
            print("Harmony provided these error messages:")
            pprint.pprint(status["errors"])

        return job_id

    def _download_job_results(
        self,
        job_id: str,
        download_dir: Path,
        overwrite: bool,
    ) -> list[Path]:
        print(f"Downloading results for harmony job {job_id}")

        futures = self.harmony_client.download_all(
            job_id, str(download_dir), overwrite=overwrite
        )

        paths = []
        for future in as_completed(futures):
            paths.append(Path(future.result()))

        return paths

    def download_granules(
        self, download_dir: Path, overwrite: bool = False
    ) -> list[Path]:
        all_paths = []
        for job_id in self.job_ids:
            paths = self._download_job_results(
                job_id=job_id, download_dir=download_dir, overwrite=overwrite
            )
            all_paths.extend(paths)

        return all_paths
