FROM python:3.12.3-slim
WORKDIR /root
COPY . .
RUN mkdir -p /root/.config/gpterminator
RUN ls
RUN pip install . 
ARG APIKEY
ENV OPENAI_API_KEY=$APIKEY
CMD ["gpterm"]