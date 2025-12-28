import os
import csv
import shutil


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

    combined_file_path = f"{final_result_dir}/vessel_track_{mmsi}_combined.csv"

    csv_files = [f for f in os.listdir(output_dir) if f.endswith(".csv")]
    csv_files.sort()  # Sort to maintain chronological order

    header_saved = False
    with open(combined_file_path, "w", newline="", encoding="utf-8") as outfile:
        writer = None
        for filename in csv_files:
            file_path = os.path.join(output_dir, filename)
            print(f"Processing chunk: {filename}")

            with open(file_path, "r", newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                try:
                    header = next(reader)
                    if not header_saved:
                        writer = csv.writer(outfile)
                        writer.writerow(header)
                        header_saved = True

                    for row in reader:
                        writer.writerow(row)
                except StopIteration:
                    print(f"Warning: {filename} is empty.")
                    continue

    print(f"Successfully combined all files into: {combined_file_path}")


def get_output_dir_path(mmsi: str, temp_dir: str) -> str:
    return f"{temp_dir}/vessel_track_{mmsi}"


def final_result_dir_path(mmsi: str, results_dir: str) -> str:
    return f"{results_dir}/vessel_track_{mmsi}"
