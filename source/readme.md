# Online OCR addon #

Author: Larry Wang
NVDA compatibility: from 2018.3 to 2019.1
Download [development version](https://github.com/larry801/online_ocr/download/0.9-dev/onlineOCR-0.9-dev.nvda-addon)

This addon aims at adding more accurate online engines to NVDA.

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

Control+Shift+NVDA+R Recognize current navigator object with online OCR engine Then read result.If pressed twice, open a virtual result document.

NVDA+Alt+R Recognizes image in clipboard with online OCR engine. Then read result.If pressed twice, open a virtual result document.
It accepts two kinds of content.
First is an actual image(CF_DIB), you can put that into clipboard by taking a screenshot with PrintScreen key or copy image in a browser.

Second is a file copied in  explorer.(CF_HDROP)
If it is not an image or there is only text in clipboard.This addon will tell you, No image in clipboard.

Third is a path or url of an image. This addon will try to open or download that image file 
If none of above 
### Engine Configuration

You can choose recognition engines and configure them in detail in *Online OCR* category in NVDA settings dialog.

The following settings are applicable to all engines.

Copy result to clipboard after recognition:
If enabled, recognition result will be copied to clipboard after recognition.

Swap the effect of repeated gesture with none repeated ones:
By default a virtual result document is shown only if you press the corresponding gesture twice, if you use that frequently you can enable this option so that you only need to press once to get a result viewer.

Enable more verbose logging for debug purpose:

Some logs are essential for debugging but affects performace and takes up a lot of space. Only turn this on if specifically instructed to by the addon author or an NVDA developer.

Proxy type:
Which type of proxy you are using. If you do not know what is a proxy just leave it as is.

Proxy address:
Full url of your proxy. If you do not know what is a proxy just leave it as is.
If you choose to use proxy your porxy will be verified before saving , after verification, there will be a prompt to tell you result.
The following settings means the same in all engines, describle them here to save space.

API Access Type:
This controls how you get access to the corresponding API endpoints.

If you choose "Use public quota", you are using free quota in an account registered by addon author.
If you choose "Use your own API key", this addon will use quota from your own account.


APP ID, API key or API Secret Key:
If you want to use quota from your own account corresponding access tokens is required. Some engines only need API key.
Some engines require two tokens.
These are only valid if you choose "use your own API key" in API Access type.

## Engines

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
[OCR space](https://ocr.space/ocrapi)
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

If you use your own key, you should get a subscription key for using Microsoft Computer Vision API from the link below:
Step 1: Create an account.

https://azure.microsoft.com/en-ua/try/cognitive-services/

Please note that the key has to be created for the Computer Vision API. The first "GET API key" button you encounter with single key navigation. Currently Microsoft provides the option to create a trial key for 7 days. You can also sign up for a free azure account for more trail. Signing up requires a credit card. If you already have a subscription account you can skip this step.

Step 2: Deploy Cognitive Services
Now you have an azure account. 
First login on  [Azure Portal](https://portal.azure.com)
Wait until you get the message Portal is Ready you are logged into azure portal.
Find the link called All resources after All services
button and activate it.
Wait until you get the message Blade All resources is ready , your focus will be an editbox,then press shift+tab find a menu item called add and activate it.

Wait until you get the message Search the Marketplace,
Type Cognitive Services and press down arrow.
Wait until you get the message List of options Cognitive Services one of five, then press enter.
Wait until you get the message Blade Cognitive Services is ready press tab or b to find a button named Create activate it.
Wait until you get the message Blade Create is ready, your focus will be an editbox, type a name for this resource. Note that Your resource name can only include alphanumeric characters, ‘_,-’, and can’t end with ’_’ or ’-‘.
I choose NVDAOCR.
Press tab to go to Subscription combobox. Usually you can leave it as is.
Press tab to go to Location combobox. Choose one close to your current location. Be sure to remember this since location is required in engine configuration.
Press tab to go to Pricing tie combobox. Usually a free tie like F0 is adequate.If that is not enough you can choose other tier after reading full pricing details in View full pricing details link.
Press tab to go to Create new Resource group  editbox. You should create one if you do not have any Resource group.Press tab  find Create new button. 
Then press tab go to Create Button to create this rescource.
Wait until you get the message Deployment succeeded.
Then find Go to resource button sometimes you need go up to activate Notifications button before you can find Go to resource button.
Wait until you get the message Blade Quick Start is busy.
Find the link named keys, then activate it.
Wait until you get the message Blade Manage keys is ready.
Find edit box named key 1 or key 2. The content of that edit box is the API key required in engine configuration.Press Ctrl-C to copy it for engine configuration
Then you can fill in these two settings required if you use your own API key.
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

## Update Log

### 0.8

Add friendly notice if recognition result is empty.
Fix another place do not work well with non ascii config path

### 0.6
Added proxy settings for people with access of Internet behind a specific proxy.
Added serveral general options.
Fix unicode decode error due to sending unicode url to urllib3.

### 0.5
Fix unicode error if OCR engine upload image file directly instead of base64 encode.
Change gesture of recognizing clipboard to Control+Shift+NVDA+R 
since NVDA+shift+r is used in Word and Excel to define row headers in tables, or to delete the definitions when pressed twice.

### 0.4

Fix installation error when config path contains non-ascii characters
Change gesture to avoid collison with golden cursor.
Change default engine to Microsoft azure because it is able to detect text language automatically.

### 0.3 
Add detail documentation on how to get API key of Microsoft Azure OCR
Fix issue about new installation.
Removed auto OCR since this feature is problematic and may confuse with online engines. Auto OCR will be a seperate addon, when it is stable enough.