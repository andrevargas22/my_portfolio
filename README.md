# Personal Website

This repository contains the source code for my personal website.

Backend: Flask (Python)
Frontend: HTML, CSS and JavaScript

[https://andrevargas.com.br](https://andrevargas.com.br)


curl -X POST http://localhost:8080/websub/callback \
  -H "Content-Type: application/atom+xml" \
  -H "User-Agent: FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)" \
  -d @test_notification.xml \
  -v