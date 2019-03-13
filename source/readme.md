# Online OCR addon #

This addon aims at enhancing the experience of OCR when using NVDA.

Add more accurate online engines to NVDA.
Add "Auto OCR" feature. Whenever navigator object changes, NVDA will automatically run OCR on current navigator object with Windows 10 OCR engine.

The author of addon have registered account with free API quota and put them on www.nvdacn.com  to make this addon easier to use.Registering your own key is highly recommended.

Online engines relies on the use and presence of the following services.

https://www.nvdacn.com

https://ocr.space/ocrapi

http://ai.qq.com

http://ai.baidu.com

http://ai.sogou.com/

## Hotkeys

NVDA+Shift+R Recognize current navigator object  with online OCR engine and read results directly
NVDA+ALT+Shift+R Recognize current navigator object with online OCR engine and open a result viewer like Windows 10 OCR
NVDA+Windows+R Recognizes the text in clipboard images with Custom OCR engine and read results directly
NVDA+Alt+Windows+R Recognizes image in clipboard with online OCR engine.Then open a result viewer like Windows 10 OCR

Ctrl+semicolon Enable or disable "Auto OCR".

## Configuration

You can choose recognition engines and configure them in detail in *Online OCR* categroy in NVDA settings dialog.

The following two settings are applicable to all engines.

API Access Type: How you get access to the corresponding API endpoints.
If you choose Use public quota, you are using free quota in an account registered by addon author.
If you choose Use your own api key,this addon will use your own api access tokens.
There are four engines avaliable.

API key or API Secret Key:
These are only valid if you choose "use your own api key" in API Access type.

### OCR space
This one is a paid API with free quota provided by ocr.space
Support 24 languages and table recognition.
Here are its settings:
Detect image orientation
If set to true, the api autorotates the image correctly.
Scale image for better quality
If set to true, the api does some internal upscaling. This can improve the OCR result significantly, especially for low-resolution PDF scans.
Optimize for table recognition 
If set to true, the OCR logic makes sure that the parsed text result is always returned line by line. This switch is recommended for table OCR, receipt OCR, invoice processing and all other type of input documents that have a table like structure.

You can get your own free api key by registering on
https://ocr.space/ocrapi
Find the link "Register for free API key"
Click on it and you will find a form to fill in.
The form asks you to enter the following data
Email Address 
First Name
Last Name
How do you plan to use the OCR API?
After filling it and submit. You may also need to pass reCAPTCHA
Then you will receive a confirmation e-mail
Click the button "Yes, subscribe me to this list." and you will receive API key by e-mail.

### Baidu OCR
This one is also a paid API with free quota provided by Baidu.
Baidu OCR supports 10 languages and can get position of every character

Here are its settings:

Detect image direction is suitable for scanned pages.
Get position of every character allows you to do more precise operation on some inaccessible application. Enabling this will make recognition slightly slower.

Use Accurate API takes longer time but has higher quality and also higher price.

It has four endpoints with seperate quota limit.

Basic OCR without any information about text location.
Currently 50000 times a day.
Basic OCR with information about text location.
Currently 500 times a day.
Accurate OCR without any information about text location.
Currently 500 times a day.
Accurate with information about text location.
Currently 50 times a day.

If you checked the high accurate api checkbox you are using accurate API.
If you presses NVDA+Shift+R or NVDA+Windows+R, you are using endpoints without any information about text location. 

Though it provides a quite gengerous free quota, its website is Chinese only and not quite accessible.

### Sougou OCR and Tencent AI OCR
These two API are free to use with frequency limit.
If you want to by pass the limit you can register your own api key.The website  of these two APIs are also Chinese only and not quite accessible.
There is no information about language support in these api document
According to my test Chinese and English and their mixture is surpported.
There are no additional configuration for these API.
