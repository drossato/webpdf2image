from flask import Flask, render_template, request, Response, send_file
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import io
import pdf2image as p2i
import re
import os


popplerPath = r'poppler-0.68.0/bin'


app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      files = request.files.getlist('files')
      try:
         with tempfile.SpooledTemporaryFile() as tp:
            zipped = zipfile.ZipFile(tp, mode='w')
            p = re.compile('(.*)\.pdf')
            for f in files:
               converted = p2i.convert_from_bytes(f.stream.read(), poppler_path=popplerPath, size=(900, None))
               prefix = secure_filename(p.findall(f.filename)[0])

               for i in range(len(converted)):
                  buffer = io.BytesIO()
                  converted[i].save(buffer, format='JPEG')
                  zipped.writestr(prefix + '_page' + "{:02d}".format(i) + '.jpg', buffer.getvalue())

            # Reset the cursor back to beginning of the temp file
            tp.seek(0)
            bytes_zipped = tp.read()
            response = Response(bytes_zipped)
            response.headers['Content-Disposition'] = 'attachment; filename=imagens.zip'
            response.mimetype = 'application/zip'

         return response

      except:
         return render_template('error.html', mensagem='Erro! Arquivo ' + f.filename + ' não é um PDF válido.')


@app.route('/')
def upload():
    return render_template('upload.html', mensagem='  ')


if __name__ == '__main__':
   app.run(debug=True)
