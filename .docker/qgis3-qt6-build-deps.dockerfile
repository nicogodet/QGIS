FROM fedora:34 as single
MAINTAINER Matthias Kuhn <matthias@opengis.ch>

#SHELL ["/bin/bash", "-c"]

RUN cd /usr/src \
  && wget https://github.com/KDE/qca/archive/refs/tags/v2.3.3.zip \
  && unzip v2.3.3.zip \
  && cd qca-2.3.3 \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -DQT6=ON -GNinja \
  && ninja install

RUN cd /usr/src \
  && wget https://github.com/frankosterfeld/qtkeychain/archive/refs/heads/master.zip \
  && unzip master.zip \
  && cd qtkeychain-master \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_WITH_QT6=ON -GNinja \
  && ninja install

RUN cd /usr/src \
  && wget https://sourceforge.net/projects/qwt/files/qwt/6.2.0/qwt-6.2.0.zip/download \
  && unzip download \
  && cd qwt-6.2.0 \
  && qmake6 qwt.pro \
  && make -j4 \
  && make install
