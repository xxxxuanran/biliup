# Build webui
FROM node:lts as webui

COPY . /biliup

RUN set -eux; \
	\
	cd biliup; \
	npm install; \
	npm run build

# Download ffmpeg
FROM python:3.12-slim as ffmpeg
RUN set -eux; \
	\
	savedAptMark="$(apt-mark showmanual)"; \
	useApt=false; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
		wget \
		xz-utils \
	; \
	apt-mark auto '.*' > /dev/null; \
	\
	arch="$(dpkg --print-architecture)"; arch="${arch##*-}"; \
	url='https://github.com/yt-dlp/FFmpeg-Builds/releases/download/autobuild-2024-08-30-14-08/'; \
	case "$arch" in \
		'amd64') \
			url="${url}ffmpeg-n7.0.2-6-g7e69129d2f-linux64-gpl-7.0.tar.xz"; \
		;; \
		'arm64') \
			url="${url}ffmpeg-n7.0.2-6-g7e69129d2f-linuxarm64-gpl-7.0.tar.xz"; \
		;; \
		*) \
			useApt=true; \
		;; \
	esac; \
	\
	if [ "$useApt" = true ] ; then \
		apt-get install -y --no-install-recommends \
			ffmpeg \
		; \
	else \
		wget -O ffmpeg.tar.xz "$url" --progress=dot:giga; \
		tar -xJf ffmpeg.tar.xz -C /usr --strip-components=1; \
	fi;


# Deploy Biliup
FROM python:3.12-slim as biliup
ENV TZ=Asia/Shanghai
EXPOSE 19159/tcp
VOLUME /opt
LABEL org.opencontainers.image.source="https://github.com/biliup/biliup"

COPY . /biliup

RUN set -eux; \
	savedAptMark="$(apt-mark showmanual)"; \
	apt-get update; \
	apt-get install -y --no-install-recommends g++ locales; \
	localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8; \
	cd biliup && \
	pip3 install --no-cache-dir quickjs && \
	pip3 install -e . && \
	\
	# Clean up \
	apt-mark auto '.*' > /dev/null; \
	[ -z "$savedAptMark" ] || apt-mark manual $savedAptMark; \
	apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
	rm -rf \
		/tmp/* \
		/usr/share/doc/* \
		/var/cache/* \
		/var/lib/apt/lists/* \
		/var/tmp/* \
		/var/log/*

COPY --from=webui /biliup/biliup/web/public/ /biliup/biliup/web/public/
COPY --from=ffmpeg /usr/bin/ffmpeg /usr/bin/ffmpeg

ENV LANG en_US.UTF-8
WORKDIR /opt

ENTRYPOINT ["biliup"]
