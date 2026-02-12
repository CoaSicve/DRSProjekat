FROM python:3.9

WORKDIR /app

RUN pip install flask 
RUN pip install flask-cors
RUN pip install flask-jwt-extended
RUN pip install flask_sqlalchemy
RUN pip install pydantic
RUN pip install Cors
RUN pip install werkzeug
RUN pip install gunicorn
RUN pip install pymysql
RUN pip install cryptography
RUN pip install python-dotenv
RUN pip install flask-socketio
RUN pip install Flask-SocketIO==5.3.7 eventlet==0.36.1

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "--timeout", "120", "app.main:app"]