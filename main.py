import asyncio
import httpx
from datetime import date, datetime, timedelta


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
    temp_dir: str = "./temp",
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

            with open(f"{temp_dir}/{filename}", "wb") as f:
                f.write(response.content)

            print(f"Successfully downloaded: {filename}")

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")


async def main():
    # Configuration
    API_KEY = "6e22363ada662d5dd2dbab10fe139e79246b4a99"
    MMSI = "538007475"
    FROM_DATE = "2022-01-08"
    TO_DATE = "2025-12-26"

    days = None

    res = validate_dates(FROM_DATE, TO_DATE)
    if isinstance(res, tuple) and res[0] == "正確":
        days = res[1]
        print(f"Correct, total days: {days}")
    else:
        print(f"Error: {res}")
        return

    start_date = parse_date(FROM_DATE)
    end_date = parse_date(TO_DATE)

    if days <= 180:
        await fetch_vessel_track(
            api_key=API_KEY,
            mmsi=MMSI,
            from_date=start_date,
            to_date=end_date,
            temp_dir="./temp",
        )
    else:
        print(f"Interval is {days} days (> 180), splitting requests...")

        current_start = start_date
        while current_start < end_date:

            current_end = current_start + timedelta(days=180)
            if current_end > end_date:
                current_end = end_date

            await fetch_vessel_track(
                api_key=API_KEY,
                mmsi=MMSI,
                from_date=current_start,
                to_date=current_end,
                temp_dir="./temp",
            )

            current_start = current_end + timedelta(days=1)

            # If we haven't reached the end, sleep
            if current_start < end_date:
                print("Sleeping for 60 seconds between chunks...")
                await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
