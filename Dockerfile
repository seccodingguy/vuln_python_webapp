FROM alpine:3.13.8

# Update
RUN apk add --update python py-pip
RUN apk add tar

# Install app dependencies
RUN pip install Flask

RUN mkdir /app

# Bundle app source
COPY python_website.tar.gz python_website.tar.gz
RUN tar -xvf python_website.tar.gz -C /app
RUN rm python_website.tar.gz

EXPOSE  8000
CMD ["python", "/app/hello.py", "-p", "8000"]
