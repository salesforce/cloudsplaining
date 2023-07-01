FROM --platform=linux/amd64 alpine:3.17.2

COPY . ./app

WORKDIR /app
### install prerequesites

RUN apk add --update --no-cache python3==3.10.11-r0 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools==67.6.0
RUN apk add nodejs==18.16.0-r0
RUN apk add npm==9.1.2-r0
RUN apk add make==4.3-r1
###### install requirements.txt
RUN python3 -m pip install -r requirements.txt
### remove unnecassary
RUN rm -rf dist/
RUN	rm -rf build/
RUN	rm -rf *.egg-info
RUN	find . -name '*.pyc' -delete
RUN	find . -name '*.pyo' -delete
RUN	find . -name '*.egg-link' -delete
RUN	find . -name '*.pyc' -exec rm --force {} +
RUN	find . -name '*.pyo' -exec rm --force {} +
#### seorate requirements
RUN python3 -m pip install --upgrade setuptools==67.6.0 wheel==0.40.0
RUN	python3 -m setup -q sdist bdist_wheel
RUN python3 -m pip install -q ./dist/cloudsplaining*.tar.gz
######## NPM installation
RUN npm install

ENTRYPOINT ["cloudsplaining"]