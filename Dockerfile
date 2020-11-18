FROM python:3.7.0-stretch
LABEL mantainer="Francesco Fattori f.fattori4@studenti.unipi.it"
ADD ./ /code
WORKDIR code
ENV FLASK_APP=app.py
#ENV PATH .:$PATH
#RUN virtualenv venv
RUN pip install -r requirements.txt
#RUN python setup.py develop
EXPOSE 5002
CMD ["python", "app.py"]
#CMD ["flask", "run"]
#CMD ["bash", "build_and_run.sh"]