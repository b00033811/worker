FROM python:3.7-stretch AS build-env
WORKDIR /usr/src/app
COPY requirements.txt .
# add here nexus pip conf 
RUN pip install --upgrade pip
RUN pip install pystan
RUN pip install -r requirements.txt
COPY . .
RUN echo "Build Completed."
# Building Distroless Container
FROM gcr.io/distroless/python3-debian10:debug
COPY --from=build-env /usr/src/app /usr/src/app
COPY --from=build-env /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
COPY --from=build-env /usr/local/lib/libpython3.7m.so.1.0 /usr/local/lib/libpython3.7m.so.1.0
WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/local/lib/python3.7/site-packages
ENV LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib
CMD ["worker.py"]
