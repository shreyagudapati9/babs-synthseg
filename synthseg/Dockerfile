
# Base Image
FROM freesurfer/freesurfer:7.4.1


COPY run_synthseg.py /run_synthseg.py
RUN chmod +x /run_synthseg.py
ENTRYPOINT ["/usr/local/freesurfer/python/bin/python3", "/run_synthseg.py"]
