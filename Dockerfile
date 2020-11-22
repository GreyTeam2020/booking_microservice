FROM python:3.7.0-stretch
LABEL mantainer="Francesco Fattori f.fattori4@studenti.unipi.it"
ADD ./ /code
WORKDIR code
ENV FLASK_APP=app.py
RUN pip install -r requirements.txt
EXPOSE 5002
CMD ["python", "app.py"]