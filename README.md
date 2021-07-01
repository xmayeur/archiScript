# jArchi scripts

## Introduction
This repo contains various scripts to use with the Archimate tool

# Installation
- download and extract the [script plugin](jarchiPlugIn/com.archimatetool.script_1.1.0.202101121529.archiplugin) with the `.archiplugin` extension from the jarchiPlugIn GIT folder
- from Archimate tool, go to the `Manage Plug-ins` menu under the `Help` one and install the downloaded plugin.
   Refer to [jArchi wiki](https://github.com/archimatetool/archi-scripting-plugin/wiki) for more information.
- copy all `.ajs` scripts, including the `lib` folder to any location of your desktop
-  In Archimate tool Preferences / Scripting, update the Script folder field to that location  
 
# Scripts

## Export to Markdown

### From Archimate tool
- select a view in Archimate
- execute the `exportToMarkdown` script
- a `md` sub-folder under the path of the archimate model file is created
- a `.md` document with the name of the model and the view is created
- a `.png` file in the subfoler `.image` also contains the archimate drawing of the view
- the script will then execute `toConfluence.exe` tool, if properly installed and callable from user path (else you need to change the `exportCmd` variable in the `Export to Markdown.ajs` script to define the exact pathname)

### toConfluence image and usage information 
- Download [toConfluence](https://artprodsu6weu.artifacts.visualstudio.com/Affcba4f3-9df1-4f1d-81bd-1c100139ef08/f55d8f82-468c-48a4-8e4b-6a4e99d3e101/_apis/artifact/cGlwZWxpbmVhcnRpZmFjdDovL1hhdmllck1heWV1ci9wcm9qZWN0SWQvZjU1ZDhmODItNDY4Yy00OGE0LThlNGItNmE0ZTk5ZDNlMTAxL2J1aWxkSWQvMTMvYXJ0aWZhY3ROYW1lL3RvY29uZmx1ZW5jZQ2/content?format=file&subPath=%2Ftoconfluence.exe)
- Also see [toConfluence usage](https://dev.azure.com/XavierMayeur/toConfluence/_git/toConfluence?path=%2FREADME.md&version=GBmaster)

