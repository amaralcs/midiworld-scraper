# midiworld-scraper

A simple Python scraper to download midi files from [Midiworld](https://www.midiworld.com/)

## Usage

The scraper was designed to run in windows and downloads the files using PowerShell. If running this on a unix system it should be easy enough to write a function using `wget` instead.

To use the scraper, call it as a python module and pass the name of the genre to download. Additionally, you can specify a start and end index, which control the starting page from which to start download as well as the last page to download. This can be useful if you encouter errors and want to resume from a specific location. By default no limit is imposed and the scraper will download from all pages of the given genre.

Example usage:
```
python src/scraper.py --genre dance  --outpath scraped_files/dance
```

The scraper downloads files at an interval of 2 seconds so as not to bombard the website with requests.