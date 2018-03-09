import os
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from time import time
import pickle
import cv2
import openface
import numpy as np

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

multiple = True
imgDim = 96
networkModel = '/root/openface/models/openface/nn4.small2.v1.t7'
dlibFacePredictor = '/root/openface/models/dlib/shape_predictor_68_face_landmarks.dat'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

align = openface.AlignDlib(dlibFacePredictor)
net = openface.TorchNeuralNet(networkModel, imgDim=imgDim, cuda=False)

with open('data/model/classifier.pkl', 'r') as f:
    le, clf = pickle.load(f)

def getRep(imgPath, multiple=False):
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        return []

    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    if multiple:
        bbs = align.getAllFaceBoundingBoxes(rgbImg)
    else:
        bb1 = align.getLargestFaceBoundingBox(rgbImg)
        bbs = [bb1]

    reps = []
    for bb in bbs:
        alignedFace = align.align(
            imgDim,
            rgbImg,
            bb,
            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        if alignedFace is None:
            raise Exception("Unable to align image: {}".format(imgPath))

        rep = net.forward(alignedFace)
        reps.append((bb.center(), rep))

    sreps = sorted(reps, key=lambda x: x[0])
    return sreps


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = '%d_%s' % (int(time() * 1000000), secure_filename(file.filename))
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
            file.save(file_path) 
 
            reps = getRep(file_path, multiple)

            result = {}
            result['file'] = file.filename
            result['faces'] = []

            for r in reps:
                rep = r[1].reshape(1, -1)
                bb = r[0]
                predictions = clf.predict_proba(rep).ravel()
                maxI = np.argmax(predictions)
                person = le.inverse_transform(maxI)
                confidence = predictions[maxI]

                r = {}
                r['x'] = bb.x
                r['y'] = bb.y
                r['person'] = person.decode('utf-8')
                r['confident'] = confidence

                result['faces'].append(r)

            # delete uploaded file 
            os.remove(file_path) 
 
            return jsonify(result)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''