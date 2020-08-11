## Bihar Electoral Rolls (2020)

We scraped the 2020 Bihar Electoral Rolls from http://ele.bihar.gov.in/pdfsearch/ (Publication Date: 07-02-2020). In all, there were 72,723 primary rolls from 243 constituencies.

The file name has the following format: `FinalRoll_ACNo_<AC NO 1~243>PartNo_<PART NO>.pdf`

### Scripts

1. We used the [script](scripts/bihar.py) to download the files and upload them to Google Cloud Storage (gs://in-electoral-rolls-2020/bihar).
  - There were a few files which we couldn't download in the first try. The script for downloading those is [here](scripts/bihar_patch.py).
2. [Notebook](scripts/bihar_check.ipynb) to check if we downloaded all the files
3. [Notebook](scripts/bihar_to_csv.ipynb) to check file size and produce [metadata CSV for files](metadata_and_log_files/bihar.csv)
4. [Notebook](scripts/scrape-dry-run-getmeta.ipynb) gets the [metadata from the webpage (including names etc.)](metadata_and_log_files/metadata.csv) and appends to [the csv obtained step 3](metadata_and_log_files/bihar.csv)

### Log Files and Metadata CSV

* [list.txt](metadata_and_log_files/list.txt) --- files that downloaded the first time.
* [list2.txt](metadata_and_log_files/list2.txt) --- all files that downloaded after the 2nd time.
* [list3.txt](metadata_and_log_files/list3.txt) --- all files with file size.
* [Metadata CSV for Files along with size](metadata_and_log_files/bihar.csv)
* [Metadata CSV with data from the webpage](metadata_and_log_files/metadata.csv)

### How Do I Get the Electoral Rolls?

We have instituted the same process as [here](https://github.com/in-rolls/electoral_rolls).

Given privacy concerns, we are releasing the data only for research purposes. To access the pdfs, you must agree to take all precautions to maintain the privacy of Indian electors. (There is a difference between data being available in pdfs, split across different sites, sometimes behind CAPTCHA, and a common data dump.) You will get read access to Google Coldline storage bucket for a month. The buckets are setup as requester pays. So you need to create a project that will be used for billing. You can access them as follows:

```
gsutil -u projectname_for_billing ls gs://in-electoral-rolls-2020/bihar
```
