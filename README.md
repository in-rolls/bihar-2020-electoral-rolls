## Bihar Electoral Rolls (2020)

We scraped the 2020 Bihar Electoral Rolls from http://ele.bihar.gov.in/pdfsearch/. (Publication Date 07.02.2020) In all, there are 72,723 primary rolls from 243 constituencies.

### Script

We used the [script](bihar.py) to download 72,723 PDF files and upload to Google Cloud Storage (gs://in-electoral-rolls-2020/bihar). The file name follows the following format: `FinalRoll_ACNo_<AC NO 1~243>PartNo_<PART NO>.pdf`

### Log Files

* [list.txt](list.txt)
* [list2.txt](list2.txt) --- files that weren't downloaded the first time.

## Checking That we Downloaded Everything

Notebook to check [here](https://github.com/in-rolls/bihar-2020-electoral-rolls/blob/master/bihar_check.ipynb)

### How Do I Get the Electoral Rolls?

We have instituted the same process as [here](https://github.com/in-rolls/electoral_rolls).

Given privacy concerns, we are releasing the data only for research purposes. To access the pdfs, you must agree to take all precautions to maintain the privacy of Indian electors. (There is a difference between data being available in pdfs, split across different sites, sometimes behind CAPTCHA, and a common data dump.) You will get read access to Google Coldline storage bucket for a month. The buckets are setup as requester pays. So you need to create a project that will be used for billing. You can access them as follows:

```
gsutil -u projectname_for_billing ls gs://in-electoral-rolls-2020/bihar
```
