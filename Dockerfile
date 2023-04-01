FROM amazon/aws-lambda-python:3.9

ARG chromedriver_version="112.0.5615.28"
# https://vikyd.github.io/download-chromium-history-version/#/
ARG chrome_version='112.0.5606.1'
ARG chrome_position='1107251'

# chrome dependencies
RUN yum install xz atk cups-libs gtk3 libXcomposite alsa-lib tar \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel unzip bzip2 -y -q

# install chrome
RUN mkdir -p "/opt/chrome/$chrome_version"
RUN curl -Lo "/opt/chrome/$chrome_version/chrome-linux.zip" "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F${chrome_position}%2Fchrome-linux.zip?alt=media"
RUN unzip -q "/opt/chrome/$chrome_version/chrome-linux.zip" -d "/opt/chrome/$chrome_version/"
RUN mv /opt/chrome/$chrome_version/chrome-linux/* /usr/bin/

# install chromedriver
RUN mkdir -p "/opt/chromedriver/$chromedriver_version"
RUN curl -Lo "/opt/chromedriver/$chromedriver_version/chromedriver_linux64.zip" "https://chromedriver.storage.googleapis.com/$chromedriver_version/chromedriver_linux64.zip"
RUN unzip -q "/opt/chromedriver/$chromedriver_version/chromedriver_linux64.zip" -d "/usr/bin/"

RUN yum install git
RUN pip install --user --upgrade pip
RUN pip install pipenv
COPY Pipfile .
RUN pipenv lock --clear
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt
COPY src/ ${LAMBDA_TASK_ROOT}/src
