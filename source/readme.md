# Online OCR addon #

This addon aims at enhancing the experience of OCR when using NVDA.

Add more accurate online engines to NVDA.
Add "Auto OCR" feature. Whenever navigator object changes, NVDA will automatically run OCR on current navigator object with Windows 10 OCR engine.
Online engines relies on the use and presence of the following services.

https://www.nvdacn.com
https://ocr.space/ocrapi
http://ai.qq.com
http://ai.baidu.com

## Hotkeys

NVDA+Shift+R Recognize current navigator object  with online OCR engine and read results directly
NVDA+ALT+Shift+R Recognize current navigator object with online OCR engine and open a result viewer like Windows 10 OCR
NVDA+Windows+R Recognizes the text in clipboard images with Custom OCR engine and read results directly
NVDA+Alt+Windows+R Recognizes image in clipboard with online OCR engine.Then open a result viewer like Windows 10 OCR

Ctrl+semicolon Toggle "Auto OCR".

## Configuration

You can choose recognition engines and configure them in detail in *Online OCR* categroy in NVDA settings dialog.

API Access Type: How you get access to the corresponding API endpoints.
If you choose Use public quota, you are using free quota in an account registered by addon author.
If you choose US,this addon will use your own api access tokens.
There are four engines avaliable.

### OCR space
This one is paid API with free quota.
Support 24 languages and table recognition.
You can get your own free api key by registering on
https://ocr.space/ocrapi

### Baidu OCR
This one is paid API with free quota.
There are four types of api.
Basic OCR without any information about text location.
Basic OCR with information about text location.
Accurate OCR without any information about text location.
Accurate with information about text location.
### Sougou OCR and Tencent AI OCR
These two API are free to use with QPS(query per second) limit.
There is no information about language support in these api document
According to my test Chinese and English and their mixture is surpported.


