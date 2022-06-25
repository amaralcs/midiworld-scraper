"""
    A scraper to download midi files from https://www.midiworld.com/
"""
import time
from bs4 import BeautifulSoup
import sys
import argparse
import requests
import os
import subprocess
from glob import glob
import re
import logging

logger = logging.getLogger("utils_logger")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_genre_page(genre, base_path="https://www.midiworld.com/"):
    return base_path + "search/{}/" + f"?q={genre}"


def download(url, outfile):
    """Download a file using powershell

    Parameters
    ----------
    url : str
        The URL to download.
    outfile : str
        The name of the file to save.

    Returns
    -------
    None
    """
    cmd = f"Invoke-WebRequest -OutFile '{outfile}' -Uri {url}"
    r = subprocess.Popen(f"powershell.exe {cmd}")
    if r.returncode:
        logger.warning("\t\t there was an error downloading this file")


def download_files(file_list, outpath):
    """Iterates through all items in the file list and get the URL to download

    Parameters
    ----------
    file_list : BeautifulSoup.soup
        Soup object.
    outpath : str
        Path to output files.

    Returns
    -------
    None
    """
    cur_files = [os.path.split(fname)[1] for fname in glob(outpath + "/*.mid")]

    for item in file_list.find_all("li"):
        # Get the name of the file and clean it
        name = item.text.split(" - ")[0].strip().replace(" ", "_").lower()
        name = re.sub(r"[!-/:-@[-`{-~.,]", "_", name)
        name = re.sub(r"_{2,}", "_", name) + ".mid"

        url = item.find("a").get("href")
        if name in cur_files:
            logger.info(f"\tskipping {name}")
        else:
            logger.info(f"\tdownloading {name}")
            outfile = os.path.join(outpath, name)
            download(url, outfile)
            time.sleep(2)


def find_next_page(page_url):
    """Gets the next page of results

    Parameters
    ----------
    page_url : str
        The current page url.

    Returns
    -------

    """
    html = requests.get(page_url).text
    page = BeautifulSoup(html, "html.parser")
    page_results = page.find("h3").next_sibling.next_sibling.text.strip()

    if page_results == "found nothing!":
        logger.info("No more results to process.")
        return None
    else:
        return page


def read_cmd(argv):
    """Parses input options for this module.

    Parameters
    ----------
    argv : List
        List of input parameters to this module

    Returns
    -------
    Argparser
    """
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--start-idx", default=1, type=int)
    parser.add_argument("--end-idx", default=-1, type=int)
    parser.add_argument(
        "--genre",
        default="hip-hop",
        choices=[
            "classic",
            "pop",
            "rock",
            "rap",
            "dance",
            "punk",
            "blues",
            "country",
            "movie_themes",
            "tv_themes",
            "christmas_carols",
            "video_game_themes",
            "jazz",
            "hip-hop",
        ],
    )
    parser.add_argument("--outpath", default="../data/midi-world")
    return parser.parse_args()


def main(argv):
    """The main function to run the job."""
    args = read_cmd(argv)
    page_idx = args.start_idx
    end_idx = args.end_idx
    genre = args.genre
    outpath = os.path.join(args.outpath, genre)
    os.makedirs(outpath, exist_ok=True)

    # Debug arguments
    # genre = "hip-hop"
    # outpath = f"data/midi-world/{genre}"

    while page_idx != end_idx:
        logger.info(f"Getting files from page {page_idx}")
        page_url = get_genre_page(genre).format(page_idx)
        page = find_next_page(page_url)
        if page is None:
            break

        file_list = page.find_all("ul")[1]
        download_files(file_list, outpath)
        page_idx += 1
    logger.info("Complete.")


if __name__ == "__main__":
    main(sys.argv[1:])
