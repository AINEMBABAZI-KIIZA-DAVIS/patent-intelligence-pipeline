import requests
import os

files_to_download = {
    "g_patent.tsv.zip": "https://s3.amazonaws.com/data.patentsview.org/download/g_patent.tsv.zip",
    "g_inventor_disambiguated.tsv.zip": "https://s3.amazonaws.com/data.patentsview.org/download/g_inventor_disambiguated.tsv.zip",
    "g_assignee_disambiguated.tsv.zip": "https://s3.amazonaws.com/data.patentsview.org/download/g_assignee_disambiguated.tsv.zip",
    "g_location_disambiguated.tsv.zip": "https://s3.amazonaws.com/data.patentsview.org/download/g_location_disambiguated.tsv.zip",
    "g_patent_abstract.tsv.zip": "https://s3.amazonaws.com/data.patentsview.org/download/g_patent_abstract.tsv.zip"
}

def download_file(url, local_filename):
    print(f"Downloading {local_filename} from {url}...")
    # Stream the download so it doesn't take up all memory
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        # Since these files are gigabytes long, for coursework testing,
        # we can just download the first 20MB of the zip to prove we use original data.
        # However, a partial ZIP might be unreadable by pandas. 
        # So we download the whole thing. Note: This may take a while!
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    print(f"Finished downloading {local_filename}")

if __name__ == "__main__":
    for filename, url in files_to_download.items():
        if not os.path.exists(filename) and not os.path.exists(filename.replace('.zip', '')):
            download_file(url, filename)
        else:
            print(f"File {filename} automatically found.")
    print("\nAll original data files present. You can now run main.py")
