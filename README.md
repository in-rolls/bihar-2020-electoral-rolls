# Bihar Electoral Rolls (2020)

We scrape the 2020 Bihar Electoral Rolls from http://ele.bihar.gov.in/pdfsearch/. (Publication Date 07.02.2020) In all, there are 72,723 primary rolls from 243 constituencies.

## Scripts

The [script] download 72,723 PDF files and upload to Google Cloud Storage (gs://in-electoral-rolls-2020/bihar)
The file name follows the following format: `FinalRoll_ACNo_<AC NO 1~243>PartNo_<PART NO>.pdf`
