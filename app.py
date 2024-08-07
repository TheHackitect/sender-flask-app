from dis import dis
from genericpath import isdir
import os,string,random
from flask import Flask, redirect, render_template, send_file, send_from_directory,request, abort,session
from pathlib import Path
import json
from werkzeug.utils import secure_filename

rootpath = os.path.split(os.getcwd())[0]
home = (Path.home())
path = Path(rootpath)



ext =  open("extensions.json","r")
exts = json.load(ext)

def get_icon(file_ext):
    if file_ext in exts:
        ico = exts[file_ext]
        if ico == "image":
            icon = "file-image"
        if ico == "audio":
            icon = "file-audio"
        if ico == "executable":
            icon = "cogs"
        if ico == "video":
            icon = "film"
        if ico == "text":
            icon = "file-alt"
        if ico == "spreadsheet":
            icon = "table"
        if ico == "presentation":
            icon = "file-chart-pile" 
        if ico == "database":
            icon = "database" 
        if ico == "system":
            icon = "cog" 
        if ico == "web":
            icon = "globe" 
    else:
        icon = "file-alt"
    return icon

def main():
    app = Flask(__name__)    
    @app.route('/open', methods=['POST','GET'])
    def open():
        if request.method == "POST":
            path = request.form.get("openpath")
            try:
                root_dir_content = os.listdir(Path(path))
            except:
                return render_template("landing.html", heading=f"'{path}' Is not a Directory")
            display =list()
            for dir in root_dir_content:
                file_ext = os.path.splitext(dir)[1]
                icon = get_icon(file_ext)
                size = os.stat(path).st_size/(1024*1024)
                if os.path.isdir(Path(f"{path}\\{dir}")) == True:
                    data = {
                        "type":"folder",
                        "name":dir,
                        "ico":"folder",
                        "path":Path(f"{path}\\{dir}"),
                        "size":size
                    }
                    display.append(data)
                elif os.path.isfile(Path(f"{path}\\{dir}")) == True:
                    data = {
                        "type":"file",
                        "name":dir,
                        "file_ext":f"{file_ext}",
                        "path":Path(f"{path}\\{dir}"),
                        "ico":icon,
                        "size":size
                    }
                    display.append(data)
                else:
                    pass
            return render_template("landing.html", display = display, heading = f"{path}")
        elif request.method == "GET":
            return render_template("landing.html", heading = "You didn't specify a path")
    

    @app.route('/upload', methods = ['GET', 'POST'])
    
    def uploadfile():
        if request.method == 'POST':
            f = request.files['files'] 
            path = request.form.get("uploadpath")
            app.config["UPLOAD_FOLDER"] = str(Path(path))
            try:
                f.save(os.path.join(app.config['UPLOAD_FOLDER'] ,secure_filename(f.filename)))
            except:
                return render_template("landing.html",heading="Its either a permission error or you never selected a file for upload!")
            return redirect("/")
        elif request.method == "GET":
            return render_template("landing.html", heading = "You didn't specify a path.. You should upload a file...")

    @app.route('/download', methods=['POST','GET'])
    def download():
        if request.method == "POST":
            path = request.form.get("downloadpath")
            try:
                return send_file(path,as_attachment=True)
            except:
                return render_template("landing.html",heading="An error occured")
        else:
            return "Method Not Allowed!"


    @app.route('/delete', methods=['POST','GET'])
    def delete():
        if request.method == "POST":
            path = request.form.get("deletepath")
            if isdir(path) == True:
                files = os.listdir(Path(path))
                if len(files) > 0:
                    for file in files:
                        os.remove(f"{path}/{file}")
                        continue
            else:
                pass
            try:
                os.rmdir(path)
            except:
                os.remove(path)
            return redirect("/")
        else:
            return render_template("landing.html",heading="This method is mot allowed here.")   
         

    @app.route('/', methods=['POST','GET'])
    # @app.route('/path/<path>', methods=['POST','GET'])
    def create_post():
        if request.method == "POST":
            return render_template("landing.html", heading = "And how on earth did you do That?")
        elif request.method == "GET":
            root_dir_content = os.listdir(Path.home())
            display =list()
            for dir in root_dir_content:
                file_ext = os.path.splitext(dir)[1]
                icon = get_icon(file_ext)
                path = f"{Path.home()}\\{dir}"
                size = os.stat(path).st_size/(1024*1024)
                if os.path.isfile(Path(f"{path}")) == True:
                    data = {
                        "type":"file",
                        "name":dir,
                        "file_ext":f"{file_ext}",
                        "path":path,
                        "ico":icon,
                        "size":size
                    }
                    display.append(data)
                elif os.path.isdir(Path(f"{path}")) == True:
                    data = {
                        "type":"folder",
                        "name":dir,
                        "ico":"folder",
                        "path":path,
                        "size":size
                    }
                    display.append(data)

                
                else:
                    pass
            return render_template("landing.html", display = display, heading = f"{Path.home()}")

    @app.errorhandler(404)
    def invalid_route(e):
        return render_template(
            "landing.html",
            headimg="Oops! The page you requested was not found on the server. Probably it was removed.",            
            )
    
    @app.errorhandler(500)
    def internal_server_error(e):
        reason = "internal_server_error"
        headimg = "Oops! The page you requested could not be loaded. This is not your Fault, we are looking into it."
        return render_template(
            "landing.html",
            headimg=headimg,

            )
    
    @app.route("/static/<path:path>")
    def static_dir(path): 
        return send_from_directory("static", path)
    app.run(threaded=True, host="0.0.0.0", port=8080,debug=True)


if __name__ == '__main__':
    main()

