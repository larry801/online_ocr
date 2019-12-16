# Online image describer addon #

* Author: Larry Wang
* NVDA compatibility: from 2018.3 to 2019.3
* Download [development version][2]

This addon aims at adding online image recognition engines to NVDA.
There are two types of engines. OCR and image describer.
OCR extract text from image.
Image describer describe visual features in image in text form.
Such as general description, color type landmarks and so on.
Internet connection is required to use this addon, since image describe services are provided by API endpoints on the Internet.
They are called engines in this addon.
There are three types of engine for this addon.

* Online OCR engine
* Online image describer engine
* Windows 10 OCR engine (offline)

You also need to choose the source of recognition image.

* Current navigator object
* Current foreground window
* The whole screen
* Image data or file from clipboard
* Image file pathname or image url from clipboard

### Keyboard commands

After choosing these types, you can start recognition with one gesture. 
NVDA+Alt+P  Perform recognize according to source and engine type setting, Then read result. If pressed twice, open a virtual result document.

There are four additional gestures left unassigned. Please assign them before using.
Cycle through different recognition engine types.
cycle through different recognition source types.
Cancel current recognition
This gesture can be useful if you think you have waited for too long and want to cancel.
Also sometimes you do not want to be disturbed by recognition message because you need to review some messages arrived after recognition start.

Show previous result in a virtual result document.
Though there is a feature to copy result to clipboard. Character position information cannot be preserved, so this gesture is added to solve this problem.


There are also four old gestures are left unassigned for users who prefer gestures in previous versions. 
It is recommended to use new gesture and switch engine type according to your need.

Recognize current navigator object with online OCR engine Then read result. If pressed twice, open a virtual result document.

Recognizes image in clipboard with online OCR engine. Then read result. If pressed twice, open a virtual result document.

Recognize current navigator object Then read result. If pressed twice, open a virtual result document.

Recognizes image in clipboard . Then read result. If pressed twice, open a virtual result document.


## Engine Configuration

You can choose recognition engines and configure them in detail in *Online Image Describer* category in NVDA settings dialog.

The author of addon have registered account with free API quota and set up a proxy server on www.nvdacn.com to make this addon easier to test at first. Test quota is limited and may be cancelled by API provider anytime.
It is highly recommended to register your own key according to guide in each engine.

The following settings are applicable to all engines.

* Copy recognition result to the clipboard:
If enabled, recognition result text will be copied to clipboard after recognition.

* Use browseable message for text result
If enabled, recognition result text will be shown in a popup window instead of speech or braille message. 

* Swap the effect of repeated gesture with none repeated ones:
By default, a virtual result document is shown only if you press the corresponding gesture twice, if you use that frequently you can enable this option so that you only need to press once to get a result viewer.

* Enable more verbose logging for debug purposes:
Some logs are essential for debugging but affects performance and takes up a lot of space. Only turn this on if specifically instructed to by the addon author or an NVDA developer.

* Proxy type:
Which type of proxy you are using. If you do not know what a proxy is just leave it as is.

* Proxy address:
Full URL of your proxy. If you do not know what a proxy is just leave it as is.
If you choose to use proxy your proxy will be verified before saving , after verification, there will be a prompt to tell you result.
The following settings means the same in all engines, describe them here to save space.

* API Access Type:
This controls how you get access to the corresponding API endpoints.
If you choose "Use public quota", you are using free quota in an account registered by addon author.
If you choose "Use your own API key", this addon will use quota from your own account.

* APP ID, API key or API Secret Key:
If you want to use quota from your own account corresponding access tokens is required. Some engines only need API key.
Some engines require two tokens.
These are only valid if you choose "use your own API key" in API Access type.
 

Note that the quality and accuracy of results are affected by many factors.

* Models and techniques used by engine provider
* Quality of uploaded image
* Is navigator object hidden behind something else
* Screen resolution
 

## Online image description

Here are three engines available.

### Machine Learning Engine by Oliver Edholm

It's a free engine gives description of an image.
If there is text inside it will do OCR on the image.
There are two settings for this engine.

