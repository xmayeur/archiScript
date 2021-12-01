 set archiPath=C:\Users\XY56RE\programs\Archi
 set archiRepo=C:\Users\XY56RE\PycharmProjects
 set model=p00401-tracing-architecture
 set reportPath=C:\Users\XY56RE\exported\
 set script=archiScripts\Export to Markdown.ajs
 start "Archi" "%archiPath%\Archi.exe" -p -application com.archimatetool.commandline.app -consoleLog -nosplash --modelrepository.loadModel "%archiRepo%\%model%" --script.runScript "%archiRepo%\%script%"
 REM --jasper.createReport %reportPath% --jasper.filename report --jasper.format PDF --jasper.title TracING
