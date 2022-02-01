@ECHO OFF
set archiPath=C:\Users\XY56RE\programs\Archi
set archiRepo=C:\Users\XY56RE\PycharmProjects
set model=C:\Users\XY56RE\PycharmProjects\p13596-architecture-model
set reportPath=C:\Users\XY56RE\exported\
set script=archiScripts\Export to Markdown.ajs
set XMLpath=C:\Users\XY56RE\ING\BE Architecture CoE Application Landscape - General\ARIS-Archi exchange files
set CSVpath=C:\Users\XY56RE\PycharmProjects\p13596-architecture-model\CSV

cd %XMLpath%
setlocal enabledelayedexpansion
for %%f in (.\Esperanto*.xml) do (
    echo +%%~nf

    "%archiPath%\Archi.exe" -application com.archimatetool.commandline.app -consoleLog -nosplash ^
    --xmlexchange.import "%%f" --csv.export "%CSVpath%\%%~nf_"
)

for %%f in (.\Esperanto*.xml) do (
    echo +%%~nf
    "%archiPath%\Archi.exe" -application com.archimatetool.commandline.app -consoleLog -nosplash ^
    --loadModel "%model%\importAris.archimate" ^
    --csv.import "%CSVpath%\%%~nf_\elements.csv" ^
    --saveModel "%model%\importAris.archimate"
)
 rem --modelrepository.loadModel "%archiRepo%\%model%" --script.runScript "%archiRepo%\%script%"

