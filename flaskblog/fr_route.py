# import secrets
# import os
# from PIL import Image
# from flask import render_template, url_for, flash, redirect, request, Response
# from flaskblog import app, db, bcrypt
# from flaskblog.recognition import FaceRecognition, video_capture
# from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, FR_LoginForm
# from flaskblog.models import User, Post
# from flask_login import login_user, current_user, logout_user, login_required
# import cv2
# import math
# import numpy as np
# import face_recognition

# camera = cv2.VideoCapture(0)

# face_locations = []
# face_encodings = []
# face_names = []
# known_face_encodings = []
# known_face_names = []
# process_current_frame = True

# def encode_faces():
#         dir = 'flaskblog/static/fr_images/'
#         for image in os.listdir(dir):
#             face_image = face_recognition.load_image_file(dir + image)
#             face_encoding = face_recognition.face_encodings(face_image)[0]

#             if image not in known_face_names:
#                 known_face_encodings.append(face_encoding)
#                 known_face_names.append(image)

# def face_confidence(face_distance, face_match_threshold=0.6):
#     range = (1.0 - face_match_threshold)
#     linear_val = (1.0 - face_distance) / (range * 2.0)

#     if face_distance > face_match_threshold:
#         # return str(round(linear_val * 100, 2)) + '%'
#         return round(linear_val * 100, 2)
#     else:
#         value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
#         # return str(round(value, 2)) + '%'
#         return round(value, 2)

# def gen_frames():
#     while True:
#         success, frame = video_capture.read()
#         if not success:
#             break
#         else:
#             if process_current_frame:
#                 # Resize frame of video to 1/4 size for faster face recognition processing
#                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#                 # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
#                 rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

#                 # Find all the faces and face encodings in the current frame of video
#                 face_locations = face_recognition.face_locations(rgb_small_frame)
#                 face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

#                 face_names = []
#                 for face_encoding in face_encodings:
#                     # See if the face is a match for the known face(s)
#                     matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#                     name = "Unknown"
#                     confidence = '???'

#                     # Calculate the shortest distance to face
#                     face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

#                     best_match_index = np.argmin(face_distances)
#                     if matches[best_match_index]:
#                         name = known_face_names[best_match_index]
#                         confidence = face_confidence(face_distances[best_match_index])

#                     if name != 'Unknown' and confidence != '???':
#                         if confidence > 97:
#                             print(name, confidence)
#                             video_capture.release()
#                             cv2.destroyAllWindows()
#                             return name
#                     face_names.append(f'{name} ({confidence})')

#             process_current_frame = not process_current_frame

#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


    
# @app.route("/frlogin", methods=["GET", "POST"])
# def frlogin():
#     # if current_user.is_authenticated:
#     #     return redirect(url_for('home'))
#     # fr = FaceRecognition()
#     # name = fr.run_recognition()
#     # name = name.split('.')[0]
#     # print(name)
#     # if name:
#     #     user = User.query.filter_by(username=name).first()
#     #     if user:
#     #         login_user(user, remember=False)
#     #         next_page = request.args.get('next')
#     #         return redirect(next_page) if next_page else redirect(url_for('home'))
#     #     else:
#     #         print('User not found')
#     # return redirect(url_for('home'))
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
