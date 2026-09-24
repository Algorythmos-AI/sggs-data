# The rebuild toolchain, pinned: one definition of "the interpreter that builds the dataset".
# Base image pinned by digest; Python libraries by version (pipeline/requirements-toolchain.txt);
# gh pinned by version and checksum (it restores the private backups). Build context: repo root.
#
#   docker build -t sggs-toolchain -f toolchain/Dockerfile .
#   docker run --rm -v "$PWD:/repo" -w /repo sggs-toolchain bash pipeline/rebuild_all.sh <pdf>
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e

ARG GH_VERSION=2.101.0
ARG GH_SHA256=9bca2d1c16825f109907a23307628a2f0698fbf99662b73a5cf0b020293072b8

# git + git-lfs (fresh clones), perl (shasum, used by every verification script), curl + CA roots.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git git-lfs perl curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/gh.tgz "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
 && echo "${GH_SHA256}  /tmp/gh.tgz" | sha256sum -c - \
 && tar -xzf /tmp/gh.tgz -C /tmp \
 && install -m 0755 "/tmp/gh_${GH_VERSION}_linux_amd64/bin/gh" /usr/local/bin/gh \
 && rm -rf /tmp/gh.tgz "/tmp/gh_${GH_VERSION}_linux_amd64"

COPY pipeline/requirements-toolchain.txt /tmp/requirements-toolchain.txt
RUN pip install --no-cache-dir -r /tmp/requirements-toolchain.txt \
 && python -c "import fitz, numpy, scipy, sqlite3; print('toolchain:', fitz.VersionBind, 'numpy', numpy.__version__, 'scipy', scipy.__version__, 'sqlite', sqlite3.sqlite_version)"

# Checkouts mounted from the host are owned by another uid.
RUN git config --system --add safe.directory '*'
WORKDIR /repo
