# Online OCR addon #

Author: Larry Wang
NVDA compatibility: from 2018.3 to 2019.1
Download [development version 0.2](https://github.com/larry801/online_ocr/releases/download/0.2/onlineOCR-0.2-dev.nvda-addon)  

This addon aims at enhancing the experience of OCR when using NVDA.
There are two main features.

Add "Auto OCR" feature.
Add more accurate online engines to NVDA.

## Auto OCR

Whenever you use object navigation commands to change current navigator object, NVDA will automatically run OCR on current navigator object with Windows 10 OCR engine.

You can use CTRL semicolon Enable or disable "Auto OCR".

## Online OCR

The author of addon have registered account with free API quota and set up a proxy server on www.nvdacn.com to make this addon easier to test at frist. Test quota is limited and may be cancelled by API provider anytime.
It is highly recommended to register your own key according to guide in each engine.

Online engines rely on the use and presence of the following services.

https://www.nvdacn.com

https://ocr.space/ocrapi

https://azure.microsoft.com/en-us/services/cognitive-services/
http://ai.qq.com

http://ai.baidu.com

http://ai.sogou.com/

The author of addon have registered account with free API quota and put them on www.nvdacn.com to make this addon easier to use at first. Test quota is limited. Registering your own key is highly recommended for service availability and privacy concern.

### Keyboard commands

NVDA+Shift+R Recognize current navigator object with online OCR engine and read results directly

NVDA+ALT+Shift+R Recognize current navigator object with online OCR engine and open a result viewer like Windows 10 OCR

NVDA+Windows+R Recognizes the text in clipboard images with Custom OCR engine and read results directly

NVDA+Alt+Windows+R Recognizes image in clipboard with online OCR engine. Then open a result viewer like Windows 10 OCR

### Engine Configuration

You can choose recognition engines and configure them in detail in *Online OCR* category in NVDA settings dialog.

The following settings are applicable to all engines.

API Access Type:
This controls how you get access to the corresponding API endpoints.

If you choose "Use public quota", you are using free quota in an account registered by addon author.
If you choose "Use your own API key", this addon will use quota from your own account.


APP ID, API key or API Secret Key:
If you want to use quota from your own account corresponding access tokens is required. Some engines only need API key.
Some engines require two tokens.
These are only valid if you choose "use your own API key" in API Access type.

There are five engines available.

### OCR space
This one is a paid API with free quota provided by https://ocr.space
It supports 24 languages including
Arabic 
Bulgarian 
Chinese(Simplified) 
Chinese(Traditional) 
Croatian 
Czech 
Danish 
Dutch 
English 
Finnish 
French 
German 
Greek 
Hungarian 
Korean 
Italian 
Japanese 
Polish 
Portuguese 
Russian 
Slovenian 
Spanish  
Swedish  
Turkish  

Here are settings for this engine:

Language: Text language for recognition. English by default.

Detect image orientation:
If set to true, the API autorotates the image correctly.

Scale image for better quality
If set to true, the API does some internal upscaling. This can improve the OCR result significantly, especially for low-resolution PDF scans.

Optimize for table recognition 
If set to true, the OCR logic makes sure that the parsed text result is always returned line by line. This switch is recommended for table OCR, receipt OCR, invoice processing and all other type of input documents that have a table like structure.

If you want to use your own key, you also need to specify API Key.

You can get your own free API key by registering on
https://ocr.space/ocrapi
Here is a simple guide.
Find the link "Register for free API key"
Click on it and you will find a form to fill in.
The form asks you to enter the following data
Email Address 
First Name
Last Name
How do you plan to use the OCR API?
After filling it and submit. You may also need to pass  a captcha
Then you will receive a confirmation e-mail
Find the link named "Yes, subscribe me to this list." in that e-mail. Access that link and you will receive API key by e-mail soon.

### Microsoft Azure OCR
This engine uses OCR API in Microsoft Azure Cognitive Services Computer Vision.

It supports 24 languages including
(Chinese Simplified)
(Chinese Traditional)
(Czech)
(Danish)
(Dutch)
(English)
(Finnish)
(French)
(German)
(Greek)
(Hungarian)
(Italian)
(Japanese)
(Korean)
(Norwegian)
(Polish)
(Portuguese,
(Russian)
(Spanish)
(Swedish)
(Turkish)
(Arabic)
(Romanian)
(Serbian Cyrillic)
(Serbian Latin)
(Slovak)

Here are settings for this engine:

Language: Text language for recognition. Auto detection by default.

Detect image orientation:
If set to true, the API autorotates the image correctly.

If you use your own key, you also need to specify these settings.
Azure resource Region: 
The region you choose when deploying Cognitive Services in Azure Portal.
API key:
The key you get after successfully deploying Cognitive Services in Azure Portal, KEY 2 is recommended.



### Baidu OCR
This one is also a paid API with free quota provided by Baidu.
Baidu OCR supports 10 languages including
Chinese and English mixture
English
Portuguese
French
German
Italian
Spanish
Russian
Japanese
Korean
This engine can also get position of every character

Here are its settings:



Get position of every character allows you to do more precise operation on some inaccessible application. Enabling this will make recognition slightly slower.

Use Accurate API 
If is enabled will use a different endpoint.
That accurate endpoint takes longer time but has higher quality and (If you use your own API key its price is also higher).

It has four endpoints with separate quota limit.

Basic OCR without any information about text location.
Currently 50000 times a day.
Basic OCR with information about text location.
Currently 500 times a day.
Accurate OCR without any information about text location.
Currently 500 times a day.
Accurate with information about text location.
Currently 50 times a day.

If you press NVDA+Shift+R or NVDA+Windows+R, you are using endpoints without any information about text location. 
If you press NVDA+Shift+Alt+R or NVDA+Windows+Alt+R, you are using endpoints with information about text location. 

Though it provides a quite generous free quota, its website is Chinese only and not quite accessible.

### Sougou OCR and Tencent AI OCR
These two API are free to use with frequency limit.
If you want to bypass the limit you can register your own API key. The website of these two APIs are also Chinese only and not quite accessible.
There is no information about language support in these API document
According to my test Chinese and English and their mixture is supported.
There is no additional configuration for these API.


