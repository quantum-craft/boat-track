import os
from dotenv import load_dotenv
import yaml
import asyncio
from date_utils import parse_date
from download_api import download_vessel_track_data
from file_utils import combine_result_files


async def main():
    load_dotenv()

    # Load configuration from YAML
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yaml not found.")
        return

    # Configuration
    API_KEY = os.getenv("MARINE_TRAFFIC_API_KEY")
    MMSI = config.get("mmsi")
    FROM_DATE = config.get("from_date")
    TO_DATE = config.get("to_date")
    TEMP_DIR = config.get("temp_dir")
    RESULTS_DIR = config.get("results_dir")

    if not all([API_KEY, MMSI, FROM_DATE, TO_DATE]):
        print(
            "Error: Missing required configuration (API_KEY, MMSI, FROM_DATE, or TO_DATE)."
        )
        return

    start_date = parse_date(FROM_DATE)
    end_date = parse_date(TO_DATE)

    res = await download_vessel_track_data(
        api_key=API_KEY,
        mmsi=MMSI,
        start_date=start_date,
        end_date=end_date,
        temp_dir=TEMP_DIR,
    )

    if not res:
        return

    combine_result_files(
        mmsi=MMSI,
        temp_dir=TEMP_DIR,
        results_dir=RESULTS_DIR,
    )


if __name__ == "__main__":
    asyncio.run(main())
