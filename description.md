
For configuration options:
 - [Comskip forum](http://www.kaashoek.com/comskip/)
 - [GitHub](https://github.com/erikkaashoek/Comskip)

---

<div style="background-color:#eee;border-radius:4px;border-left:solid 5px #ccc;padding:10px;">
<b>Note:</b>
<br>It is recommended to have this as the very last plugin in your <b>Worker - Processing file</b></b> flow.
</div>

This plugin will generate a comskip file and log in the same directory as the source file.

The name of the generated files will be the same as the video but with a file extension of **.txt**.

The plugin does not install the required comskip dependencies. Ensure you have done this prior to running.

For installation into the Unmanic Docker container, create a startup file:

`/config/startup.sh`
```
if ! command -v comskip &> /dev/null; then
    echo "**** Installing comskip ****"
    apt-get update
    apt-get install -y comskip
fi
```
