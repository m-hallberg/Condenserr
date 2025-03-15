FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TMDB_API_KEY=5c9f355d2a63541c00570f1a15c255df
ENV TVDB_API_KEY=22892b01-6f6b-421f-b060-ac140e24427a
ENV WEBHOOK_URL=https://discord.com/api/webhooks/1348717842274713712/rwJChGuCynxe_3pSHvRcdF4jS1_IpZfIfMND1p67W2fmxH2FzZYkF_kZNjZDluCgu23M

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]