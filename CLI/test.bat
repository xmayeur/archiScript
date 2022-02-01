 @ECHO OFF
set archiPath=C:\Users\XY56RE\programs\Archi
 set archiRepo=C:\Users\XY56RE\PycharmProjects
 set model=C:\Users\XY56RE\PycharmProjects\p13596-architecture-model
 set reportPath=C:\Users\XY56RE\exported\
 set script="archiScripts\Export to Markdown.ajs"
 set XMLpath="C:\Users\XY56RE\ING\BE Architecture CoE Application Landscape - General\ARIS-Archi exchange files"
 set CSVpath="C:\Users\XY56RE\PycharmProjects\p13596-architecture-model\CSV"

setlocal enabledelayedexpansion
 for %%f in (%XMLpath%\*.xml) do (

    echo %%f
    echo %%~nf
 )