* Access Types
The author of this addon has setup a proxy on www.nvdacn.com for users who cannot access google service access.
If you want to use this proxy please chose Use proxy on www.nvdacn.com in access type settings.
If you want to use your own key in the following two Microsoft engines. Please follow the guide in Microsoft Azure OCR section.

* Language of result:
English by default. If you configure another language than English, the description could have translation issues because it's automatically generated by machine translation service.

Security:
* The images are sent to a script hosted on the Google Cloud Platform for analysis. After the analysis the image gets removed from the server and will never be seen again.

### Microsoft Azure Image Analyser

This engine extracts a rich set of visual features based on the image content. 
This engine is english only. If you want description in other languages, you can use Microsoft Azure Image Describer

Visual Features include:
Adult - detects if the image is pornographic in nature (depicts nudity or a sex act). Sexually suggestive content is also detected.
Brands - detects various brands within an image, including the approximate location. The Brands argument is only available in English.
Categories - categorizes image content according to a taxonomy defined in documentation.
Color - determines the accent color, dominant color, and whether an image is black&white.
Description - describes the image content with a complete sentence in supported languages.
Faces - detects if faces are present. If present, generate coordinates, gender and age.
ImageType - detects if image is clip art or a line drawing.
Objects - detects various objects within an image, including the approximate location. The Objects argument is only available in English.
Tags - tags the image with a detailed list of words related to the image content.

Some features also provide additional details:

Celebrities - identifies celebrities if detected in the image.
Landmarks - identifies landmarks if detected in the image.

### Microsoft Azure Image describer

This engine generates a description of an image in human readable language with complete sentences. The description is based on a collection of content tags, which are also returned by the operation. More than one description can be generated for each image. Descriptions are ordered by their confidence score.
There are two settings for this engine.

* Language
The language in which the service will return a description of the image. English by default.

* Maximum Candidates
Maximum number of candidate descriptions to be returned. The default is 1.

## Online OCR

Online engines rely on the use and presence of the following services.

https://www.nvdacn.com

https://ocr.space/ocrapi

https://azure.microsoft.com/en-us/services/cognitive-services/

http://ai.qq.com

http://ai.baidu.com

http://ai.sogou.com/

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
Chinese Simplified
Chinese Traditional
Czech
Danish
Dutch
English
Finnish
French
German
Greek
Hungarian
Italian
Japanese
Korean
Norwegian
Polish
Portuguese
Russian
Spanish
Swedish
Turkish
Arabic
Romanian
Serbian Cyrillic
Serbian Latin
Slovak

Here are settings for this engine:

Language: Text language for recognition. Auto detection by default.

Detect image orientation:
If set to true, the API autorotates the image correctly.

If you use your own key, you should get a subscription key for using Microsoft Computer Vision API from the link below:
Step 1: Create an account.

https://azure.microsoft.com/en-ua/try/cognitive-services/

Please note that the key must be created for the Computer Vision API. The first "GET API key" button you encounter with single key navigation. Currently Microsoft provides the option to create a trial key for 7 days. You can also sign up for a free azure account for more trail. Signing up requires a credit card. If you already have a subscription account, you can skip this step.

