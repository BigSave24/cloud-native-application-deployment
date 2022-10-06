FROM python:3.8
LABEL platform_engineer="Kevin Edmond"

COPY ./techtrends /app
WORKDIR /app
RUN pip install -r requirments.txt
RUN python init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]