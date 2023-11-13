
# Base Image
FROM freesurfer/freesurfer:7.4.1


COPY jobSubmitter.py /jobSubmitter.py
RUN chmod +x /jobSubmitter.py
ENTRYPOINT ["/usr/local/freesurfer/python/bin/python3", "/jobSubmitter.py"]
