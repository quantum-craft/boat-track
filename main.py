import asyncio
import os
import shutil
from dotenv import load_dotenv
import httpx
from datetime import date, datetime, timedelta
import yaml


def parse_date(d: str | date) -> date:
    """Helper to ensure we have a date object."""
    if isinstance(d, date):
        return d

    try:
        ret_date = datetime.strptime(d, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("不正確的日期格式, 請使用 YYYY-MM-DD 格式")

    return ret_date


def validate_dates(
    start_date: str | date, end_date: str | date
) -> str | tuple[str, int]:
    """
    Checks the interval between start_date and end_date.

    Returns:
        1. "invalid" if start_date > end_date
        2. "today is not end" if end_date is today
        3. ("valid", days) if valid
    """
    s = parse_date(start_date)
    e = parse_date(end_date)
    today = date.today()

    if s > e:
        return "起迄日不合法, 結束日期在起始日期之前"

    if e == today:
        return "不能把今天設為結束日期"

    delta = (e - s).days
    return "正確", delta


async def fetch_vessel_track(
    api_key: str,
    mmsi: str,
    from_date: date,
    to_date: date,
    protocol: str = "csv",
    version: int = 3,
    *,
    output_dir: str,
) -> None:
    """
    Fetches vessel track data from MarineTraffic API and saves it to a file.

    Args:
        api_key: The MarineTraffic API key
        mmsi: Maritime Mobile Service Identity number
        from_date: Start date (YYYY-MM-DD or date object)
        to_date: End date (YYYY-MM-DD or date object)
        protocol: Output format (default: csv)
        version: API version (default: 3)
    """
    base_url = f"https://services.marinetraffic.com/api/exportvesseltrack/{api_key}"

    params = {
        "v": version,
        "fromdate": str(from_date),
        "todate": str(to_date),
        "MMSI": mmsi,
        "protocol": protocol,
    }

    print(f"Fetching data for MMSI: {mmsi}...")
    print(f"Fetching chunk: {from_date} to {to_date}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()

            # Generate filename based on parameters
            filename = f"vessel_track_{mmsi}_{from_date}_{to_date}.{protocol}"

            with open(f"{output_dir}/{filename}", "wb") as f:
                f.write(response.content)

            print(f"Successfully downloaded: {filename}")

            return True

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")

        return False
    except Exception as e:
        print(f"An error occurred: {e}")

        return False


def combine_result_files(mmsi: str, temp_dir: str, results_dir: str) -> None:
    """
    Combines all result files into a single file.
    """

    output_dir = get_output_dir_path(
        mmsi=mmsi,
        temp_dir=temp_dir,
    )

    if not os.path.exists(output_dir):
        print(f"Output directory does not exist: {output_dir}")

        return

    print(f"Combine all chunk files in {output_dir}:")
    final_result_dir = final_result_dir_path(
        mmsi=mmsi,
        results_dir=results_dir,
    )

    if os.path.exists(final_result_dir):
        shutil.rmtree(final_result_dir)

    os.makedirs(final_result_dir, exist_ok=True)

    for filename in os.listdir(output_dir):
        print(filename)


def get_output_dir_path(mmsi: str, temp_dir: str) -> str:
    return f"{temp_dir}/vessel_track_{mmsi}"


def final_result_dir_path(mmsi: str, results_dir: str) -> str:
    return f"{results_dir}/vessel_track_{mmsi}"


async def download_vessel_track_data(
    api_key: str, mmsi: str, start_date: date, end_date: date, temp_dir: str
) -> None:
    """
    Validates dates and downloads vessel track data, splitting into chunks if necessary.
    """

    res = validate_dates(start_date, end_date)
    if not (isinstance(res, tuple) and res[0] == "正確"):
        print(f"Error: {res}")
        return

    days = res[1]

    print(f"Correct, total days: {days}")

    output_dir = get_output_dir_path(
        mmsi=mmsi,
        temp_dir=temp_dir,
    )

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    if days <= 180:
        res = await fetch_vessel_track(
            api_key=api_key,
            mmsi=mmsi,
            from_date=start_date,
            to_date=end_date,
            output_dir=output_dir,
        )

        if not res:
            print("Failed to download vessel track data")
            return

    else:
        print(f"Interval is {days} days (> 180), splitting requests...")

        current_start = start_date
        while current_start < end_date:
            current_end = current_start + timedelta(days=180)
            if current_end > end_date:
                current_end = end_date

            res = await fetch_vessel_track(
                api_key=api_key,
                mmsi=mmsi,
                from_date=current_start,
                to_date=current_end,
                output_dir=output_dir,
            )

            if not res:
                print("Failed to download vessel track data")
                return

            current_start = current_end + timedelta(days=1)

            # If we haven't reached the end, sleep
            if current_start < end_date:
                print("Sleeping for 60 seconds between chunks...")
                await asyncio.sleep(60)


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

    await download_vessel_track_data(
        api_key=API_KEY,
        mmsi=MMSI,
        start_date=start_date,
        end_date=end_date,
        temp_dir=TEMP_DIR,
    )

    combine_result_files(
        mmsi=MMSI,
        temp_dir=TEMP_DIR,
        results_dir=RESULTS_DIR,
    )


if __name__ == "__main__":
    asyncio.run(main())
