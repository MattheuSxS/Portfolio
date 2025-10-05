FROM ubuntu:latest

LABEL maintainer="Matheus Dos S. Silva"
LABEL mail="mattheusxs@gmail.com"
LABEL description="This is a Docker image for Infrastructure as Code (IaC) tools."
LABEL version="2.0"
LABEL license="MIT"
LABEL name="mattheusxs/portfolio-iac"
LABEL imagetag="2.0.0 ~~> linux/arm64 | 1.0.0 ~~> linux/amd64"

ENV TERRAFORM_VERSION=1.13.3
ENV GOOGLE_CLOUD_SDK_VERSION=539.0.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    zip \
    unzip \
    curl \
    openssh-client \
    iputils-ping \
    git \
    python3.12 \
    python3-pip \
    python3-venv \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                          Download and Install Docker                                                  #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -f docker


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                          Download and Install Terraform                                               #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                          Download and install the GCP CLI                                             #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
RUN curl -sSL "https://dl.google.com/cloudsdk/channels/rapid/downloads/google-cloud-cli-${GOOGLE_CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" -o /tmp/google-cloud-cli.tar.gz && \
    mkdir -p /usr/local/gcloud && \
    tar -xzf /tmp/google-cloud-cli.tar.gz -C /usr/local/gcloud && \
    /usr/local/gcloud/google-cloud-sdk/install.sh \
    --usage-reporting=false \
    --quiet \
    --path-update=true && \
    rm -rf /tmp/google-cloud-cli.tar.gz


ENV PATH=$PATH:/usr/local/gcloud/google-cloud-sdk/bin

CMD ["/bin/bash"]