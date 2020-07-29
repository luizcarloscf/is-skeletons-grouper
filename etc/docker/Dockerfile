FROM ubuntu:16.04 as build

WORKDIR /tmp/
ADD bootstrap.sh .
RUN bash bootstrap.sh  \
  && rm -f bootstrap.sh 

RUN pip3 uninstall --yes conan \
 && pip3 uninstall --yes conan_package_tools \
 && rm -rf /root/.conan \
 && pip3 install conan \
 && pip3 install conan_package_tools \
 && conan remote add bincrafters https://api.bintray.com/conan/bincrafters/public-conan \
 && conan remote add is https://api.bintray.com/conan/labviros/is  

ENV CONAN_USERNAME is
ENV CONAN_LOGIN_USERNAME is
ENV CONAN_CHANNEL stable

# build caffe and openpose packages
ADD etc/packages/ /tmp/packages/
RUN cd /tmp/packages/armadillo/   \
  && python3 build.py             \
  && cd /tmp/                     \
  && rm -rf packages

ADD conanfile.py .
RUN conan install . -s compiler.libcxx=libstdc++11 --build=missing

ADD . /project
RUN cd /project                                                  \
 && ./build.sh                                                   \
 && mkdir -v -p /tmp/deploy                                      \
 && libs=`find build/ -type f -name '*.bin' -exec ldd {} \;      \
    | cut -d '(' -f 1 | cut -d '>' -f 2 | sort | uniq`           \
 && for lib in $libs; do                                         \
      cp --verbose --parents $lib /tmp/deploy;                   \
      libdir=`dirname $lib`;                                     \
    done                                                         \
 && cp --verbose `find build/ -type f -name '*.bin'` /tmp/deploy \
 && cp --verbose etc/conf/options.json /tmp/deploy               \
 && sudo rm -rf build/

# Deployment container
FROM ubuntu:16.04
WORKDIR /opt/is
COPY --from=build /tmp/deploy /
COPY --from=build /project/etc/conf/options.json /opt/is
RUN mv /service.bin /opt/is
RUN mv /rpc.bin /opt/is