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

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]