Step 2: Deploy Cognitive Services
Now you have an azure account. 
First login on  [Azure Portal](https://portal.azure.com)
Wait until you get the message Portal is Ready you are logged into azure portal.
Find the link called All resources after All services
button and activate it.
Wait until you get the message Blade All resources are ready , your focus will be an edit box, then press shift tab find a menu item called add and activate it.

Wait until you get the message Search the Marketplace,
Type Cognitive Services and press down arrow.
Wait until you get the message List of options Cognitive Services one of five, then press enter.
Wait until you get the message Blade Cognitive Services is ready press tab or b to find a button named Create activate it.
Wait until you get the message Blade Create is ready, your focus will be an edit box, type a name for this resource. Note that Your resource name can only include alphanumeric characters, ‘_,-’, and can’t end with ’_’ or ’-‘.
I choose NVDAOCR.
Press tab to go to Subscription combo box. Usually you can leave it as is.
Press tab to go to Location combo box. Choose one close to your current location. Be sure to remember this since location is required in engine configuration.
Press tab to go to Pricing tie combo box. Usually a free tie like F0 is adequate. If that is not enough you can choose other tier after reading full pricing details in View full pricing details link.
Press tab to go to Create new Resource group  edit box. You should create one if you do not have any Resource group. Press tab  find Create new button. 
Then press tab go to Create Button to create this resource.
Wait until you get the message Deployment succeeded.
Then find Go to resource button sometimes you need go up to activate Notifications button before you can find Go to resource button.
Wait until you get the message Blade Quick Start is busy.
Find the link named keys, then activate it.
Wait until you get the message Blade Manage keys is ready.
Find edit box named key 1 or key 2. The content of that edit box is the API key required in engine configuration. Press Ctrl-C to copy it for engine configuration
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

If you press the gesture which only read result, you are using endpoints without any information about text location. 
If you press the gesture which shows an result viewer, you are using endpoints with information about text location. 

Though it provides a quite generous free quota, its website is Chinese only and not quite accessible.

## Change Log

### 0.18

Compatible with python3
Introduce the concept of recognition source type and engine type to reduce gesture usage.
Add a new unassigned gesture to cycle through different recognition source types.
Add a new unassigned gesture to cycle through different recognition engine types.
Add a new gesture to recognize according to image source and engine type setting.
Add a new unassigned gesture to show previous result in a virtual result document.

### 0.17

Fixed following issues:
Jump directly to panel when switch to onlineImageDescriber in settings dialog
Fix wrong description in azure analyzer

### 0.16

Add a cancel recognition gesture

Fixed following issues:
CheckListBox state change not announced
Swap the effect of repeated gesture not working in online image describer


### 0.15

Add an option to pop up a window containing message instead of speech or braille message for text results
Change checkboxes for visual features in Microsoft Azure Image Analyzer into a CheckBoxList.

Fix following issues:
Cannot load jpg image file from clipboard
Result document object do not show up after recognition.
Position in result document objects are not reliable if image is resized internally.
Result from Microsoft Azure Image Describer is in the same line which makes it hard to navigate around. 

### 0.14

Fixed some bugs:
Cannot use your own API key in Microsoft Azure engines
Cannot get text result if there is a braille display

### 0.13
Make sure that the add-on works when reloading the plug-ins without
restart (NVDA+Control+F3)

### 0.12
Fixed browse mode message of Microsoft Azure Image Describer
The accent color is now represented as NVDA colour descriptions.
Improved result format of Microsoft Azure Image Analyser
Improve document according to review comments
Fixed gesture inconsistency.
Control+Shift+NVDA for clipboard while NVDA+ALT for navigator object
Fix missing imageInfo error while recognizing.
 
### 0.11
Added image description capability
Change addon summary to online image describer

### 0.10
Fix error using user's own API key in sougou API.
Fix unknown panel issue by adding settings to supportedSettings

### 0.9

Fix double press gesture no effect issue.
Revised document to reflect changes in code.
Clarified what kind of clipboard image is supported and how to copy image for recognition. 

Fixed the clipboard recognition cannot open result viewer issue.
Added support to recognize copied local image file path in clipboard.


### 0.8

Added friendly notice if recognition result is empty.
Fixed another place do not work well with non ascii config path

### 0.6
Added proxy settings for people with access of Internet behind a specific proxy.
Added several general options.
Fix Unicode decode error due to sending Unicode URL to urllib3.

### 0.5
Fix Unicode error if OCR engine upload image file directly instead of base64 encode.
Change gesture of recognizing clipboard to Control+Shift+NVDA+R 
since NVDA+Shift+R is used in Word and Excel to define row headers in tables, or to delete the definitions when pressed twice.

### 0.4

Fix installation error when config path contains non-ascii characters
Change gesture to avoid collision with golden cursor.
Change default engine to Microsoft azure because it can detect text language automatically.

### 0.3 
Add detail documentation on how to get API key of Microsoft Azure OCR
Fix issue about new installation.
Removed auto OCR since this feature is problematic and may confuse with online engines. Auto OCR will be a separate addon, when it is stable enough.


[[!tag dev]]

[2]: https://addons.nvda-project.org/files/get.php?file=oid-dev
