### Container to build dtn7-ng
FROM golang:1.22 AS dtn7-ng-builder

COPY dtn7-ng /dtn7-ng
WORKDIR /dtn7-ng
RUN go build -race -buildvcs=false -o /dtngod ./cmd/dtnd


### DTN7-rs
FROM maciresearch/core_worker:9.0.1 AS dtn7-rs-builder
RUN wget https://github.com/dtn7/dtn7-rs/releases/download/v0.21.0/dtn7-0.21.0-x86_64-unknown-linux-gnu.tar.gz \
    && tar xf dtn7-0.21.0-x86_64-unknown-linux-gnu.tar.gz \
    && mv dtn7-0.21.0/bin/dtnd /dtnrs \
    && mv dtn7-0.21.0/bin/dtnquery /dtnrsquery \
    && mv dtn7-0.21.0/bin/dtnrecv /dtnrsrecv \
    && mv dtn7-0.21.0/bin/dtnsend /dtnrssend \
    && mv dtn7-0.21.0/bin/dtntrigger /dtnrstrigger

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
    bwm-ng \
    sysstat \
    frr \
    && apt-get clean

RUN pip3 install dtnclient

ENV PATH=/opt/core/venv/bin/:$PATH

RUN echo 'custom_services_dir = /root/.coregui/custom_services' >> /etc/core/core.conf
COPY dotcore/mobility /root/mobility


# Install the software
# DTN7
COPY --from=dtn7-ng-builder /dtngod                          /usr/local/sbin/
# DTN7-RS
COPY --from=dtn7-rs-builder /dtnrs                              /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrsquery                         /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrsrecv                          /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrssend                          /usr/local/sbin/
COPY --from=dtn7-rs-builder /dtnrstrigger                       /usr/local/sbin/
