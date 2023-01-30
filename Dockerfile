### Container to build dtn7-go
FROM golang:1.19 AS dtn7-go-builder

COPY dtn7-go /dtn7-go
WORKDIR /dtn7-go
RUN go build -race -buildvcs=false -o /dtngod ./cmd/dtnd


### Build serval
FROM maciresearch/core_worker:9.0.1 AS serval-builder

RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
    build-essential \
    autoconf \
    automake \
    libtool \
    grep \
    sed \
    gawk \
    jq \
    curl \
    git \
    libsodium-dev \
    gcc-9 \
    && apt-get clean

ADD serval-dna /serval-dna
WORKDIR /serval-dna
RUN autoreconf -f -i -I m4
# ENV CFLAGS -Wno-error=deprecated-declarations -O1
ENV CC gcc-9
RUN ./configure
RUN make -j $(nproc) servald


## Build ibrdtn
FROM maciresearch/core_worker:0.4.2 AS ibrdtn-builder

# Install depencencies according to https://github.com/ibrdtn/ibrdtn/wiki/Build-IBR-DTN
# install common dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
    build-essential \
    devscripts \
    automake \
    autoconf \
    pkg-config \
    libtool \
    debhelper \
    cdbs \
    git \
    subversion \
    wget \
    curl \
    gawk \
    libncurses5-dev


# install library packages
RUN apt-get install --no-install-recommends -yq \
    libssl-dev \
    libz-dev \
    libsqlite3-dev \
    libcurl4-openssl-dev \
    libdaemon-dev \
    libcppunit-dev \
    libnl-3-dev \
    libnl-cli-3-dev \
    libnl-genl-3-dev \
    libnl-nf-3-dev \
    libnl-route-3-dev \
    libarchive-dev

ENV CXXFLAGS -Wno-deprecated

ADD ibrdtn /ibrdtn
WORKDIR /ibrdtn/ibrdtn
RUN bash autogen.sh
RUN ./configure
RUN make -j $(nproc)
RUN make install


### DTN7-rs
FROM maciresearch/core_worker:9.0.1 AS dtn7-rs-builder
RUN wget https://github.com/dtn7/dtn7-rs/releases/download/v0.18.2/dtn7-0.18.2-x86_64-unknown-linux-gnu.tar.gz \
    && tar xf dtn7-0.18.2-x86_64-unknown-linux-gnu.tar.gz \
    && mv dtn7-0.18.2/bin/dtnd /dtnrs \
    && mv dtn7-0.18.2/bin/dtnquery /dtnrsquery \
    && mv dtn7-0.18.2/bin/dtnrecv /dtnrsrecv \
    && mv dtn7-0.18.2/bin/dtnsend /dtnrssend \
    && mv dtn7-0.18.2/bin/dtntrigger /dtnrstrigger

### CORE Container
FROM maciresearch/core_worker:9.0.1

RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
    libtk-img \
    lxterminal \
    tmux \
    wireshark \
    libdaemon-dev \
    python2 \
    && apt-get clean

RUN pip3 install dtnclient

ENV PATH=/opt/core/venv/bin/:$PATH

RUN echo 'custom_services_dir = /root/.coregui/custom_services' >> /etc/core/core.conf

# Force Serval to use its instance_path
ENV BASH_ENV /root/.serval
RUN echo 'export SERVALINSTANCE_PATH=$SESSION_DIR/`hostname`.conf' >> /root/.serval \
    && echo 'export SERVALINSTANCE_PATH=$SESSION_DIR/`hostname`.conf' >> /root/.bashrc


# Install the software
# DTN7
COPY --from=dtn7-go-builder    /dtngod                          /usr/local/sbin/
# DTN7-RS
COPY --from=dtn7-rs-builder /dtnrs                              /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrsquery                         /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrsrecv                          /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrssend                          /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrstrigger                       /usr/local/sbin/
# SERVAL
COPY --from=serval-builder  /serval-dna/servald                 /usr/local/sbin/
# IBR-DTN
COPY --from=ibrdtn-builder  /usr/local/bin/dtnsend              /usr/local/sbin/
COPY --from=ibrdtn-builder  /usr/local/sbin/dtnd                /usr/local/sbin/
COPY --from=ibrdtn-builder  /usr/local/lib/libibrdtn.so.1       /usr/lib/
COPY --from=ibrdtn-builder  /usr/local/lib/libibrcommon.so.1    /usr/lib/
# FORBAN
COPY                        forban                              /forban
COPY                        forban.diff                         /tmp/forban.diff
COPY                        forban_python.diff                  /tmp/forban_python.diff

# Patch Forban's announce interval and logging
RUN cd /forban && patch -p1 < /tmp/forban.diff
RUN cd /forban && patch -p1 < /tmp/forban_python.diff
